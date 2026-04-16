# Table Density — GIGACPO Dashboard

## Goal
Claw back horizontal real estate for Research Info/Role. Cut dead spacing without shrinking font.

## Tasks
- [ ] **T1** — `th`/`td` padding: `14px 10px` → `10px 6px` | `12px 8px` → `8px 5px`
  - Verify: rows visually tighter, text unchanged
- [ ] **T2** — Ticker width `85px` → `70px`, Company `155px` → `130px`
  - Verify: gap between ticker/company collapsed
- [ ] **T3** — Alpha/Risk/Hidden `50px` → `36px` each (chips are ~28px wide)
  - Verify: three columns noticeably narrower
- [ ] **T4** — MCap `80px` → `62px`
  - Verify: MCap→P/E '26 gap gone
- [ ] **T5** — Rev Gth `78px` → `60px`
  - Verify: gap before Research/Info/Role collapsed
- [ ] **T6** — Rename `AH / PM` → `PM/AH`, width `90px` → `72px`
  - Verify: header text updated, column tighter
- [ ] **T7** — Deploy via `remote_sync.py`
  - Verify: bmwseals.com/stocks/ reflects changes

## Done When
- [ ] Research Info/Role column visibly wider
- [ ] No font size changes
- [ ] Remote live
