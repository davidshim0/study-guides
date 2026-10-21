"""Give a page that has no dark mode the site's dark theme machinery (theme init script, dark tokens,
toggle button), copied from a reference guide. Run tools/darkfix.py afterwards.
Usage: python tools/add_dark_theme.py REFERENCE.html PAGE.html..."""
import re, sys

ref = open(sys.argv[1], encoding='utf-8').read()
init = re.search(r"<script>\(function\(\)\{\s*var t = localStorage.getItem\('theme'\).*?\}\)\(\);</script>", ref, re.S).group(0)
css_start = ref.index(':root[data-theme="dark"]{')
css_end = ref.index('/* DARKFIX-START */') if '/* DARKFIX-START */' in ref else ref.index('</style>')
css = ref[css_start:css_end].rstrip() + '\n'
btn = re.search(r'<button class="theme-toggle".*?</button>\s*<script>function toggleTheme\(\)\{.*?\}</script>', ref, re.S).group(0)

for p in sys.argv[2:]:
    s = open(p, encoding='utf-8').read()
    if 'data-theme' in s:
        print(p, 'skip (already has a theme)'); continue
    m = re.search(r'<meta charset=[^>]*>', s, re.I)
    if not m or '</style>' not in s or '<body' not in s:
        print(p, 'skip (unexpected structure)'); continue
    s = s[:m.end()] + '\n' + init + s[m.end():]
    i = s.index('</style>')
    s = s[:i] + '\n/* Dark theme (added 2026-10-21, copied from the house style) */\n' + css + s[i:]
    b = re.search(r'<body[^>]*>', s)
    s = s[:b.end()] + '\n' + btn + '\n' + s[b.end():]
    open(p, 'w', encoding='utf-8').write(s)
    print(p, 'ok')
