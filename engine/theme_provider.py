from pathlib import Path

import yaml


class ThemeProvider:
    """
    V28: Hierarchy Leader for UI/UX Design Tokens.
    This is the authoritative source for colors, typography, and layout.
    Trickles down to email_market_synopsis.py and web/ai/index.html.
    """

    def __init__(self):
        self.root = Path(__file__).parent.parent
        self.config_path = self.root / "config" / "macro_config.yaml"
        self.theme = self._load_theme()

    def _load_theme(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config.get("ui_theme", {})
        except Exception as e:
            print(f"[WARN] [THEME] Failed to load macro_config.yaml: {e}")
            return {}

    def get_color(self, key, default="#ffffff"):
        return self.theme.get("colors", {}).get(key, default)

    def get_layout(self, key, default=0):
        return self.theme.get("layout", {}).get(key, default)

    def get_typography(self, key, default=0):
        return self.theme.get("typography", {}).get(key, default)

    def generate_web_css(self):
        """Generates the content for synopsis_web.css based on authoritative tokens."""
        colors = self.theme.get("colors", {})
        layout = self.theme.get("layout", {})
        typo = self.theme.get("typography", {})

        web_scale = typo.get("web_scale_factor", 1.0)
        pulse_scale = typo.get("pulse_scale_web", 1.0)

        css = f"""/*
 * GIGACPO SOVEREIGN INTELLIGENCE — Authoritative Web Styling
 * GENERATED FROM macro_config.yaml. DO NOT EDIT MANUALLY.
 */

:root {{
    --bg-main: {colors.get('bg_main')};
    --bg-surface: {colors.get('bg_surface')};
    --bg-accent: {colors.get('bg_accent')};
    --text-bright: {colors.get('text_bright')};
    --gold: {colors.get('gold')};
    --indigo: {colors.get('indigo')};
    --bull: {colors.get('green', '#10b981')};
    --bear: {colors.get('danger', '#f43f5e')};
}}

body {{
    background-color: var(--bg-main) !important;
    font-size: {typo.get('base_size', 14) * web_scale}px !important;
    line-height: 1.6;
}}

.main-table {{
    max-width: {layout.get('web_max_width')}px !important;
    width: 95% !important;
    margin: 20px auto !important;
    border-radius: {layout.get('border_radius')}px !important;
    overflow: hidden;
}}

/* High-Density Cockpit Scaling */
.pulse-card {{
    padding: 16px !important;
    min-height: 100px !important;
}}

.pulse-label {{
    font-size: {typo.get('pulse_label_size', 11) * pulse_scale}px !important;
    letter-spacing: 0.05em;
}}

.pulse-val {{
    font-size: {typo.get('pulse_val_size', 20) * pulse_scale}px !important;
    font-weight: 900 !important;
}}

.gauge-box {{
    transform: scale({pulse_scale * 0.75});
    transform-origin: center;
}}

/* Mobile Fluidity Overrides */
@media (max-width: 600px) {{
    .main-table {{
        width: 100% !important;
        margin: 0 !important;
        border-radius: 0 !important;
    }}
    .pulse-card {{
        padding: 10px !important;
    }}
}}
"""
        return css

    def sync_web_assets(self):
        """Writes the generated CSS to the database folder for RemoteSync propagation."""
        css_content = self.generate_web_css()
        css_path = self.root / "database" / "synopsis_web.css"
        try:
            with open(css_path, "w", encoding="utf-8") as f:
                f.write(css_content)
            print(f"[OK] [THEME] Authoritative CSS synced to {css_path.name}")
            return True
        except Exception as e:
            print(f"[ERR] [THEME] Failed to sync web assets: {e}")
            return False


# Global instance for easy access
theme = ThemeProvider()
