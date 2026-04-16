# Terminal Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix sorting logic, correct date display lag (social posts), and add a visible last-sync timestamp to the Intelligence Terminal.

**Architecture:** Frontend modifications to `cpo_plays.html` script and UI sections. Prevents timezone shifts by using raw date strings and repairs broken sorting by correctly mapping columns to data fields.

**Tech Stack:** Vanilla JavaScript, HTML5.

---

### Task 1: Fix Sorting Logic

**Files:**
- Modify: `x:\COS_Stock_Plays\cpo_plays.html`:632-659 (Remove duplicate `setSort`)
- Modify: `x:\COS_Stock_Plays\cpo_plays.html`:639-659 (Update `sortFn`)
- Modify: `x:\COS_Stock_Plays\cpo_plays.html`:712-716 (Update `setSort` logic if needed)

- [ ] **Step 1: Cleanup duplicate setSort**
Find the `function setSort(col)` at line 632 and delete it if it's redundant (the one at 712 is the authoritative one used by window).

- [ ] **Step 2: Update sortFn to handle columns correctly**
Update the `sortFn` logic to handle `today` using `todayChg` and `todayPct` using `todayPct`.

```javascript
// Replacement for lines 640-659 (approx)
function sortFn(a, b) {
    let av, bv; const col = state.sortCol || 'best';
    if (col === 'best') { av = a.score; bv = b.score; }
    else if (col === 'pinned') { av = state.pinned.includes(a.ticker)?1:0; bv = state.pinned.includes(b.ticker)?1:0; }
    else if (col === 'ticker') { av = a.ticker; bv = b.ticker; }
    else if (col === 'company') { av = (a.h.Company||'').toLowerCase(); bv = (b.h.Company||'').toLowerCase(); }
    else if (col === 'alpha') { av = sfloat(a.h['Alpha Score']); bv = sfloat(b.h['Alpha Score']); }
    else if (col === 'risk') { av = sfloat(a.h['Risk Adj']); bv = sfloat(b.h['Risk Adj']); }
    else if (col === 'country') { av = (a.exchange||'').toLowerCase(); bv = (b.exchange||'').toLowerCase(); }
    else if (col === 'upside') { av = parseUpside(a.h['Target Upside']); bv = parseUpside(b.h['Target Upside']); }
    else if (col === 'mcap') { av = a.mcapB; bv = b.mcapB; }
    else if (col === 'pe26') { av = a.pe26; bv = b.pe26; }
    else if (col === 'pe27') { av = a.pe27; bv = b.pe27; }
    else if (col === 'perf1y') { av = a.perf1y??-9999; bv = b.perf1y??-9999; }
    else if (col === 'rev') { av = a.rev_num; bv = b.rev_num; }
    else if (col === 'today') { av = a.todayChg??-9999; bv = b.todayChg??-9999; } // FIXED: Use dollar move
    else if (col === 'todayPct') { av = a.todayPct??-9999; bv = b.todayPct??-9999; } // FIXED: Added case
    else if (col === 'ext')   { av = a.extPct??-9999;   bv = b.extPct??-9999; }
    else { av = (a.h.Role||'')+(a.h.Notes||''); bv = (b.h.Role||'')+(b.h.Notes||''); }
    
    if (typeof av === 'string' && typeof bv === 'string') return av.localeCompare(bv) * state.sortDir;
    return (av < bv ? -1 : (av > bv ? 1 : 0)) * state.sortDir;
}
```

- [ ] **Step 3: Verify sorting behavior**
Open `cpo_plays.html` (mentally or via temporary test) and ensure `setSort` uses `state.sortDir = -1` for initial click.

- [ ] **Step 4: Commit**
```bash
git add cpo_plays.html
git commit -m "fix: repair Day $ and % Chg sorting logic"
```

### Task 2: Fix Social Intelligence Date Lag

**Files:**
- Modify: `x:\COS_Stock_Plays\cpo_plays.html`:780-848 (renderIntel function)

- [ ] **Step 1: Change date parsing logic**
In `renderIntel`, avoid `toLocaleDateString()` to prevent timezone shifts.

```javascript
// Change line 793 (approx)
// OLD: const date = new Date(p.timestamp).toLocaleDateString();
// NEW:
const date = p.timestamp ? p.timestamp.split('T')[0] : 'Unknown';
```

- [ ] **Step 2: Commit**
```bash
git add cpo_plays.html
git commit -m "fix: correct timezone shift in social intelligence terminal"
```

### Task 3: Add Last Sync Timestamp to Social Terminal

**Files:**
- Modify: `x:\COS_Stock_Plays\cpo_plays.html`:288-300 (Intel Modal Header)
- Modify: `x:\COS_Stock_Plays\cpo_plays.html`:719-740 (filterIntel function)

- [ ] **Step 1: Update HTML for Intellectual Terminal Header**
Add a container for the timestamp.

```html
<!-- Inside intel-header (line 289 approx) -->
<div>𝕏 SOCIAL INTELLIGENCE TERMINAL <span id="intel-sync-time" style="font-size:9px; color:var(--text-dim); margin-left:15px; font-weight:700;"></span></div>
```

- [ ] **Step 2: Update filterIntel to populate timestamp**
Inject the `visual_last_updated` value from the module.

```javascript
// Inside filterIntel() (line 724 approx)
function filterIntel() {
    // ...existing code...
    const module = window.X_INTEL_MODULE || { posts: [] };
    
    // ADD THIS:
    const syncTimeEl = document.getElementById('intel-sync-time');
    if (syncTimeEl && module.visual_last_updated) {
        const d = new Date(module.visual_last_updated);
        syncTimeEl.innerText = `LATEST SYNC: ${d.toLocaleString([], {month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'})} EST`;
    }
    // ...existing code...
}
```

- [ ] **Step 3: Commit**
```bash
git add cpo_plays.html
git commit -m "feat: add last-sync timestamp to social intelligence terminal"
```

### Task 4: Final Verification & Deploy

- [ ] **Step 1: Run build and deploy**
```powershell
npm run build; npm run deploy
```

- [ ] **Step 2: Verify live URL**
Check `https://bmwseals.com/stocks/` for 4/16/2026 data and correct sorting.
