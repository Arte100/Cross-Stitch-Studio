"""Own colours for the other brands, read from published colour pictures and brought onto our measured DMC scale.
Run after build.py has made colours/test/index.html:  python3 _build/colours/own_colours.py
Sources (raw readings are in _build/colours/swatches/):
  Madeira: the colour boxes on page 2 of the Madeira Mouline colour card, 2024 (the maker's own card)
  Anchor:  the colour cells of the Country Threads Anchor to DMC chart, and the colour boxes of the Goblen ART Anchor page
  Cosmo:   the two Cosmo pictures beside each pair on the Wyldwood Creative comparison page
Each source draws colours its own way, so one smooth correction per source is fitted from all its pairs (source colour of
a thread against our measured colour of its DMC match). What is left after that correction is the thread's own difference.
Anchor and Cosmo have two sources each. Their differences from DMC agree with each other (correlation 0.7 to 0.8), so they are averaged."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from own_calib import *
out = {}
rpA = rep('anchor'); ct = json.load(open(S + 'anchor_ct_colours.json')); gb = json.load(open(S + 'anchor_goblen_colours.json'))
ctL = {c: L(v['hex']) for c, v in ct.items()}; gbL = {c: L(h) for c, h in gb.items()}
fct = fit([(ctL[c], DL[norm(v['dmc'])]) for c, v in ct.items() if norm(v['dmc']) in DL]); fgb = fit([(gbL[c], DL[rpA[c][0]]) for c in gbL if c in rpA])
A = {}
for c in set(ctL) | set(gbL):
    v = [f(l[c]) for f, l in ((fct, ctL), (fgb, gbL)) if c in l]
    if len(v) == 2 and dE(v[0], v[1]) > 12: continue          # the two sources disagree: no own colour
    A[c] = np.mean(v, axis=0)
out['anchor'] = A
md = json.load(open(S + 'madeira_colours.json')); mL = {c: L(v['hex']) for c, v in md.items()}
fm = fit([(mL[c], DL[norm(v['rest'][1])]) for c, v in md.items() if len(v['rest']) > 1 and norm(v['rest'][1]) in DL])
out['madeira'] = {c: fm(l) for c, l in mL.items()}
rpC = rep('cosmo'); raw = [o for o in json.load(open(S + 'cosmo_raw.json')) if o['ok']]
fx = lambda t: t.replace('l', '1').replace('O', '0').replace('I', '1')
rows = [(norm(fx(o['dmc'])), fx(o['cosmo']), o) for o in raw]; rows = [r for r in rows if r[0] in DL and r[1] in rpC]
C = {}
for k in ('ct', 'cb'):
    f = fit([(L(o[k]), DL[a]) for a, c, o in rows]); g = collections.defaultdict(list)
    for a, c, o in rows: g[c].append(f(L(o[k])))
    C[k] = {c: np.median(v, axis=0) for c, v in g.items()}
out['cosmo'] = {c: (C['ct'][c] + C['cb'][c]) / 2 for c in C['ct'] if dE(C['ct'][c], C['cb'][c]) <= 12}
res = {b: {c: H(l) for c, l in sorted(d.items())} for b, d in out.items()}
json.dump(res, open(S + 'brand_colours.json', 'w'), indent=0)
for b, d in out.items():
    rp = rep(b); x = [min(dE(d[c], DL[a]) for a in rp[c]) for c in d if c in rp]
    print(b, 'threads with an own colour:', len(x), 'of', len(rp), '| difference from DMC match: median %.1f, 90th %.1f' % (np.median(x), np.percentile(x, 90)))
