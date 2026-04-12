# Active Issues & Resolutions

- **[FIXED] Browser CORS Security Block**: Browser prohibits `fetch()` from local filesystem.
  - **Resolution**: Implemented JS Data Bridge (`research/sync_data.py`).
- **[OPEN] Graphviz Binary Missing**: `dot` executable not in PATH for automated infographics.
  - **Resolution**: Switched to pure-Python `Pillow` generation.
- **[OPEN] Data Gaps**: Revenue estimates for Tier-2 suppliers (AXTI, Sumitomo) are estimates.
  - **Status**: Research ongoing in `TASKS.md`.
