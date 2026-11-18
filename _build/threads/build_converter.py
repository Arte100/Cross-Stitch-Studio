"""Builds the thread colour converter preview as one self-contained HTML file.
Usage: python3 build_converter.py <out.html> [--with-third-party]
DMC colours come from the cross stitch tool. Other brands come from the CSV files Arte supplied
(source: stitchmate.app) and are only included in the private preview."""
import sys, json, csv, base64, io, re
from PIL import Image

out = sys.argv[1]
third = '--with-third-party' in sys.argv
REPO = '/home/claude/cross-stitch-studio'
SRC = '/home/claude/threads/src'

s = open(REPO + ('/stitch/test/index.html' if '--test-colours' in sys.argv else '/stitch/index.html'), encoding='utf-8').read()
i = s.index('const DMC_RAW = `') + len('const DMC_RAW = `'); j = s.index('`', i)
dmc = [l.split(',') for l in s[i:j].strip().split('\n')]
brands = [{'id': 'dmc', 'label': 'DMC', 'rows': [[r[0], r[1], r[2].upper()] for r in dmc]}]
if third:
    for bid, label, f in [('anchor', 'Anchor', 'anchor.csv'), ('madeira', 'Madeira', 'madeira.csv'), ('cosmo', 'Cosmo', 'cosmo.csv'),
                          ('sullivans', 'Sullivans', 'sullivans.csv'), ('jpcoats', 'J&P Coats', 'jpcoats.csv')]:
        rows = []
        for x in csv.DictReader(open(f'{SRC}/{f}', encoding='utf-8-sig')):
            code = list(x.values())[0].strip(); name = x['Color Name'].strip()
            if name.lower() == f'{label.lower()} {code.lower()}': name = ''
            rows.append([code, name, x['HEX'].lstrip('#').upper()])
        brands.append({'id': bid, 'label': label, 'rows': rows})

im = Image.open(REPO + '/logo.png').convert('RGBA'); im.thumbnail((120, 120)); b = io.BytesIO(); im.save(b, 'PNG', optimize=True)
logo = 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()

html = open('/home/claude/threads/converter_template.html', encoding='utf-8').read()
html = html.replace('/*DATA*/', 'const BRANDS=' + json.dumps(brands, separators=(',', ':')) + ';').replace('LOGO_SRC', logo)
html = html.replace('<!--PRIVATE-->', '<div class="private">Private preview. The colours for brands other than DMC come from a third party and are not cleared for publishing.</div>' if third else '')
open(out, 'w', encoding='utf-8').write(html)
print(out, len(html), [(b_['id'], len(b_['rows'])) for b_ in brands])
