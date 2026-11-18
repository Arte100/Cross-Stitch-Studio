"""Builds the pages of The Jolly Makery website.

Usage: python3 build_site.py <output folder> live|preview

live:    links end in a slash (thejollymakery.com/learn/)
preview: links end in index.html, so the pages also work where folders are not served
"""
import hashlib
import os
import sys

OUT, MODE = sys.argv[1], sys.argv[2]
IDX = "" if MODE == "live" else "index.html"
EMAIL = "thejollymakery+feedback@gmail.com"

CSS = """/* Colours follow the theme chosen here or in any tool. The names match the cross stitch tool. */
:root{--bg:#F7DDE2;--surface:#ffffff;--ink:#3A0F18;--muted:#7A4450;--line:#EFC4CD;--accent:#8F1A2E;--accent-ink:#ffffff;color-scheme:light}
:root[data-skin="lavender"]{--bg:#ECE9F8;--ink:#221C3F;--muted:#5B5580;--line:#D3CDEE;--accent:#4B3FA3}
:root[data-skin="mint"]{--bg:#E3F3EC;--ink:#0F2F26;--muted:#3F6558;--line:#BFE0D2;--accent:#17685A}
:root[data-skin="sky"]{--bg:#E3EEF8;--ink:#12283D;--muted:#45617D;--line:#C2D7EB;--accent:#1F5C94}
:root[data-skin="classic"]{--bg:#eef0f4;--ink:#1b2233;--muted:#5d6678;--line:#d5d9e2;--accent:#b3203a}
:root[data-skin="dark"]{--bg:#141821;--surface:#1e2430;--ink:#e9ecf3;--muted:#9aa3b5;--line:#343c4c;--accent:#ff6b81;--accent-ink:#1b0a0e;color-scheme:dark}
:root{--soft:color-mix(in srgb,var(--bg) 35%,var(--surface));--accent-deep:color-mix(in srgb,var(--accent) 80%,var(--ink))}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;overflow-y:scroll}
body{margin:0;background:var(--bg);color:var(--ink);font-family:Figtree,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:1rem;line-height:1.5}
img{max-width:100%;height:auto}
a{color:var(--accent)}
a:hover{color:var(--ink)}
h1,h2,h3{font-family:"Bricolage Grotesque",Figtree,sans-serif;font-weight:700;margin:0;line-height:1.1}
h1{font-size:clamp(2.1rem,6vw,3.5rem)}
h2{font-size:clamp(1.7rem,4vw,2.25rem)}
h3{font-size:1.4rem}
p{margin:0}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px}
.band{padding:56px 0}
.white{background:var(--surface)}
.stack{display:flex;flex-direction:column;gap:16px}
.muted{color:var(--muted)}
.lead{font-size:1.2rem;color:var(--muted);max-width:36rem}
.eyebrow{font-size:.85rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}
header.site{background:var(--surface);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}
header.site .wrap{display:flex;flex-wrap:wrap;align-items:center;gap:4px 12px;padding-top:8px;padding-bottom:8px}
.brand{display:flex;align-items:center;gap:12px;text-decoration:none;color:var(--ink);font-family:"Bricolage Grotesque",Figtree,sans-serif;font-size:1.4rem;font-weight:700}
.brand img{width:46px;height:auto}
nav.main{display:flex;gap:4px;margin-left:auto}
nav.main a{min-height:44px;padding:0 14px;display:flex;align-items:center;border-radius:22px;color:var(--ink);font-weight:600;text-decoration:none}
nav.main a[aria-current="page"]{background:var(--bg)}
nav.main a:hover{background:var(--soft)}
details.theme{position:relative}
details.theme summary{list-style:none;min-height:44px;padding:0 14px;display:flex;align-items:center;gap:8px;border-radius:22px;border:1px solid var(--line);color:var(--accent);font-weight:700;cursor:pointer;user-select:none}
details.theme summary::-webkit-details-marker{display:none}
details.theme summary svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
details.theme[open] summary,details.theme summary:hover{background:var(--soft)}
.themelist{position:absolute;right:0;top:calc(100% + 8px);width:220px;background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:8px;display:flex;flex-direction:column;gap:2px;box-shadow:0 10px 30px rgba(0,0,0,.18)}
.themelist button{min-height:44px;padding:0 10px;display:flex;align-items:center;gap:12px;border:none;border-radius:10px;background:transparent;color:var(--ink);font:inherit;font-weight:600;text-align:left;cursor:pointer}
.themelist button:hover{background:var(--soft)}
.themelist button[aria-pressed="true"]{background:var(--bg);font-weight:700}
.themelist i{flex:none;width:24px;height:24px;border-radius:12px;border:1px solid var(--line)}
.social{display:flex;flex-wrap:wrap;gap:8px}
.social a{min-height:44px;padding:0 16px;display:inline-flex;align-items:center;border-radius:22px;border:1px solid var(--accent);color:var(--accent);font-weight:700;text-decoration:none}
.social a:hover{background:var(--accent);color:var(--accent-ink)}
.card h2{font-size:1.5rem}
.grid.three{grid-template-columns:repeat(3,1fr)}
@media (max-width:900px){.grid.three{grid-template-columns:repeat(2,1fr)}}
@media (max-width:560px){.grid.three{grid-template-columns:1fr}}
.card .btn.follow{font-size:.95rem;padding:0 12px;white-space:nowrap}
.card .btn.off{background:transparent;border-style:dashed;color:var(--muted);border-color:var(--muted);cursor:default}
.btn{min-height:52px;padding:0 24px;display:inline-flex;align-items:center;justify-content:center;border-radius:26px;background:var(--accent);color:var(--accent-ink);font-size:1.05rem;font-weight:700;text-decoration:none;border:2px solid var(--accent);font-family:inherit;cursor:pointer}
.btn:hover{background:var(--accent-deep);border-color:var(--accent-deep);color:var(--accent-ink)}
.btn.ghost{background:var(--surface);color:var(--accent)}
.btn.ghost:hover{background:var(--soft);color:var(--accent);border-color:var(--accent)}
.btn.light{background:var(--surface);color:var(--accent);border-color:var(--surface)}
.btn.light:hover{background:var(--soft);color:var(--accent);border-color:var(--soft)}
.row{display:flex;flex-wrap:wrap;gap:12px}
.hero{display:flex;flex-wrap:wrap;align-items:center;gap:40px}
.hero>div:first-child{flex:1 1 420px}
.hero>div:last-child{flex:1 1 260px;display:flex;justify-content:center}
.hero img{width:100%;max-width:360px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px}
.card{background:var(--surface);border-radius:20px;padding:24px;display:flex;flex-direction:column;gap:12px}
.card.pink{background:var(--bg)}
.card.soft{background:var(--soft);border:1px solid var(--line)}
a.card{text-decoration:none;color:var(--ink)}
a.card:hover{border-color:var(--accent);color:var(--ink)}
.card .btn{margin-top:auto;min-height:48px}
.tag{align-self:flex-start;padding:4px 12px;border-radius:12px;background:var(--accent);color:var(--accent-ink);font-size:.8rem;font-weight:700}
.tag.line{background:transparent;border:1px solid var(--accent);color:var(--accent)}
.num{font-family:"Bricolage Grotesque",Figtree,sans-serif;font-size:2.5rem;font-weight:700;color:var(--accent);line-height:1}
ol.steps{margin:0;padding:0;list-style:none}
.callout{background:var(--accent);color:var(--accent-ink);border-radius:24px;padding:36px;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:20px}
.callout>div{flex:1 1 320px}
.callout p{font-size:1.1rem}
article.guide{background:var(--surface);border-radius:20px;padding:28px;display:flex;flex-direction:column;gap:14px}
article.guide ul,article.guide ol{margin:0;padding-left:1.3rem;display:flex;flex-direction:column;gap:6px}
.narrow{max-width:760px}
form.fb{background:var(--surface);border-radius:20px;padding:24px;display:flex;flex-direction:column;gap:16px}
form.fb label,form.fb legend{font-weight:700}
form.fb fieldset{border:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px}
form.fb legend{padding:0;margin-bottom:6px}
form.fb .opt{min-height:48px;padding:0 14px;border-radius:14px;border:1px solid var(--muted);display:flex;align-items:center;gap:12px;font-weight:600}
form.fb input[type=radio]{width:20px;height:20px;accent-color:var(--accent)}
form.fb textarea,select{width:100%;padding:12px 14px;border-radius:14px;border:1px solid var(--muted);font:inherit;color:var(--ink);background:var(--surface)}
select{min-height:48px}
.field{display:flex;flex-direction:column;gap:6px}
.small{font-size:.9rem}
footer.site{padding:28px 0 40px;font-size:.95rem;color:var(--muted)}
footer.site .wrap{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-end;gap:16px}
footer.site nav{display:flex;flex-wrap:wrap;gap:4px 18px}
footer.site a{min-height:44px;display:inline-flex;align-items:center}
main :target,article.guide{scroll-margin-top:130px}
@media (max-width:760px){
header.site .wrap{padding-left:16px;padding-right:16px}
.brand{flex:1;min-width:0;font-size:1.2rem}
.brand img{width:40px}
details.theme{order:2}
details.theme summary span{display:none}
details.theme summary{padding:0;width:44px;justify-content:center}
nav.main{order:3;flex:1 0 100%;margin-left:0;overflow-x:auto;white-space:nowrap;scrollbar-width:none;gap:2px}
nav.main::-webkit-scrollbar{display:none}
nav.main a{flex:none;padding:0 11px;font-size:.95rem;min-height:40px}
}
@media (max-width:560px){.band{padding:40px 0}.callout{padding:26px}.btn{width:100%}}
"""

CSS_VER = hashlib.md5(CSS.encode()).hexdigest()[:8]

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=Figtree:wght@400;500;600;700&display=swap" rel="stylesheet">'

# Social media accounts: (name, address, what we post there). Leave the address as None until the account exists:
# the Community page then shows "Coming soon" for it, and the footer lists only the accounts that have an address.
SOCIAL = [
    ("Instagram", "https://www.instagram.com/thejollymakery", "Finished pieces, work in progress and new designs."),
    ("Facebook", "https://www.facebook.com/thejollymakery", "News, and a place to share what you have made."),
    ("TikTok", "https://www.tiktok.com/@thejollymakery", "Short videos of patterns being made and stitched."),
    ("YouTube", "https://www.youtube.com/@thejollymakery", "Longer guides to the tools, step by step."),
    ("Pinterest", "https://uk.pinterest.com/thejollymakery/", "Pattern ideas and colour palettes to save."),
    ("X", "https://x.com/thejollymakery", "Short updates and news about the tools."),
]

THEMES = [("pink", "Pink", "#F7DDE2", "#8F1A2E"), ("lavender", "Lavender", "#ECE9F8", "#4B3FA3"), ("mint", "Mint", "#E3F3EC", "#17685A"),
          ("sky", "Sky blue", "#E3EEF8", "#1F5C94"), ("classic", "Classic grey", "#eef0f4", "#b3203a"), ("dark", "Dark", "#141821", "#ff6b81")]
THEME_BUTTONS = "\n".join(
    '<button type="button" data-skin="%s"><i style="background:linear-gradient(135deg,%s 50%%,%s 50%%)"></i>%s</button>' % (i, bg, ac, n)
    for i, n, bg, ac in THEMES)

NAV = [("home", "Home", ""), ("tools", "Tools", "tools/"), ("learn", "Learning hub", "learn/"), ("shop", "Shop", "shop/"),
       ("community", "Community", "community/"), ("feedback", "Feedback", "feedback/"), ("about", "About us", "about/")]


def link(up, target):
    """A link from a page `up` folders deep to a site path such as 'learn/' or '#tools'."""
    if target == "":
        return (up + IDX) or "./"
    if target.startswith("#"):
        return (up + IDX) + target
    return up + target + IDX


def page(path, key, title, desc, body):
    depth = path.count("/")
    up = "../" * depth
    nav = "\n".join(
        '<a href="%s"%s>%s</a>' % (link(up, t), ' aria-current="page"' if k == key else "", label)
        for k, label, t in NAV)
    live_social = [(n, u) for n, u, _ in SOCIAL if u]
    social = ""
    if live_social:
        social = '<nav class="social" aria-label="Social media">' + "".join('<a href="%s" rel="noopener">%s</a>' % (u, n) for n, u in live_social) + "</nav>"
    stitch = "http://thejollymakery.com/" if MODE == "preview" else up + "stitch/"
    body = body.replace('{UP}stitch/{IDX}', stitch).replace('{UP}', up).replace('{IDX}', IDX)
    html = f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#F7DDE2">
<meta name="description" content="{desc}">
<title>{title}</title>
<link rel="icon" href="{up}stitch/favicon-32.png">
<link rel="apple-touch-icon" href="{up}stitch/apple-touch-icon-180.png">
{FONTS}
<link rel="stylesheet" href="{up}site.css?v={CSS_VER}">
<script>
/* The colour theme is shared with the tools: both read and save the same setting on this device. */
(function(){{try{{var s=localStorage.getItem("xs.skin");if(s&&s!=="pink")document.documentElement.setAttribute("data-skin",s);}}catch(e){{}}}})();
</script>
</head>
<body>
<header class="site"><div class="wrap">
<a class="brand" href="{link(up, '')}"><img src="{up}logo.png" alt="" width="46" height="49">The Jolly Makery</a>
<nav class="main" aria-label="Main menu">
{nav}
</nav>
<details class="theme" id="themeBox">
<summary aria-label="Colour theme" title="Colour theme"><svg aria-hidden="true" viewBox="0 0 24 24"><path d="M12 3a9 9 0 1 0 0 18c1.2 0 2-.9 2-2 0-1.3-1-1.6-1-2.6 0-.8.7-1.4 1.6-1.4H17a4 4 0 0 0 4-4c0-4.4-4-8-9-8z"></path><circle cx="7.5" cy="11.5" r="1"></circle><circle cx="10.5" cy="7.5" r="1"></circle><circle cx="15.5" cy="7.8" r="1"></circle></svg><span>Theme</span></summary>
<div class="themelist" role="group" aria-label="Colour theme">
{THEME_BUTTONS}
</div>
</details>
</div></header>
<main>
{body}
</main>
<footer class="site"><div class="wrap">
<div class="stack" style="gap:4px">
<span>The Jolly Makery. Free tools for people who make things.</span>
<nav aria-label="Footer">
<a href="{link(up, 'shop/')}">Shop</a>
<a href="{link(up, 'community/')}">Community</a>
<a href="{link(up, 'feedback/')}">Feedback</a>
<a href="{link(up, 'about/')}">About us</a>
</nav>
</div>
{social}
</div></footer>
<script>
(function(){{
  var BG={{pink:"#F7DDE2",lavender:"#ECE9F8",mint:"#E3F3EC",sky:"#E3EEF8",classic:"#eef0f4",dark:"#141821"}};
  var box=document.getElementById("themeBox"), root=document.documentElement;
  var buttons=box.querySelectorAll("button[data-skin]");
  function show(id){{ if(!BG[id]) id="pink"; if(id==="pink") root.removeAttribute("data-skin"); else root.setAttribute("data-skin",id);
    var m=document.querySelector('meta[name="theme-color"]'); if(m) m.setAttribute("content",BG[id]);
    buttons.forEach(function(b){{ b.setAttribute("aria-pressed", b.dataset.skin===id ? "true" : "false"); }}); }}
  var saved=null; try{{ saved=localStorage.getItem("xs.skin"); }}catch(e){{}}
  show(saved||"pink");
  buttons.forEach(function(b){{ b.addEventListener("click",function(){{ show(b.dataset.skin); try{{ localStorage.setItem("xs.skin",b.dataset.skin); }}catch(e){{}} box.open=false; }}); }});
  document.addEventListener("click",function(e){{ if(box.open && !box.contains(e.target)) box.open=false; }});
  document.addEventListener("keydown",function(e){{ if(e.key==="Escape") box.open=false; }});
  /* On a phone the menu slides sideways: bring the current page's link into view. */
  var nav=document.querySelector("nav.main"), cur=nav&&nav.querySelector('[aria-current="page"]');
  if(cur){{ var left=cur.offsetLeft-nav.offsetLeft, right=left+cur.offsetWidth;
    if(right>nav.clientWidth) nav.scrollLeft=right-nav.clientWidth+12; }}
}})();
</script>
</body>
</html>
"""
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full) or OUT, exist_ok=True)
    open(full, "w").write(html)


HOME = """<section class="band"><div class="wrap hero">
<div class="stack">
<p class="eyebrow">Free tools for people who make things</p>
<h1>Create it. Make it. Enjoy it.</h1>
<p class="lead">Design your own cross stitch pattern, follow it stitch by stitch, and print it when you are ready. No account, no adverts, no cost.</p>
<div class="row">
<a class="btn" href="{UP}stitch/{IDX}">Open the cross stitch tool</a>
<a class="btn ghost" href="{UP}learn/{IDX}">Learn how to start</a>
</div>
</div>
<div><img src="{UP}logo.png" alt="The Jolly Makery logo: an embroidery hoop with stitched roses, a needle and a heart of thread" width="512" height="549"></div>
</div></section>

<section class="band white" id="tools"><div class="wrap stack" style="gap:28px">
<div class="stack" style="gap:8px">
<h2>The tools</h2>
<p class="lead">Two tools are ready today. More crafts will follow.</p>
</div>
<div class="grid">
<article class="card pink">
<span class="tag">Ready</span>
<h3>Cross stitch</h3>
<p class="muted">Draw a pattern, turn a photo into one, or start from 237 example designs. Add lettering and outlines, get a shopping list for thread and fabric, then tick off stitches as you sew.</p>
<a class="btn" href="{UP}stitch/{IDX}">Open tool</a>
</article>
<article class="card">
<span class="tag">Ready</span>
<h3>Thread colour converter</h3>
<p class="muted">Convert a thread number between DMC, Anchor, Madeira, Cosmo and Sullivans, and see the colour big enough to hold your thread against.</p>
<a class="btn" href="{UP}colours/{IDX}">Open tool</a>
</article>
<article class="card soft">
<span class="tag line">Your idea</span>
<h3>What next?</h3>
<p class="muted">We are choosing the next craft to build a tool for. Tell us which one would help you most.</p>
<a class="btn ghost" href="{UP}feedback/{IDX}">Suggest a tool</a>
</article>
</div>
</div></section>

<section class="band"><div class="wrap stack" style="gap:28px">
<h2>How it works</h2>
<ol class="steps grid">
<li class="card"><span class="num">1</span><h3>Create</h3><p class="muted">Pick your fabric and thread colours, then draw your design or start from a photo.</p></li>
<li class="card"><span class="num">2</span><h3>Make</h3><p class="muted">Print the pattern, or follow it on screen and tick off each stitch as you finish it.</p></li>
<li class="card"><span class="num">3</span><h3>Enjoy</h3><p class="muted">Frame it, gift it, or keep it. It is yours, made by you.</p></li>
</ol>
</div></section>

<section class="band white"><div class="wrap stack" style="gap:28px">
<div class="row" style="align-items:flex-end;justify-content:space-between">
<div class="stack" style="gap:8px"><h2>Learning hub</h2><p class="lead">Short guides for beginners and returning makers.</p></div>
<a href="{UP}learn/{IDX}" style="font-weight:700;min-height:44px;display:inline-flex;align-items:center">See all guides</a>
</div>
<div class="grid">
<a class="card soft" href="{UP}learn/{IDX}#chart"><span class="eyebrow">Getting started</span><h3>How to read a cross stitch chart</h3><p class="muted">Squares, symbols and the thread key, explained.</p></a>
<a class="card soft" href="{UP}learn/{IDX}#fabric"><span class="eyebrow">Materials</span><h3>Choosing your fabric count</h3><p class="muted">What 14 count and 18 count mean, and how they change the finished size.</p></a>
<a class="card soft" href="{UP}learn/{IDX}#photo"><span class="eyebrow">Using the tool</span><h3>Turning a photo into a pattern</h3><p class="muted">Which photos work well, and what to tidy up after.</p></a>
</div>
</div></section>

<section class="band"><div class="wrap">
<div class="callout">
<div class="stack" style="gap:8px"><h2>Help us make it better</h2><p>Found a fault? Missing a feature? Tell us what would help you and other makers.</p></div>
<a class="btn light" href="{UP}feedback/{IDX}">Leave feedback</a>
</div>
</div></section>
"""

TOOLS = """<section class="band"><div class="wrap stack" style="gap:28px">
<div class="stack" style="gap:10px">
<h1>Tools</h1>
<p class="lead">Free tools that work on a phone, a tablet or a computer. No account is needed, and your work stays on your own device.</p>
</div>
<div class="grid">
<article class="card">
<span class="tag">Ready</span>
<h2>Cross stitch</h2>
<p class="muted">Design a pattern from a blank fabric, a photo, or one of 237 example designs.</p>
<ul class="muted" style="margin:0;padding-left:1.2rem;display:flex;flex-direction:column;gap:4px">
<li>489 thread shades and six fabric counts</li>
<li>Lettering, outlines and backstitch lines</li>
<li>A shopping list for thread and fabric</li>
<li>Tick off stitches as you sew</li>
<li>Save as an image, or print the pattern</li>
</ul>
<a class="btn" href="{UP}stitch/{IDX}">Open tool</a>
</article>
<article class="card">
<span class="tag">Ready</span>
<h2>Thread colour converter</h2>
<p class="muted">Have a pattern written for one thread brand and a box of another? Find the matching number.</p>
<ul class="muted" style="margin:0;padding-left:1.2rem;display:flex;flex-direction:column;gap:4px">
<li>DMC, Anchor, Madeira, Cosmo and Sullivans</li>
<li>Search by number, or by colour name for DMC</li>
<li>See both colours side by side, or full screen</li>
<li>Browse the whole table, sorted by number or shade</li>
<li>Matches cross-checked, with clear slips removed</li>
</ul>
<a class="btn" href="{UP}colours/{IDX}">Open tool</a>
</article>
<article class="card soft">
<span class="tag line">Your idea</span>
<h2>What next?</h2>
<p class="muted">We are choosing the next craft to build a tool for. Tell us which one would help you most, and what you would want it to do.</p>
<a class="btn ghost" href="{UP}feedback/{IDX}">Suggest a tool</a>
</article>
</div>
</div></section>
"""

def community_body():
    cards = []
    for name, url, what in SOCIAL:
        if url:
            action = '<a class="btn follow" href="%s" rel="noopener">Follow on %s</a>' % (url, name)
            tag = ""
        else:
            action = '<span class="btn follow off">Coming soon</span>'
            tag = ""
        cards.append('<article class="card">%s<h2>%s</h2><p class="muted">%s</p>%s</article>' % (tag, name, what, action))
    return """<section class="band"><div class="wrap stack" style="gap:28px">
<div class="stack" style="gap:10px">
<p class="eyebrow">Community</p>
<h1>Follow the project</h1>
<p class="lead">The Jolly Makery is growing one tool at a time. Follow along to see what is new, share what you have made, and help decide what we build next.</p>
</div>
<div class="grid three">
""" + "\n".join(cards) + """
</div>
<div class="callout">
<div class="stack" style="gap:8px"><h2>Made something with our tools?</h2><p>We would love to see it. Tell us about it, and tell us what would make the tools better.</p></div>
<a class="btn light" href="{UP}feedback/{IDX}">Leave feedback</a>
</div>
</div></section>
"""


SHOP = """<section class="band"><div class="wrap narrow stack" style="gap:24px">
<div class="stack" style="gap:10px">
<span class="tag line">Coming soon</span>
<h1>Shop</h1>
<p class="lead">Our shop is on its way. It will open on Etsy, starting with cross stitch patterns as PDF files that you download and print at home.</p>
</div>
<div class="card stack">
<h2>What to expect</h2>
<ul class="muted" style="margin:0;padding-left:1.2rem;display:flex;flex-direction:column;gap:6px">
<li>Original patterns designed by us, made with our own cross stitch tool</li>
<li>Each pattern as a printable PDF, with a picture of the finished piece, a thread key and clear charts</li>
<li>More kinds of handmade work later</li>
</ul>
</div>
<div class="card soft stack">
<h2>The tools stay free</h2>
<p class="muted">The shop helps to pay for the website. The tools and the example designs inside them remain free for everyone.</p>
<div class="row"><a class="btn" href="{UP}community/{IDX}">Follow us to hear when it opens</a><a class="btn ghost" href="{UP}stitch/{IDX}">Design your own pattern</a></div>
</div>
</div></section>
"""

LEARN = """<section class="band"><div class="wrap narrow stack" style="gap:24px">
<div class="stack" style="gap:10px">
<h1>Learning hub</h1>
<p class="lead">Short guides for beginners and returning makers. More will be added as the tools grow.</p>
<ul style="margin:0;padding-left:1.2rem">
<li><a href="#chart">How to read a cross stitch chart</a></li>
<li><a href="#fabric">Choosing your fabric count</a></li>
<li><a href="#photo">Turning a photo into a pattern</a></li>
</ul>
</div>

<article class="guide" id="chart">
<p class="eyebrow">Getting started</p>
<h2>How to read a cross stitch chart</h2>
<p>A chart is a map of your fabric. Each square on the chart is one stitch, and each square on the fabric is one place to make it.</p>
<ul>
<li><strong>Symbols and colours.</strong> Every square holds a symbol, a colour, or both. Each one stands for one thread shade.</li>
<li><strong>The thread key.</strong> The key lists every symbol beside its thread number, so you know which thread to use.</li>
<li><strong>Heavier grid lines.</strong> A thicker line every ten squares makes counting easier.</li>
<li><strong>Centre marks.</strong> Small arrows on the edges point to the middle of the design.</li>
<li><strong>Lines along the grid.</strong> These are backstitch, a plain running line added at the end for outlines and details.</li>
</ul>
<p>Most stitchers start in the middle. Fold your fabric in half twice to find its centre, find the centre of the chart, and begin there. That way the design sits evenly on the fabric.</p>
<p>One habit makes the finished piece look neat: keep the top arm of every cross slanting the same way.</p>
</article>

<article class="guide" id="fabric">
<p class="eyebrow">Materials</p>
<h2>Choosing your fabric count</h2>
<p>Cross stitch fabric called Aida is woven in small squares. The count is the number of squares, and so stitches, in one inch. A higher count means smaller stitches and a smaller finished piece.</p>
<p>To work out the finished size, divide the number of stitches by the count. The answer is in inches. Multiply by 2.54 for centimetres.</p>
<ul>
<li>A design 70 stitches wide on 14 count is 5 inches wide (12.7 centimetres).</li>
<li>The same design on 18 count is about 3.9 inches wide (9.9 centimetres).</li>
</ul>
<p>14 count is the usual choice for a first project, because the squares are easy to see. Two strands of thread is usual on 14 count.</p>
<p>Buy more fabric than the design needs. Leave a margin on every side for framing, often around 3 inches (7.5 centimetres). The cross stitch tool works out both sizes for you in its shopping list.</p>
</article>

<article class="guide" id="photo">
<p class="eyebrow">Using the tool</p>
<h2>Turning a photo into a pattern</h2>
<p>The cross stitch tool can turn a photo into a chart. Open the Menu and choose Photo to pattern. The photo you pick makes the biggest difference to the result.</p>
<ul>
<li><strong>Choose a clear subject.</strong> One face, one flower or one pet works better than a busy scene.</li>
<li><strong>Look for contrast.</strong> A subject that stands out from a plain background gives cleaner shapes.</li>
<li><strong>Crop close.</strong> Cut away anything you do not want to stitch.</li>
<li><strong>Pick a sensible size.</strong> More stitches keep more detail, and also mean more work.</li>
<li><strong>Keep the colours down.</strong> Fewer thread colours make a pattern that is cheaper to buy for and calmer to sew.</li>
</ul>
<p>Afterwards, use Tidy stray stitches to remove lone single stitches, then touch up any area by hand.</p>
<p>Only use photos you took yourself, or have permission to use.</p>
</article>

<div class="row"><a class="btn" href="{UP}stitch/{IDX}">Open the cross stitch tool</a></div>
</div></section>
"""

ABOUT = """<section class="band"><div class="wrap narrow stack" style="gap:24px">
<h1>About us</h1>
<div class="card stack">
<p>The Jolly Makery is run by two people who like making things. One of us stitches, and makes bracelets and keyrings. The other is an engineer by background, who took on building the tools as a challenge and as a way to learn how the craft world works.</p>
<p>We started with a cross stitch pattern designer, because we wanted one that was simple, free and worked on a phone. A thread colour converter came next, because our own thread box held more than one brand. More tools for other crafts will follow.</p>
<p>Everything here is free to use. There is no account to create and there are no adverts.</p>
</div>
<div class="card soft stack">
<h2>Tell us what you think</h2>
<p class="muted">The best ideas for what to build next come from the people using the tools.</p>
<div class="row"><a class="btn" href="{UP}feedback/{IDX}">Leave feedback</a></div>
</div>
</div></section>
"""

FEEDBACK = """<section class="band"><div class="wrap narrow stack" style="gap:20px">
<div class="stack" style="gap:10px">
<h1>Feedback</h1>
<p class="lead">Tell us what to fix, what to add, and how we can help makers more. Every message is read by the two of us.</p>
</div>
<form class="fb" id="fb">
<fieldset>
<legend>What is your message about?</legend>
<label class="opt"><input type="radio" name="kind" value="An idea for a new feature" checked>An idea for a new feature</label>
<label class="opt"><input type="radio" name="kind" value="Something is not working">Something is not working</label>
<label class="opt"><input type="radio" name="kind" value="A tool for another craft">A tool for another craft</label>
<label class="opt"><input type="radio" name="kind" value="Something else">Something else</label>
</fieldset>
<div class="field"><label for="fbTool">Which part?</label>
<select id="fbTool"><option>Cross stitch tool</option><option>A new tool</option><option>The website</option><option>Not sure</option></select></div>
<div class="field"><label for="fbMsg">Your message</label>
<textarea id="fbMsg" rows="7" placeholder="Tell us in your own words" required></textarea></div>
<button class="btn" type="submit">Send feedback</button>
<p class="small muted">This opens your email app with the message ready to send. Nothing is sent until you press send there. If it does not open, write to <a href="mailto:__EMAIL__">__EMAIL__</a>.</p>
</form>
<div class="card stack"><h2>What happens next</h2><p class="muted">We read every message and add good ideas to our list. Faults get fixed first.</p></div>
</div></section>
<script>
document.getElementById("fb").addEventListener("submit", function (e) {
  e.preventDefault();
  var kind = document.querySelector('input[name="kind"]:checked').value;
  var tool = document.getElementById("fbTool").value;
  var msg = document.getElementById("fbMsg").value.trim();
  if (!msg) { document.getElementById("fbMsg").focus(); return; }
  var subject = "[Website feedback] " + kind + " (" + tool + ")";
  location.href = "mailto:__EMAIL__?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(msg);
});
</script>
""".replace("__EMAIL__", EMAIL)

NOTFOUND = """<section class="band"><div class="wrap narrow stack" style="gap:20px">
<h1>Page not found</h1>
<p class="lead">That page does not exist, or it has moved.</p>
<div class="row"><a class="btn" href="/">Go to the home page</a><a class="btn ghost" href="/stitch/">Open the cross stitch tool</a></div>
</div></section>
"""

os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "site.css"), "w").write(CSS)
page("index.html", "home", "The Jolly Makery: free tools for people who make things",
     "Free craft tools that work on your phone. Design, stitch and print your own cross stitch patterns. No account and no adverts.", HOME)
page("tools/index.html", "tools", "Tools | The Jolly Makery",
     "Free craft tools from The Jolly Makery: a cross stitch pattern designer and a thread colour converter.", TOOLS)
page("learn/index.html", "learn", "Learning hub | The Jolly Makery",
     "Short cross stitch guides: reading a chart, choosing a fabric count, and turning a photo into a pattern.", LEARN)
page("shop/index.html", "shop", "Shop | The Jolly Makery",
     "The Jolly Makery shop is coming soon on Etsy, starting with printable cross stitch patterns.", SHOP)
page("community/index.html", "community", "Community | The Jolly Makery",
     "Follow The Jolly Makery on social media, share what you have made, and help decide what we build next.", community_body())
page("about/index.html", "about", "About us | The Jolly Makery",
     "Who is behind The Jolly Makery and why the tools are free.", ABOUT)
page("feedback/index.html", "feedback", "Feedback | The Jolly Makery",
     "Tell The Jolly Makery what to fix, what to add, and which craft tool to build next.", FEEDBACK)

if MODE == "live":
    # 404 page uses site-root links, since it can be shown at any depth.
    page("404.html", "", "Page not found | The Jolly Makery", "Page not found.", NOTFOUND)
    p = os.path.join(OUT, "404.html")
    h = open(p).read()
    h = h.replace('href="site.css?v=', 'href="/site.css?v=')
    for a in ( 'href="stitch/', 'src="logo.png"', 'href="learn/"', 'href="feedback/"', 'href="about/"', 'href="tools/"', 'href="shop/"', 'href="community/"', 'href="./"', 'href="#tools"'):
        attr, val = a.split('="')
        h = h.replace(a, attr + '="/' + ('"' if val == './"' else val))
    h = h.replace('href="/', 'href="/').replace('href="/"', 'href="/"')
    open(p, "w").write(h)
    # The test copy moved with the tool.
    os.makedirs(os.path.join(OUT, "test"), exist_ok=True)
    open(os.path.join(OUT, "test", "index.html"), "w").write(
        '<!DOCTYPE html>\n<html lang="en-GB"><head><meta charset="utf-8"><meta name="robots" content="noindex">'
        '<meta http-equiv="refresh" content="0; url=../stitch/test/"><title>Moved</title></head>'
        '<body><p>The test copy has moved to <a href="../stitch/test/">stitch/test</a>.</p></body></html>\n')
    # Retires the offline helper that the tool used when it lived at the site root.
    open(os.path.join(OUT, "sw.js"), "w").write(
        '/* The cross stitch tool moved to /stitch/. This retires the offline helper it used at the site root. */\n'
        'self.addEventListener("install", () => self.skipWaiting());\n'
        'self.addEventListener("activate", e => { e.waitUntil((async () => {\n'
        '  const keys = await caches.keys();\n'
        '  await Promise.all(keys.filter(k => k.startsWith("cross-stitch-studio-")).map(k => caches.delete(k)));\n'
        '  await self.registration.unregister();\n'
        '  const pages = await self.clients.matchAll({ type: "window" });\n'
        '  pages.forEach(p => p.navigate(p.url));\n'
        '})()); });\n')
print("built", MODE, "in", OUT)
