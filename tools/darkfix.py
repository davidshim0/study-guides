"""Dark mode for study guides: EVERYTHING dark (cards, tinted boxes, figures). Idempotent: replaces its marked block."""
import re, sys
MARK_A, MARK_B = '/* DARKFIX-START */', '/* DARKFIX-END */'
DARK_BG, CARD = (0x17, 0x14, 0x0F), (0x22, 0x1E, 0x17)
def hx(c): c = c.lstrip('#'); return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
def h(c): return '#%02X%02X%02X' % tuple(int(round(v)) for v in c)
def lum(c):
    a = [v/255 for v in c]; a = [v/12.92 if v <= .03928 else ((v+.055)/1.055)**2.4 for v in a]
    return .2126*a[0] + .7152*a[1] + .0722*a[2]
def cr(a, b): l1, l2 = lum(a), lum(b); return (max(l1, l2)+.05)/(min(l1, l2)+.05)
def mix(a, b, t): return tuple(a[i]*t + b[i]*(1-t) for i in range(3))
def lighten(c, target=4.8):
    t = 0.0; c0 = c
    while cr(c, CARD) < target and t < 1:
        t += .02; c = tuple(round(v + (255-v)*t) for v in c0)
    return c
def css_rules(css):
    """(selector, body) for top-level rules; rules inside @-blocks are skipped."""
    out=[]; i=0; n=len(css)
    while i<n:
        j=css.find('{',i)
        if j<0: break
        sel=css[i:j].strip()
        depth=1; k=j+1
        while k<n and depth:
            if css[k]=='{': depth+=1
            elif css[k]=='}': depth-=1
            k+=1
        body=css[j+1:k-1]
        if not sel.startswith('@') and '{' not in body: out.append((re.sub(r'/\*.*?\*/','',sel,flags=re.S).strip(), body))
        i=k
    return out
HEX=r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b'
def full(c):
    c=c.lstrip('#'); return c if len(c)==6 else ''.join(x*2 for x in c)
def darkify_literals(s, vals):
    D=':root[data-theme="dark"]'; rules=[]
    style=s[s.index('<style>')+7:s.index('</style>')] if '<style>' in s else ''
    style=re.sub(re.escape(MARK_A)+r'.*?'+re.escape(MARK_B),'',style,flags=re.S)
    style=re.sub(r'/\*.*?\*/','',style,flags=re.S)
    for sel,body in css_rules(style):
        if not sel or 'svg' in sel or sel.startswith(':root') and 'data-theme' not in sel: continue
        decl=[]
        m=re.search(r'(?<![-a-z])color:\s*'+HEX,body)
        accent_bg=re.search(r'background[^;]*var\(--(honey|honey-deep|dram|ltram|optane|ink)\)',body)
        if m and not accent_bg:
            c=hx(full(m.group(1)))
            if cr(c,CARD)<4.5: decl.append('color:%s' % h(lighten(c, 7.0)))
        m=re.search(r'background(?:-color)?:\s*'+HEX,body)
        mr=re.search(r'background(?:-color)?:\s*rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+))?\)',body)
        if m:
            c=hx(full(m.group(1)))
            if lum(c)>0.45: decl.append('background:%s' % h(mix(c,CARD,.12)))
        elif mr:
            c=tuple(int(mr.group(i)) for i in (1,2,3)); a=float(mr.group(4) or 1)
            if lum(c)>0.45 and a>0.3: decl.append('background:rgba(%d,%d,%d,%s)' % (tuple(int(v) for v in mix(c,CARD,.12))+(mr.group(4) or '1',)))
        mb=re.search(r'background(?:-color)?:\s*var\(--(ink|honey)\)',body)
        if mb:
            if mb.group(1)=='ink':
                decl=['background:#3A342B','color:var(--ink)','border-color:var(--ink-faint)']
            elif 'honey' in vals:
                hv=hx(vals['honey'])
                decl=['background:%s' % h(mix(hv,CARD,.28)),'color:%s' % h(lighten(hv,7.0)),'border-color:%s' % vals['honey']]
        if decl:
            parts=[x.strip() for x in sel.split(',') if x.strip()]
            parts=[x if x.startswith(D) else D+' '+x for x in parts]
            rules.append('%s{%s}' % (','.join(parts), ';'.join(d+' !important' for d in decl)))
    body_html=s[s.index('</style>'):]
    body_html=re.sub(r'<svg\b.*?</svg>','',body_html,flags=re.S)
    seen=set()
    for m in re.finditer(r'style="([^"]*)"',body_html):
        st=m.group(1)
        for mm in re.finditer(r'(?<![-a-z])(color):\s*('+HEX+')',st):
            lit=mm.group(0); c=hx(full(mm.group(3)))
            if lit in seen or cr(c,CARD)>=4.5: continue
            seen.add(lit); rules.append('%s [style*="%s"]:not(svg *){color:%s !important}' % (D,lit,h(lighten(c, 7.0))))
        for mm in re.finditer(r'(background(?:-color)?):\s*('+HEX+')',st):
            lit=mm.group(0); c=hx(full(mm.group(3)))
            if lit in seen or lum(c)<=0.45: continue
            seen.add(lit); rules.append('%s [style*="%s"]:not(svg *){background:%s !important}' % (D,lit,h(mix(c,CARD,.12))))
    return rules

def block(s):
    root = re.search(r':root\{([^}]*)\}', s)
    vals = dict(re.findall(r'--([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6})', root.group(1))) if root else {}
    dvars = []
    for k, v in vals.items():
        if k.endswith('-soft') and k != 'ink-soft':                       # tinted backgrounds -> dark tints of their accent
            base = vals.get(k[:-5], v)
            dvars.append('--%s:%s' % (k, h(mix(hx(base), CARD, .20))))
        elif (not re.search(r'(^|-)(ink|paper|card|line|bg|shadow|radius)', k) and lum(hx(v)) < 0.5
              and cr(hx(v), CARD) < 4.5):
            dvars.append('--%s:%s' % (k, h(lighten(hx(v)))))   # accents readable on dark
    nodark = re.sub(re.escape(MARK_A) + r'.*?' + re.escape(MARK_B), '', s, flags=re.S)
    have = set(re.findall(r'--([a-z0-9-]+)\s*:', ' '.join(re.findall(r':root\[data-theme="dark"\]\s*\{([^}]*)\}', nodark))))
    for k, v in (('ink', '#ECE4D6'), ('ink-soft', '#B6AB98'), ('ink-faint', '#8A7F6C')):
        if k in vals and k not in have:
            dvars.append('--%s:%s' % (k, v))
    D = ':root[data-theme="dark"]'
    css = [MARK_A, '/* Dark mode: everything dark, including tinted cards and figures (figures are inverted). */']
    if dvars: css.append('%s{%s}' % (D, ';'.join(dvars)))
    css += [
      '%s :is(figure.viz,figure.paperfig,.analogy .ill){background:var(--card) !important;border-color:var(--line) !important}' % D,
      '%s :is(figure.viz,.analogy .ill) svg{filter:invert(.88) hue-rotate(180deg)}' % D,
      '%s :is(figure,.analogy .ill) img{filter:invert(.88) hue-rotate(180deg)}' % D,
      '%s{color-scheme:dark}' % D,
      '%s :is(input,select,textarea){background:var(--card) !important;color:var(--ink) !important;border-color:var(--line-strong) !important}' % D,
      '%s .bar-fill{filter:brightness(.8)}' % D,
      '%s .viz-title{color:var(--ink) !important}' % D,
      '%s .viz-kicker{color:var(--ink-faint) !important}' % D,
      '%s :is(figure.viz,figure.paperfig) figcaption,%s figure.viz .legend span{color:var(--ink-soft) !important}' % (D, D),
      '%s :is(.tbtn,.tbl .best:hover td){color:var(--ink) !important}' % D,
      '%s .card[style*="-soft"]{background:var(--card) !important;border-color:var(--line) !important}' % D,
      '%s .card[style*="-soft"] :is(h3,h4,ul,ol,li,p,span,div,td,th){color:var(--ink) !important}' % D,
      '%s .card[style*="-soft"] :is(em,i){color:var(--ink-soft) !important}' % D,
      '%s [style*="-soft"] [style*="color:#"],%s [style*="-soft"][style*="color:#"]{color:var(--ink) !important}' % (D, D),
      ] + darkify_literals(s, vals) + [MARK_B]
    return '\n'.join(css)
for p in sys.argv[1:]:
    s = open(p, encoding='utf-8').read()
    if ':root[data-theme="dark"]' not in s or '</style>' not in s:
        print(p, 'skip (no dark theme)'); continue
    s = re.sub(re.escape(MARK_A) + r'.*?' + re.escape(MARK_B) + r'\n?', '', s, flags=re.S)
    i = s.index('</style>')
    s = s[:i] + block(s) + '\n' + s[i:]
    open(p, 'w', encoding='utf-8').write(s)
    print(p, 'ok')
