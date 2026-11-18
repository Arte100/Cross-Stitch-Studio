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
rev = collections.defaultdict(list)
for c, v in json.load(open(HERE + '/swatches/madeira_colours.json')).items():
    if len(v['rest']) > 1: rev[norm(v['rest'][1])].append(c)
for a, cs in rev.items():
    if a in d:
        alt = [c for c in uniq(cs) if c not in d[a]['p']]
        if alt: d[a]['a'] = alt
    elif a in DSET: d[a] = {'p': uniq(cs), 's': 'maker'}
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
# ---- Colour sense check. The published charts contain slips (a white matched to a dark grape, an olive to a dark brown).
# Every thread code is shared by a group of DMC threads. A DMC thread whose measured colour is far from the rest of its
# group is treated as a slip in the source and that match is removed. Nothing is invented: a slip leaves "No match"
# unless another chart offers a number that passes the same check.
import numpy as np
from skimage.color import rgb2lab, deltaE_ciede2000
_hex = {r[0]: r[2] for r in dmc}; _lab = {a: rgb2lab(np.array([[[int(h.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4)]]]))[0, 0] for a, h in _hex.items()}
def dE(a, b): return float(deltaE_ciede2000(_lab[a], _lab[b]))
FAR = 23
def natk(c):
    m = re.match(r'(\d+)', c); return int(m.group(1)) if m else -1
REPORT = []
def sense(b, d):
    for a in [a for a in d if a not in _lab]: del d[a]
    for _ in range(4):
        N = collections.defaultdict(list)
        for a, e in d.items():
            for c in e['p'] + e.get('a', []): N[c].append(a)
        codes = sorted(N, key=natk); pos = {c: i for i, c in enumerate(codes)}
        def fam(a, c):   # distance to the DMC threads matched to the neighbouring codes (makers number their colours in families)
            i = pos[c]; o = [x for cc in codes[max(0, i - 3):i] + codes[i + 1:i + 4] for x in N[cc] if x != a and x not in N[c]]
            return min([dE(a, x) for x in o] or [0])
        bad = set()
        for c, mem in N.items():
            if len(mem) < 2: continue
            near = {a: min(dE(a, x) for x in mem if x != a) for a in mem}
            lone = [a for a in mem if near[a] > FAR]
            if not lone: continue
            if len(lone) < len(mem): bad.update((a, c) for a in lone)          # the rest of the group agree with each other
            else:                                                              # nobody agrees: keep the one that fits the number family
                keep = min(mem, key=lambda a: fam(a, c)); bad.update((a, c) for a in mem if a != keep)
        if not bad: break
        for a, c in sorted(bad):
            e = d[a]; was = 'match' if c in e['p'] else 'also'
            e['p'] = [x for x in e['p'] if x != c]; e['a'] = [x for x in e.get('a', []) if x != c]
            if not e['p'] and e['a']: e['p'] = e['a'][:1]; e['a'] = e['a'][1:]
            if not e['a']: e.pop('a', None)
            REPORT.append((b, a, c, was, e['p'][0] if e['p'] else 'No match'))
            if not e['p']: del d[a]
# Slips found by eye, where a code has no group to be checked against: J&P Coats "3843" for DMC 995 is a DMC number and "3238" for
# DMC 703 is a mistyped 6238; Madeira 0101 is a pale yellow given for the dark topaz DMC 780.
for b, a, c in (('jpcoats', '995', '3843'), ('jpcoats', '703', '3238'), ('madeira', '780', '0101')):
    e = CONV[b][a]; e['p'] = [x for x in e['p'] if x != c]; REPORT.append((b, a, c, 'match', e['p'][0] if e['p'] else 'No match'))
    if not e['p']: del CONV[b][a]
for b in CONV: sense(b, CONV[b])
# ---- Second check, for brands that have colours of their own (see own_colours.py): a match is removed when the brand
# thread's own colour is clearly not the DMC thread's colour, and a closer published number is moved to the front.
OWN = {}
if os.path.exists(HERE + '/swatches/brand_colours.json'): OWN = json.load(open(HERE + '/swatches/brand_colours.json'))
def _l(h): h = h.lstrip('#'); return rgb2lab(np.array([[[int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]]]))[0, 0]
for b, own in OWN.items():
    ol = {c: _l(h) for c, h in own.items()}; d = CONV[b]
    for a in list(d):
        e = d[a]; dist = lambda c: float(deltaE_ciede2000(ol[c], _lab[a])) if c in ol else 10.0
        for c in [c for c in e['p'] + e.get('a', []) if dist(c) > 20]:
            was = 'match' if c in e['p'] else 'also'; e['p'] = [x for x in e['p'] if x != c]; e['a'] = [x for x in e.get('a', []) if x != c]
            REPORT.append((b, a, c, was + ' (own colour)', ''))
        allc = e['p'] + e.get('a', [])
        if allc and dist(allc[0]) > 12:
            best = min(allc, key=dist)
            if dist(best) < dist(allc[0]) - 6: allc.remove(best); allc.insert(0, best); n = max(1, len(e['p'])); e['p'] = allc[:1] if best not in e['p'] else [best] + [x for x in e['p'] if x != best]; e['a'] = [x for x in allc if x not in e['p']]
        if not e['p'] and e.get('a'): e['p'] = e['a'][:1]; e['a'] = e['a'][1:]
        if not e.get('a'): e.pop('a', None)
        if not e['p']: del d[a]
# ---- Our own suggestion where no published match survives: the closest thread of that brand by colour (Arte, 18 November 2026).
# Only for brands with colours of their own, and only when the closest thread is close enough to be worth offering.
OURS = collections.Counter()
for b, own in OWN.items():
    ol = {c: _l(h) for c, h in own.items()}; ks = list(ol); M = np.array([ol[c] for c in ks])
    for a in DMC:
        if a in CONV[b]: continue
        dd = deltaE_ciede2000(np.tile(_lab[a], (len(ks), 1)), M); k = int(np.argmin(dd))
        if dd[k] <= 10: CONV[b][a] = {'p': [ks[k]], 's': 'ours'}; OURS[b] += 1
# ---- Our own colour matching as a second opinion: where the published match is clearly off by colour (over 12) and another
# thread of that brand is much closer (at least 6 better), the closer thread is offered beside the published one.
CLOSER = collections.Counter()
for b, own in OWN.items():
    ol = {c: _l(h) for c, h in own.items()}; ks = list(ol); M = np.array([ol[c] for c in ks])
    for a, e in CONV[b].items():
        c = e['p'][0]
        if e['s'] == 'ours' or c not in ol: continue
        dp = float(deltaE_ciede2000(ol[c], _lab[a])); dd = deltaE_ciede2000(np.tile(_lab[a], (len(ks), 1)), M); k = int(np.argmin(dd))
        if dp > 12 and dd[k] <= dp - 6 and ks[k] not in e['p']: e['c'] = ks[k]; CLOSER[b] += 1
print('Published match kept, closer thread by colour offered beside it:', dict(CLOSER))
print('Closest by colour, our own suggestions:', dict(OURS))
print('Colour sense check removed', len(REPORT), 'entries:')
for r in REPORT: print('  ', *r)
LABEL = {'sullivans': 'Sullivans', 'madeira': 'Madeira', 'anchor': 'Anchor', 'cosmo': 'Cosmo', 'jpcoats': 'J&P Coats'}
# J&P Coats is left out (Arte, 18 November 2026: a brand we cannot validate is taken out). Its only chart is the Cyberstitchers one;
# the Goblen ART chart agrees with it on just 120 of 730 pairs, and there are no J&P Coats colours. The data stays in src/ for later.
ORDER = ['anchor', 'madeira', 'cosmo', 'sullivans']
hexof = {r[0]: r[2].upper() for r in dmc}
def nat(c):
    m = re.match(r'(\d+)(.*)', c); return (int(m.group(1)), m.group(2)) if m else (-1, c)
brands = [{'id': 'dmc', 'label': 'DMC', 'rows': [[r[0], r[1].replace('Gray', 'Grey'), r[2].upper(), ''] for r in dmc]}]
OUT = {}; RANK = {'maker': 0, 'agreed': 1, 'one': 2, 'split': 3, 'doubt': 4, 'ours': 5}
for b in ORDER:
    d = {a: v for a, v in CONV[b].items() if a in DSET}
    r = {}
    for a in DMC:
        e = d.get(a)
        if not e: continue
        if e['s'] == 'ours':      # our own suggestion: in the other direction it is only ever an extra
            for c in e['p']: r.setdefault(c, {'p': [], 'a': [], 's': 'split', 'first': []}); r[c]['a'].append(a)
            continue
        for n, c in enumerate(e['p']): r.setdefault(c, {'p': [], 'a': [], 's': e['s'], 'first': []}); r[c]['p'].append(a); r[c]['s'] = max(r[c]['s'], e['s'], key=lambda z: RANK[z]); r[c]['first'].append(n == 0)
        for c in e.get('a', []): r.setdefault(c, {'p': [], 'a': [], 's': e['s'], 'first': []}); r[c]['a'].append(a)
    rows = []
    for c in sorted(r, key=nat):
        e = r[c]; cand = [a for a, f in zip(e['p'], e['first']) if f] or e['p'] or e['a']
        best = [a for a in cand if d[a]['s'] in ('maker', 'agreed') and len(d[a]['p']) == 1] or cand
        oh = OWN.get(b, {}).get(c); rows.append([c, '', (oh or hexof[best[0]]).lstrip('#').upper(), best[0], 1 if oh else 0]); del e['first']
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
