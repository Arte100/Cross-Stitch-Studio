"""Builds the thread colour converter (tool number 2) as one self-contained page.
Usage: python3 _build/colours/build.py <output index.html> [--test]
DMC screen colours come from the cross stitch tool (measured from our own DMC colour card).
Number matches come from the published charts in _build/colours/src (see SOURCES below)."""
import sys, json, re, base64, io, collections, os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE)); S = HERE + '/src/'
out = sys.argv[1]; TEST = '--test' in sys.argv
s = open(REPO + '/stitch/index.html', encoding='utf-8').read()
i = s.index('const DMC_RAW = `') + 17; j = s.index('`', i)
dmc = [l.split(',') for l in s[i:j].strip().split('\n')]
DMC = [r[0] for r in dmc]; DSET = set(DMC)
def norm(x):
    x = x.strip().rstrip('*').upper()
    m = {'BLANC': 'Blanc', 'WHITE': 'Blanc', 'ECRU': 'Ecru'}
    if x in m: return m[x]
    if x.isdigit() and len(x) <= 2 and int(x) < 36: return x.zfill(2)
    return x
def uniq(l):
    o = []
    for x in l:
        if x not in o: o.append(x)
    return o
CONV = {}
# ---- Sullivans: the maker's own chart
d = {}
t = open(S + 'sullivans_msw.txt').read().split()
for a, c in zip(t[0::2], t[1::2]): d[norm(a)] = {'p': [c], 's': 'maker'}
for n in range(1, 36): d[str(n).zfill(2)] = {'p': [str(45002 + n)], 's': 'maker'}
CONV['sullivans'] = d
# ---- Madeira: the maker's own colour card (2024)
d = {}; L = [l for l in open(S + 'madeira_p1_dmc.txt').read().split('\n') if l]
for k in range(0, len(L), 2):
    ds = L[k][3:].replace('B 5200', 'B5200').split(); ms = [x for x in L[k + 1][3:].split() if re.fullmatch(r'\d{4}', x)]
    assert len(ds) == len(ms)
    for a, c in zip(ds, ms): d[norm(a)] = {'p': [c], 's': 'maker'}
rev = collections.defaultdict(list); L = [l for l in open(S + 'madeira_p2.txt').read().split('\n') if l]
for k in range(0, len(L), 3):
    for c, a in zip(L[k].split()[1:], L[k + 2].split()[1:]): rev[norm(a)].append(c)
for a, cs in rev.items():
    if a in d:
        alt = [c for c in uniq(cs) if c not in d[a]['p']]
        if alt: d[a]['a'] = alt
for a in ('3847', '3848', '3765'): d[a]['s'] = 'doubt'   # looks like a slip in the maker's chart (3847/3848 repeat 3347/3348; 3765 is given a white)
CONV['madeira'] = d
# ---- Anchor: three independent charts, cross-checked
ct = collections.defaultdict(list); t = open(S + 'country_anchor_dmc.txt').read().split()
for a, x in zip(t[0::2], t[1::2]): ct[norm(x)].append(a)
VALID = set(t[0::2])
cy = {}
for l in open(S + 'cyber_dmc_anchor.txt'):
    a, v = l.strip().split('='); cy[norm(a)] = [c for c in v.split('/') if c in VALID]
lm = {}
for l in open(S + 'lazymay.tsv').read().split('\n')[1:]:
    p = [x.strip() for x in l.split('\t')]
    if len(p) >= 4 and p[2].rstrip('†') in VALID: lm[norm(p[0])] = p[2].rstrip('†')
d = {}
for a in DMC:
    srcs = [x for x in (ct.get(a, []), cy.get(a, []), [lm[a]] if a in lm else []) if x]
    if not srcs: continue
    votes = collections.Counter(c for x in srcs for c in set(x)); allc = uniq([c for x in ([lm[a]] if a in lm else [], ct.get(a, []), cy.get(a, [])) for c in x])
    win = [c for c in allc if votes[c] >= 2]
    if win: d[a] = {'p': win, 's': 'agreed'}
    else: d[a] = {'p': allc[:1], 's': 'split' if len(srcs) > 1 else 'one'}
    alt = [c for c in allc if c not in d[a]['p']]
    if alt: d[a]['a'] = alt
CONV['anchor'] = d
# ---- Cosmo: one independent chart
d = {}; t = open(S + 'cosmo_sm.txt').read().split()
for a, c in zip(t[0::2], t[1::2]):
    if c != '-': d[norm(a)] = {'p': [c], 's': 'one'}
CONV['cosmo'] = d
# ---- J&P Coats (older numbers): one independent chart
d = {}
for e in open(S + 'jpcoats_cyber.txt').read().strip().split(';'):
    a, v = e.split(' '); d[norm(a)] = {'p': v.split('/'), 's': 'one'}
CONV['jpcoats'] = d
LABEL = {'sullivans': 'Sullivans', 'madeira': 'Madeira', 'anchor': 'Anchor', 'cosmo': 'Cosmo', 'jpcoats': 'J&P Coats'}
ORDER = ['anchor', 'madeira', 'cosmo', 'sullivans', 'jpcoats']
hexof = {r[0]: r[2].upper() for r in dmc}
def nat(c):
    m = re.match(r'(\d+)(.*)', c); return (int(m.group(1)), m.group(2)) if m else (-1, c)
brands = [{'id': 'dmc', 'label': 'DMC', 'rows': [[r[0], r[1].replace('Gray', 'Grey'), r[2].upper(), ''] for r in dmc]}]
OUT = {}; RANK = {'maker': 0, 'agreed': 1, 'one': 2, 'split': 3, 'doubt': 4}
for b in ORDER:
    d = {a: v for a, v in CONV[b].items() if a in DSET}
    r = {}
    for a in DMC:
        e = d.get(a)
        if not e: continue
        for n, c in enumerate(e['p']): r.setdefault(c, {'p': [], 'a': [], 's': e['s'], 'first': []}); r[c]['p'].append(a); r[c]['s'] = max(r[c]['s'], e['s'], key=lambda z: RANK[z]); r[c]['first'].append(n == 0)
        for c in e.get('a', []): r.setdefault(c, {'p': [], 'a': [], 's': e['s'], 'first': []}); r[c]['a'].append(a)
    rows = []
    for c in sorted(r, key=nat):
        e = r[c]; cand = [a for a, f in zip(e['p'], e['first']) if f] or e['p'] or e['a']
        best = [a for a in cand if d[a]['s'] in ('maker', 'agreed') and len(d[a]['p']) == 1] or cand
        rows.append([c, '', hexof[best[0]], best[0]]); del e['first']
        if not e['a']: del e['a']
        if not e['p']: e['s'] = 'split'
    brands.append({'id': b, 'label': LABEL[b], 'rows': rows}); OUT[b] = {'d': d, 'r': r}
    st = collections.Counter(v['s'] for v in d.values())
    print(b, 'DMC threads with a match:', len(d), 'of', len(DMC), dict(st), '| threads in this brand:', len(rows))
im = Image.open(REPO + '/logo.png').convert('RGBA'); im.thumbnail((120, 120)); bio = io.BytesIO(); im.save(bio, 'PNG', optimize=True)
html = open(HERE + '/template.html', encoding='utf-8').read()
html = html.replace('/*DATA*/', 'const BRANDS=' + json.dumps(brands, separators=(',', ':')) + ';\nconst CONV=' + json.dumps(OUT, separators=(',', ':')) + ';')
html = html.replace('LOGO_SRC', 'data:image/png;base64,' + base64.b64encode(bio.getvalue()).decode())
html = html.replace('<!--PRIVATE-->', '<div class="private">Test copy. Not yet public.</div>' if TEST else '')
html = html.replace('<!--ROBOTS-->', '<meta name="robots" content="noindex">' if TEST else '')
assert '/*DATA*/' not in html
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True); open(out, 'w', encoding='utf-8').write(html); print(out, len(html))
