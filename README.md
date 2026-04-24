# GIGACPO Intelligence Terminal (V26.0)

This project tracks the Co-Packaged Optics (CPO) and Silicon Photonics (SiPh) supply chain to identify high-alpha investment opportunities in the AI infrastructure build-out.

## 🚀 Primary Access

- **Sovereign Intelligence Engine**: [engine/email_market_synopsis.py](engine/email_market_synopsis.py) (V26.0 Payload Optimized)
- **CPO Intelligence Terminal**: [web/semi/index_template.html](web/semi/index_template.html) (V21.1 Root)
- **AI/Crypto Infrastructure**: [web/ai/index_template.html](web/ai/index_template.html) (V21.1 AI)
- **Status Dashboard**: [PROJECT_STATUS.md](PROJECT_STATUS.md)


## 🛠️ Installation & Prerequisites

To ensure all stealth extraction and sync engines operate correctly:

1. **Install Python 3.14+**
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Initialize Playwright**: `python -m playwright install chromium`

## 🏗️ Core Architecture

- **Web Server Bridge**: `server.py` (FastAPI + APScheduler for automated 4:20 PM EST sync).
- **Master Dataset**: `database/CPO_MASTER_DATA.json` (The Single Source of Truth).
- **Intelligence Base**: [KNOWLEDGE.md](KNOWLEDGE.md) (Living research and catalyst log).
- **Ghost Mode Engine**: [engine/financial_auditor.py](engine/financial_auditor.py) (Stealth price/data fetching).

## 🧠 LLM Brain (Shared Intelligence)

To share the entire ecosystem with another LLM (Grok/Claude/Gemini), use:

- `gigacpo_llm_handoff.md` (49KB concentrated context).
- `database/CPO_MASTER_DATA.json` (Structured JSON).

## 🛠️ Maintenance & Production

To keep the AI's logic strictly aligned with the project's evolving needs:

- `start.bat`: Option 2=Web Server Bridge, Option 4=Live Price Refresh.
- `/production-code-audit`: Performs enterprise-grade security and performance hardening.
- `/project-skill-audit`: Analyzes patterns to update Agent Skills and project governance.
- `/update`: Synchronizes all documentation with the latest code state.

---

**Production Note**: This terminal is fully autonomous. Market-close synchronization is scheduled daily at 4:20 PM EST.
