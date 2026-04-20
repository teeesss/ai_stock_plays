"""
GIGACPO Pipeline Orchestrator
The central conductor for ingestion, standardization, scoring, and deployment.
Calls modular components from a single location.
"""

import os
import json
import datetime
import sys
from pathlib import Path

# Add root to sys path for imports
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "engine"))

try:
    from intelligence_engine import IntelligenceEngine
    from data_standardizer import DataStandardizer
    from remote_sync import RemoteSync
    from ticker_utils import load_master_tickers
except ImportError:
    # If called from within engine folder
    from intelligence_engine import IntelligenceEngine
    from data_standardizer import DataStandardizer
    from remote_sync import RemoteSync
    from ticker_utils import load_master_tickers

class PipelineOrchestrator:
    def __init__(self, terminal_type="root"):
        self.terminal_type = terminal_type
        # Paths
        self.db_path = ROOT / "database"
        self.web_root = ROOT / "web"
        
        self.master_file = self.db_path / "x_intel_master.json"
        self.global_buzz_file = self.db_path / "X_INTEL_DB.json"
        self.global_visual_file = self.db_path / "X_INTEL_VISUAL_DB.json"
        
        # terminal_type logic matches ticker_utils mapping
        if terminal_type == "ai":
            self.web_dir = self.web_root / "ai"
            self.research_file = self.db_path / "AI_MASTER_DATA.json"
            self.output_js = self.web_dir / "dashboard_data.js"
        elif terminal_type == "root" or terminal_type == "semi":
            self.web_dir = self.web_root / "semi"
            self.research_file = self.db_path / "CPO_MASTER_DATA.json"
            self.output_js = self.web_dir / "dashboard_data.js"
        else:
            self.web_dir = self.web_root / terminal_type
            self.research_file = self.db_path / f"{terminal_type.upper()}_MASTER_DATA.json"
            self.output_js = self.web_dir / "dashboard_data.js"

    def load_json(self, path, default={}):
        if not path.exists(): return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def process(self):
        # 1. LOAD RAW
        master = self.load_json(self.master_file)
        research_raw = self.load_json(self.research_file)
        global_buzz = self.load_json(self.global_buzz_file).get("buzz", {})
        global_visual = self.load_json(self.global_visual_file).get("visual_mentions", {})
        
        # Consistent Ticker Discovery via ticker_utils
        target_tickers = load_master_tickers(self.terminal_type)
        print(f"--- GIGACPO Pipeline: {self.terminal_type.upper()} ({len(target_tickers)} tickers) ---")
        
        research = {}
        
        # 2. STANDARDIZE & PREPARE SCORING
        stats_map = {}
        
        if not target_tickers:
            print(f"Warning: No tickers loaded for {self.terminal_type}")
            return self

        for symbol in target_tickers:
            # We pull financials and research from research_raw (CPO_MASTER_DATA.json)
            entry = research_raw.get(symbol, {})
            
            # Extract human_research if it's nested (Root style)
            r_info_raw = entry.get("human_research", entry)
            # Ensure we don't clobber the shared entry object if they are the same
            r_info = r_info_raw.copy() if r_info_raw is entry else r_info_raw
            
            # Map legacy AI master keys (often at top level or in r_info)
            company_name = r_info.get("Company Name") or entry.get("Company Name")
            role_notes = r_info.get("Role / Notes") or entry.get("Role / Notes")
            bucket = r_info.get("Bucket") or entry.get("Bucket")
            
            if company_name and not r_info.get("Company"):
                r_info["Company"] = company_name
            if role_notes and not r_info.get("Role"):
                r_info["Role"] = role_notes
            if bucket and not r_info.get("Bucket"):
                r_info["Bucket"] = bucket
            
            # Fallback for company name
            if not r_info.get("Company") or r_info.get("Company") == symbol:
                long_name = entry.get("financials", {}).get("price", {}).get("longName") or \
                           entry.get("financials", {}).get("summaryProfile", {}).get("longName")
                r_info["Company"] = long_name or symbol

            research[symbol] = r_info
            
            # Extract Financials and Supplemental data from the rich master
            fin = entry.get("financials", {})
            obb = r_info.get("openbb_supplement", {}) or entry.get("openbb_supplement", {})
            
            summary = fin.get("summaryDetail", {})
            trend = fin.get("earningsTrend", {}).get("trend", [])
            
            # Map stats for Engine
            eps26 = next((t.get("earningsEstimate", {}).get("avg", {}).get("raw") for t in trend if t.get("period") in ["0y", "y"]), None)
            eps27 = next((t.get("earningsEstimate", {}).get("avg", {}).get("raw") for t in trend if t.get("period") in ["+1y", "1y"]), None)
            price_val = fin.get("price", {}).get("regularMarketPrice", {}).get("raw") or summary.get("regularMarketPrice", {}).get("raw", 0)
            
            # Dynamic Upside from OpenBB or Human Research
            raw_upside = obb.get("analyst_implied_upside_pct")
            upside_val = (raw_upside / 100) if raw_upside is not None else 0.25 # Default 25% if unknown
            
            # Revenue growth parsing for UI filters
            # 1. Start with human research string
            growth_str = r_info.get("Rev Growth Est")
            
            # 2. Fallback to root financial master research
            if not growth_str and symbol in financial_master:
                growth_str = financial_master[symbol].get("human_research", {}).get("Rev Growth Est", "")

            # 3. Fallback to automated financialData metrics (Live Yahoo extraction)
            rev_num = 0
            if growth_str:
                try:
                    rev_num = float(str(growth_str).replace('%','').strip()) if '%' in str(growth_str) else float(growth_str)
                except:
                    rev_num = 0
            
            if rev_num == 0:
                # Try raw revenueGrowth from financialData (0.59 = 59%)
                raw_growth = fin.get("financialData", {}).get("revenueGrowth", {}).get("raw")
                if raw_growth is not None:
                    rev_num = raw_growth * 100
                    if not growth_str:
                        growth_str = f"{rev_num:.1f}%"

            stats_map[symbol] = {
                "pe26": price_val / eps26 if eps26 and eps26 > 0 else 999,
                "pe27": price_val / eps27 if eps27 and eps27 > 0 else 999,
                "mcapB": (summary.get("marketCap", {}).get("raw") or 0) / 1e9,
                "upside": upside_val,
                "perf1y": obb.get("perf_1y"),
                "recent_7d_list": obb.get("recent_7d_status", [0]*7),
                "total_discovery": int(global_buzz.get(symbol, {}).get("7d", 0)) + len(global_buzz.get(symbol, {}).get("recent_news", [])),
                "analysts": obb.get("analyst_count"),
                "inst_pct": obb.get("inst_ownership_pct"),
                "short_pct": obb.get("short_interest_pct"),
                "conviction_count": financial_master.get(symbol, {}).get("human_research", {}).get("inst_13f_alpha", {}).get("conviction_count", 0),
                "rev_num": rev_num,
                "growth_str": growth_str,
                "obb_raw": obb # Store to prevent clobbering
            }

        # 3. SCORE
        stats_list = IntelligenceEngine.prepare_dataset_for_scoring(stats_map)
        engine = IntelligenceEngine(stats_list)
        
        # 4. BUILD PAYLOAD
        payload = {}
        for symbol in target_tickers:
            r_info = research.get(symbol, {})
            # Use engine to get dynamic scores if human override is missing
            scores = engine.calculate_ticker_score(stats_map[symbol])
            
            # Extract raw financials and history from the source
            raw_entry = research_raw.get(symbol, {})
            history = raw_entry.get("history", [])
            
            # 7-day momentum trajectory (Up/Flat=1, Down=0)
            mom_bars = stats_map.get(symbol, {}).get("recent_7d", [0]*7)
            
            # Use obb calculated status as primary, history-calc as fallback
            trajectory = mom_bars
            if not any(trajectory) and len(history) >= 8:
                pts = history[-8:]
                trajectory = [1 if pts[i]['y'] >= pts[i-1]['y'] else 0 for i in range(1, 8)]

            # Determine Alpha Score (math-driven unless manual override is NON-PLACEHOLDER)
            alpha_val = r_info.get("Alpha Score")
            if not alpha_val or alpha_val == 7.0:
                alpha_val = scores['alpha']

            # Build the finalized entry
            entry_payload = {
                "ticker": symbol,
                **stats_map[symbol],
                "human_research": {
                    **r_info,
                    "Alpha Score": alpha_val,
                    "Risk Adj": r_info.get("Risk Adj") or scores['risk'],
                    "Hiddenness": r_info.get("Hiddenness") or scores['hidden'],
                    "Target Upside": r_info.get("Target Upside") or f"+{int(stats_map[symbol]['upside']*100)}%",
                    "Rev Growth Est": stats_map[symbol].get("growth_str") or r_info.get("Rev Growth Est") or (f"{stats_map[symbol]['rev_num']}%" if stats_map[symbol]['rev_num'] else "")
                },
                "financials": raw_entry.get("financials", {}),
                "history": history,
                "performance": {
                    **(raw_entry.get("performance", {})),
                    "recent_7d_status": trajectory 
                }
            }
            # Aliases for legacy/AI terminal compatibility
            entry_payload["h"] = entry_payload["human_research"]
            entry_payload["p"] = entry_payload["performance"]
            entry_payload["obb"] = stats_map[symbol].get("obb_raw", {})
            
            payload[symbol] = entry_payload

        # 5. WRITE
        js = f"window.CPO_MASTER_DATA = {json.dumps(payload, ensure_ascii=True)};\n"
        js += f"window.DASHBOARD_METADATA = {{'last_rebuild': '{datetime.datetime.now().isoformat()}'}};"
        
        with open(self.output_js, "w", encoding="utf-8") as f:
            f.write(js)
        print(f"Success: {self.output_js.name} updated ({len(payload)} entries)")
        
        # 6. BUILD HTML FROM TEMPLATE
        self._generate_html()
        
        return self

    def _generate_html(self):
        template_path = self.web_dir / "index_template.html"
        output_html = self.web_dir / "index.html"
        
        if not template_path.exists():
            print(f"Warning: Template {template_path} not found. Skipping HTML build.")
            return

        with open(template_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Dynamic Injections
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if "Independent Autonomous Mode" in html:
            html = html.replace("Independent Autonomous Mode", f"Independent Autonomous Mode | Last Generated: {ts}")
        
        # Ensure any relative JS paths in the template point to the same directory
        # (Assuming dashboard_data.js is what the template expects)

        with open(output_html, "w", encoding="utf-8") as f:
            f.write(html)
        
        print(f"[OK] Generated {output_html.name} from template.")

    def deploy(self):
        """Auto-syncs to remote if configured."""
        if os.getenv("SFTP_HOST"):
            print(f"Deploying {self.output_js.name}...")
            RemoteSync.sync_file(Path(self.output_js))
            
            # Also sync the HTML template for this terminal
            target_html = self.web_dir / "index.html"
            if target_html.exists():
                print(f"Deploying {target_html}...")
                RemoteSync.sync_file(target_html)
        return self

if __name__ == "__main__":
    # Test run
    PipelineOrchestrator(terminal_type="ai").process()