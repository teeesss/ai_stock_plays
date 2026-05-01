import re

with open('web/ai/index_template.html', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    ("? 'up' : '}", "? 'up' : ''}"),
    ("? '+' : '}${consensus", "? '+' : ''}${consensus"),
    ("? 'active' : '}", "? 'active' : ''}"),
    ("a.summary.substring(0,180)+'...' : '}", "a.summary.substring(0,180)+'...' : ''}"),
    ("? 'border-color:rgba(245,158,11,0.3); background:rgba(245,158,11,0.03);' : ';", "? 'border-color:rgba(245,158,11,0.3); background:rgba(245,158,11,0.03);' : '';"),
    ("? '<span style=\"color:var(--accent); font-size:8px; font-weight:900; margin-right:6px;\">[MACRO]</span>' : ';", "? '<span style=\"color:var(--accent); font-size:8px; font-weight:900; margin-right:6px;\">[MACRO]</span>' : '';"),
    ("replace('%',')", "replace('%', '')"),
    ("(a.title||')", "(a.title||'')"),
    ("(a.summary||')", "(a.summary||'')"),
    ("replace('$',')", "replace('$', '')"),
    ("` : '<span style=\"color:var(--text-dim);font-size:10px;\">--</span>'}", "'' : '<span style=\"color:var(--text-dim);font-size:10px;\">--</span>'}"),
]

for old, new in replacements:
    content = content.replace(old, new)

# One more check for any line like: `? \`...\` : '<span...`
# Wait, let's fix line 679 which was broken.
# Original: `${e.macro.score ? \`<span style="color:var(--gold);font-weight:900;">${e.macro.score}</span>\` : '<span style="color:var(--text-dim);font-size:10px;">--</span>'}</span></td>`
# Corrupted: `${e.macro.score ? \`<span style="color:var(--gold);font-weight:900;">${e.macro.score}</span>\` : '<span style="color:var(--text-dim);font-size:10px;">--</span>'}`
# Let's fix that.
content = content.replace("` : '<span style=\"color:var(--text-dim);font-size:10px;\">--</span>'}", "` : '<span style=\"color:var(--text-dim);font-size:10px;\">--</span>'}")
content = content.replace("replace('%',')", "replace('%', '')")
content = content.replace("replace('$',')", "replace('$', '')")

with open('web/ai/index_template.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed")
