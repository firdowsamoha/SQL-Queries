"""HTML/SVG layouts for sheets, mockups, the brand guidelines book and the
presentation board.  Everything is composed from the lockups built in
build.py so the geometry stays identical across assets."""
import base64
import math
from pathlib import Path

from core import (BLACK, BRAND, BRAIN_ANGLES, BRAIN_E, BRAIN_RX, BRAIN_RY, BRAIN_W, C1, C2, GAP,
                  GOLD, HUB, HUB_R, NODE_R, NODES, R, T_LOWER, T_UPPER, TAGLINE, TRACE_W, W,
                  WHITE, brain_points, symbol_raw)

ROOT = Path(__file__).resolve().parents[1]
PW, PH = 1122, 793          # A4 landscape at 96 dpi

GRAY_BG = "#F2F2F1"
GRAY_LINE = "#D9D9D6"
GRAY_TEXT = "#5C5C5C"


def svg_el(inner, bb, w=None, h=None, style=""):
    x, y, bw, bh = bb
    size = (f'width="{w}"' if w else "") + (f' height="{h}"' if h else "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x:.3f} {y:.3f} {bw:.3f} {bh:.3f}" '
            f'{size} style="display:block;{style}">{inner}</svg>')


def uri(rel):
    p = ROOT / rel
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


def srgb_lum(hexc):
    c = [int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = sorted((srgb_lum(a), srgb_lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def cmyk(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    k = 1 - max(r, g, b)
    if k >= 1:
        return (0, 0, 0, 100)
    return tuple(round(100 * v) for v in ((1 - r - k) / (1 - k), (1 - g - k) / (1 - k),
                                          (1 - b - k) / (1 - k), k))


BASE_CSS = """
*{box-sizing:border-box}
html,body{margin:0;font-family:Inter,Arial,sans-serif;color:#0B0B0B;-webkit-font-smoothing:antialiased}
"""


# ---------------------------------------------------------------------------
# Variation board (previews/all-logo-variations.png, 2400x2200)
# ---------------------------------------------------------------------------
def variations_board(bld):
    from build import PREVIEW_BG, SCHEME_LABEL
    tiles = []
    for scheme in ("light", "dark", "gold-s", "black", "white", "gold"):
        bg = PREVIEW_BG[scheme]
        fg = WHITE if bg == BLACK else BLACK
        hz = svg_el(*bld.lock[("horizontal", scheme)], w=560)
        sy = svg_el(*bld.sym[scheme], h=170)
        tiles.append(f'<div class="t" style="background:{bg};color:{fg}"><div class="row">{sy}{hz}</div>'
                     f'<div class="lab">{SCHEME_LABEL[scheme]}</div></div>')
    for scheme in ("light", "dark"):
        bg = PREVIEW_BG[scheme]
        fg = WHITE if bg == BLACK else BLACK
        st = svg_el(*bld.lock[("stacked-tagline", scheme)], h=250)
        pr = svg_el(*bld.lock[("primary", scheme)], w=520)
        tiles.append(f'<div class="t" style="background:{bg};color:{fg}"><div class="row">{st}{pr}</div>'
                     f'<div class="lab">Stacked and primary lockups</div></div>')
    icons = "".join(f'<img src="{uri("icons/png/" + n)}" style="width:{s}px;height:{s}px">'
                    for n, s in (("app-icon-1024.png", 240), ("app-icon-gold-1024.png", 240),
                                 ("app-icon-light-1024.png", 240), ("favicon-64.png", 64),
                                 ("favicon-32.png", 32), ("favicon-16.png", 16)))
    tiles.append(f'<div class="t wide" style="background:{GRAY_BG}"><div class="row">{icons}</div>'
                 f'<div class="lab">App icons and favicon (shown at 64, 32 and 16 px)</div></div>')
    return f"""<html><head><style>{BASE_CSS}
body{{width:2400px;height:2200px;background:{GRAY_BG};padding:60px;display:grid;
grid-template-columns:1fr 1fr;gap:40px;align-content:start}}
.t{{height:380px;border-radius:18px;position:relative;display:flex;align-items:center;justify-content:center;
border:1px solid {GRAY_LINE}}}
.t.wide{{grid-column:span 2;height:420px}}
.row{{display:flex;align-items:center;gap:70px}}
.lab{{position:absolute;left:30px;bottom:22px;font-size:22px;font-weight:500;opacity:.75}}
</style></head><body>{''.join(tiles)}</body></html>"""


# ---------------------------------------------------------------------------
# Business-card helpers
# ---------------------------------------------------------------------------
def _strip(doc):
    return doc.split("\n", 1)[1]


def card_guide(front, back):
    def card(doc, title):
        s = _strip(doc).replace('width="96mm" height="56mm"', 'width="768" height="448"')
        k = 8  # px per mm
        ov = (f'<svg width="768" height="448" style="position:absolute;left:0;top:0">'
              f'<rect x="{3*k}" y="{3*k}" width="{90*k}" height="{50*k}" fill="none" stroke="#E0218A" '
              f'stroke-width="2"/>'
              f'<rect x="{6*k}" y="{6*k}" width="{84*k}" height="{44*k}" fill="none" stroke="#00A3E0" '
              f'stroke-width="2" stroke-dasharray="8 6"/></svg>')
        return (f'<div><div class="h">{title}</div><div style="position:relative;width:768px;height:448px">'
                f'{s}{ov}</div></div>')
    return f"""<html><head><style>{BASE_CSS}
body{{width:1800px;height:760px;background:#fff;padding:50px 60px}}
.cards{{display:flex;gap:120px}} .h{{font-weight:700;font-size:22px;margin-bottom:14px}}
.leg{{margin-top:34px;display:flex;gap:48px;font-size:19px;color:{GRAY_TEXT}}}
.sw{{display:inline-block;width:28px;height:0;border-top:3px solid;vertical-align:middle;margin-right:10px}}
</style></head><body><div class="cards">{card(front, "Front")}{card(back, "Back")}</div>
<div class="leg"><span><b style="color:#0B0B0B">Document 96 × 50 mm</b> → 96 × 56 mm incl. 3 mm bleed on every side</span>
<span><i class="sw" style="border-color:#E0218A"></i>Trim 90 × 50 mm</span>
<span><i class="sw" style="border-color:#00A3E0;border-top-style:dashed"></i>Safe area 84 × 44 mm (3 mm inside trim)</span></div>
<div class="leg" style="margin-top:10px">Guide colours are for this sheet only and never print. Backgrounds extend to the bleed edge;
keep all text and the QR code inside the safe area.</div></body></html>""".replace(
        "Document 96 × 50 mm</b> → 96 × 56 mm", "Document 96 × 56 mm</b> (90 × 50 mm card")


def card_mockup(front, back):
    def trimmed(doc):
        return (_strip(doc).replace('viewBox="0 0 96 56"', 'viewBox="3 3 90 50"')
                .replace('width="96mm" height="56mm"', 'width="900" height="500"'))
    return f"""<html><head><style>{BASE_CSS}
body{{width:2400px;height:1600px;overflow:hidden;
background:radial-gradient(ellipse at 40% 35%,#F4F3F0 0%,#E4E2DD 55%,#D3D0CA 100%)}}
.c{{position:absolute;width:900px;height:500px;border-radius:5px;overflow:hidden}}
.c svg{{display:block}}
.c::after{{content:"";position:absolute;inset:0;
background:linear-gradient(135deg,rgba(255,255,255,.10) 0%,rgba(255,255,255,0) 45%,rgba(0,0,0,.05) 100%)}}
.back{{left:330px;top:300px;transform:rotate(-9deg);
box-shadow:0 2px 3px rgba(0,0,0,.18),0 30px 60px rgba(40,35,25,.22),0 60px 120px rgba(40,35,25,.18)}}
.front{{left:1130px;top:700px;transform:rotate(6deg);
box-shadow:0 2px 3px rgba(0,0,0,.25),0 34px 70px rgba(40,35,25,.28),0 70px 140px rgba(40,35,25,.2)}}
</style></head><body><div class="c back">{trimmed(back)}</div><div class="c front">{trimmed(front)}</div></body></html>"""


def email_signature(logo_url, logo_w):
    f = "font-family:Inter,Arial,Helvetica,sans-serif"
    return f"""<!-- {BRAND} email signature. Host email-signature-logo.png on your website and
     replace the src below with its absolute https URL before pasting into your mail client. -->
<table cellpadding="0" cellspacing="0" border="0" style="{f};color:{BLACK};border-collapse:collapse">
  <tr>
    <td style="padding:0 18px 0 0;vertical-align:top;border-right:2px solid {GOLD}">
      <img src="{logo_url}" width="{logo_w}" height="72" alt="{BRAND}" style="display:block;border:0">
    </td>
    <td style="padding:0 0 0 18px;vertical-align:top">
      <div style="font-size:16px;font-weight:700;line-height:20px">[Full Name]</div>
      <div style="font-size:13px;font-weight:500;line-height:18px">[Job Title] &middot; {BRAND}</div>
      <div style="font-size:12px;line-height:18px;padding-top:8px">
        <span style="color:{GOLD};font-weight:700">E</span>&nbsp; [Email Address] &nbsp;&nbsp;
        <span style="color:{GOLD};font-weight:700">T</span>&nbsp; [Phone Number]<br>
        <span style="color:{GOLD};font-weight:700">W</span>&nbsp; [Website URL]
      </div>
      <div style="font-size:11px;font-weight:500;line-height:16px;padding-top:6px">{TAGLINE}</div>
    </td>
  </tr>
</table>
"""


# ---------------------------------------------------------------------------
# Construction sheet (SVG, 1600 x 1000)
# ---------------------------------------------------------------------------
def _p(c, r, a):
    return (c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))


def construction_svg(bld):
    k, tx, ty = 4.0, -10, 0
    hl = 0.3                                  # hairline in raw units
    F = 'font-family="Inter, Arial, sans-serif"'
    g = []
    for x in range(24, 209, 8):
        g.append(f'<line x1="{x}" y1="8" x2="{x}" y2="240" stroke="#ECECEA" stroke-width="{hl}"/>')
    for y in range(8, 241, 8):
        g.append(f'<line x1="24" y1="{y}" x2="208" y2="{y}" stroke="#ECECEA" stroke-width="{hl}"/>')
    g.append(symbol_raw(BLACK, GOLD))
    dash = f'stroke-dasharray="{4*hl} {3*hl}"'
    for c in (C1, C2):
        g.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="{R}" fill="none" stroke="#8A8A8A" '
                 f'stroke-width="{hl}" {dash}/>')
        for rr in (R - W / 2, R + W / 2):
            g.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="{rr}" fill="none" stroke="#B5B5B5" '
                     f'stroke-width="{hl}"/>')
        g.append(f'<path d="M{c[0]-4} {c[1]}H{c[0]+4}M{c[0]} {c[1]-4}V{c[1]+4}" stroke="#E0218A" '
                 f'stroke-width="{hl*2}"/>')
    g.append(f'<ellipse cx="{BRAIN_E[0]}" cy="{BRAIN_E[1]}" rx="{BRAIN_RX}" ry="{BRAIN_RY}" fill="none" '
             f'stroke="#00A3E0" stroke-width="{hl}" {dash}/>')
    for x, y in brain_points():
        g.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="1.3" fill="#00A3E0"/>')
    for c, a in ((C1, T_UPPER), (C2, T_LOWER)):
        e = _p(c, R + W / 2 + 12, a)
        g.append(f'<line x1="{c[0]}" y1="{c[1]}" x2="{e[0]:.2f}" y2="{e[1]:.2f}" stroke="#E0218A" '
                 f'stroke-width="{hl}"/>')
    # X dimension across the upper bowl's left stroke, on the horizontal diameter
    y = C1[1]
    x0, x1 = C1[0] - R - W / 2, C1[0] - R + W / 2
    g.append(f'<path d="M{x0} {y-4}V{y+4}M{x1} {y-4}V{y+4}M{x0} {y}H{x1}" stroke="#E0218A" '
             f'stroke-width="{hl*2}" fill="none"/>')
    labels = [
        (x0 + W / 2, y - 3, "X", "middle", 6),
        (C1[0] + 3, C1[1] - 3, "C1", "start", 3.4),
        (C2[0] + 3, C2[1] - 3, "C2", "start", 3.4),
        (_p(C1, R + W / 2 + 14, T_UPPER)[0], _p(C1, R + W / 2 + 14, T_UPPER)[1], f"{T_UPPER}°", "start", 3.4),
        (_p(C2, R + W / 2 + 16, T_LOWER)[0], _p(C2, R + W / 2 + 16, T_LOWER)[1], f"{T_LOWER}°", "end", 3.4),
        (BRAIN_E[0] + BRAIN_RX + 8, BRAIN_E[1] + 30, "brain ellipse", "start", 3.4),
    ]
    for lx, ly, txt, anc, size in labels:
        fill = "#FFFFFF" if txt == "X" else "#0B0B0B"
        g.append(f'<text x="{lx:.2f}" y="{ly:.2f}" {F} font-size="{size}" font-weight="600" '
                 f'text-anchor="{anc}" fill="{fill}">{txt}</text>')
    art = f'<g transform="translate({tx} {ty}) scale({k})">{"".join(g)}</g>'

    bh = bld.b.bbox[3]
    x_pct = W / bh * 100
    rows = [
        ("Grid", f"8-unit module. The symbol is {bld.b.bbox[2]:.1f} × {bld.b.bbox[3]:.1f} units "
                 f"(ratio 1 : {bld.b.bbox[3] / bld.b.bbox[2]:.2f})."),
        ("X", f"S stroke width = 32 units = {x_pct:.1f}% of symbol height. X is the master measure."),
        ("Letter S", f"Two tangent circles C1 / C2, centreline radius {R} (1.31 X), meeting on the spine."),
        ("Terminals", f"Upper terminal cut at {T_UPPER}° so the tip ends inside the brain; "
                      f"lower terminal at {T_LOWER}°."),
        ("AI brain", f"Six lobes (arcs) on a {BRAIN_RX:.0f} × {BRAIN_RY:.0f} ellipse, contour "
                     f"{BRAIN_W} units (0.34 X)."),
        ("Interlock", f"The front lobe arches over the S head, the S tip runs under the brain, the last "
                      f"lobe tucks under the spine. Gap at every crossing: {GAP} units."),
        ("Circuit", f"Traces {TRACE_W} units (0.2 X) radiate from a hub Ø{2*HUB_R:.0f} at C1 to three "
                    f"nodes Ø{2*NODE_R:.0f}: one forward, two at 45°."),
        ("Colour", "S #0B0B0B · brain, traces and nodes #D4AF37. Solid fills only."),
    ]
    ty0 = 240
    txt = [f'<text x="900" y="120" {F} font-size="22" font-weight="600" letter-spacing="3" '
           f'fill="{GOLD}">LOGO CONSTRUCTION</text>',
           f'<text x="900" y="180" {F} font-size="46" font-weight="700" fill="{BLACK}" '
           f'letter-spacing="-1">S + AI Brain symbol</text>']
    for i, (h, body) in enumerate(rows):
        y = ty0 + i * 82
        txt.append(f'<text x="900" y="{y}" {F} font-size="20" font-weight="700" fill="{BLACK}">{h}</text>')
        words, line, lines = body.split(), "", []
        for w_ in words:
            if len(line) + len(w_) > 54:
                lines.append(line)
                line = w_
            else:
                line = (line + " " + w_).strip()
        lines.append(line)
        for j, ln in enumerate(lines):
            txt.append(f'<text x="1040" y="{y + j*26}" {F} font-size="18" fill="{GRAY_TEXT}">{ln}</text>')
    legend = (f'<g {F} font-size="16" fill="{GRAY_TEXT}">'
              f'<line x1="900" y1="912" x2="930" y2="912" stroke="#E0218A" stroke-width="2"/>'
              f'<text x="940" y="918">centres, angles, X</text>'
              f'<line x1="1110" y1="912" x2="1140" y2="912" stroke="#00A3E0" stroke-width="2" stroke-dasharray="5 4"/>'
              f'<text x="1150" y="918">brain ellipse + lobe joints</text>'
              f'<line x1="1380" y1="912" x2="1410" y2="912" stroke="#8A8A8A" stroke-width="2" stroke-dasharray="5 4"/>'
              f'<text x="1420" y="918">centreline</text></g>')
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000">\n'
            f'<title>{BRAND} logo construction sheet</title>\n'
            f'<rect width="1600" height="1000" fill="#FFFFFF"/>\n{art}\n{"".join(txt)}\n{legend}\n</svg>\n')


# ---------------------------------------------------------------------------
# Brand guidelines book
# ---------------------------------------------------------------------------
BOOK_CSS = BASE_CSS + f"""
@page{{size:297mm 210mm;margin:0}}
.page{{width:{PW}px;height:{PH}px;position:relative;overflow:hidden;page-break-after:always;
padding:64px 72px;background:#fff}}
.page.dark{{background:{BLACK};color:#fff}}
.eyebrow{{font-size:12px;font-weight:600;letter-spacing:.22em;color:{GOLD};text-transform:uppercase}}
h1{{font-size:40px;line-height:1.1;letter-spacing:-.02em;margin:10px 0 18px;font-weight:700}}
h3{{font-size:15px;margin:0 0 6px;font-weight:700}}
p,li{{font-size:13.5px;line-height:1.6;color:{GRAY_TEXT};margin:0 0 10px}}
.dark p{{color:#CFCFCF}}
.foot{{position:absolute;left:72px;right:72px;bottom:30px;display:flex;justify-content:space-between;
font-size:10.5px;color:#8A8A8A;letter-spacing:.04em}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}
.grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}}
.tile{{border:1px solid {GRAY_LINE};border-radius:12px;display:flex;align-items:center;justify-content:center;
position:relative}}
.tile .cap{{position:absolute;left:14px;bottom:10px;font-size:11px;font-weight:500;color:#8A8A8A}}
.tile.k{{background:{BLACK};border-color:{BLACK}}}
.tile.g{{background:{GRAY_BG};border-color:{GRAY_BG}}}
table.spec{{border-collapse:collapse;width:100%;font-size:13px}}
table.spec td{{padding:7px 12px 7px 0;border-bottom:1px solid #ECECEA;vertical-align:top}}
table.spec td:first-child{{color:#8A8A8A;width:38%}}
.x{{position:absolute;right:10px;top:8px;width:22px;height:22px;border-radius:50%;background:{BLACK};
color:#fff;font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center}}
"""


class Guidelines:
    def __init__(self, bld):
        self.bld = bld
        self.n = 0
        self.total = 0

    def lock(self, kind, scheme, **kw):
        return svg_el(*self.bld.lock[(kind, scheme)], **kw)

    def sym(self, scheme, **kw):
        return svg_el(*self.bld.sym[scheme], **kw)

    def page(self, body, eyebrow="", dark=False, title=None):
        self.n += 1
        foot = (f'<div class="foot"><span>{BRAND} · Brand Guidelines</span>'
                f'<span>{eyebrow}</span><span>{self.n:02d}</span></div>')
        return f'<section class="page{" dark" if dark else ""}">{body}{foot}</section>'

    # -- pages --------------------------------------------------------------
    def p_cover(self):
        return (f'<section class="page dark" style="display:flex;flex-direction:column;justify-content:center;'
                f'align-items:center;gap:40px">{self.lock("stacked-tagline", "dark", h=300)}'
                f'<div style="position:absolute;bottom:40px;font-size:12px;letter-spacing:.24em;color:{GOLD};'
                f'font-weight:600">BRAND GUIDELINES · VERSION 1.0</div></section>')

    def p_overview(self):
        return self.page(f"""
<div class="eyebrow">01 · Brand overview</div><h1>Turn your data into<br>smarter decisions.</h1>
<div class="grid2" style="margin-top:26px;gap:56px">
<div><p>{BRAND} is an AI-powered data analytics platform that helps people analyse datasets, generate
insights, understand patterns, create visualisations and make smarter decisions.</p>
<p>The identity is deliberately restrained: one symbol, two colours and one typeface. Black carries
structure and authority; gold marks intelligence and the moments that matter.</p>
<h3 style="margin-top:22px">Personality</h3>
<p>Intelligent · Precise · Clear · Premium · Trustworthy</p>
<h3 style="margin-top:14px">The identity system</h3>
<p>Symbol — the S + AI Brain mark<br>Wordmark — Smart Analysis in Inter Bold<br>
Palette — Primary Black #0B0B0B and Premium Gold #D4AF37<br>Typeface — Inter</p></div>
<div class="tile" style="height:430px">{self.lock("primary", "light", w=420)}</div></div>""", "Overview")

    def p_symbol(self):
        return self.page(f"""
<div class="eyebrow">02 · The symbol</div><h1>One letter. One mind.</h1>
<div class="grid2" style="gap:56px;margin-top:20px">
<div class="tile" style="height:500px">{self.sym("light", h=380)}</div>
<div><p>The mark combines exactly two elements: the letter <b style="color:#0B0B0B">S</b> and an
<b style="color:#0B0B0B">AI brain</b>.</p>
<p>The S and the brain are woven into one form. The brain's front lobe arches over the head of the S,
the S's tip cuts under the brain's edge into its interior, and the brain's last lobe tucks back under the
S at the spine. Neither element can be lifted out without the other — the S's upper bowl is the brain.</p>
<p>From the centre of that bowl a hub sends three circuit traces to three nodes: data entering the
brand (the S) and leaving as structured reasoning (the brain).</p>
<h3 style="margin-top:20px">What it communicates</h3>
<p>Artificial intelligence — the brain and its circuit<br>Data analysis — signals branching from a single source<br>
Clarity and precision — geometric circles, consistent strokes, solid colour</p>
<h3 style="margin-top:20px">Never add</h3>
<p>Additional letters, arrows, charts, sparkles, robot heads, gradients or 3D effects.</p></div></div>""",
                         "Symbol")

    def p_construction(self):
        return self.page(f"""
<div class="eyebrow">03 · Construction</div><h1 style="margin-bottom:8px">Built on circles and a single measure.</h1>
<img src="{uri("guidelines/logo-construction-sheet.png")}" style="width:100%;margin-top:4px">""",
                         "Construction")

    def p_lockups(self):
        return self.page(f"""
<div class="eyebrow">04 · Logo versions</div><h1>Four layouts, one geometry.</h1>
<div style="display:grid;grid-template-columns:1.5fr 1fr;grid-template-rows:250px 250px;gap:20px">
<div class="tile">{self.lock("primary", "light", w=470)}<span class="cap">A · Primary logo — symbol, wordmark and tagline</span></div>
<div class="tile">{self.lock("stacked", "light", h=170)}<span class="cap">C · Stacked</span></div>
<div class="tile">{self.lock("horizontal", "light", w=430)}<span class="cap">B · Horizontal</span></div>
<div class="tile">{self.sym("light", h=170)}<span class="cap">D · Symbol only</span></div></div>
<p style="margin-top:16px">Use the primary logo where there is room for the tagline; the horizontal logo for headers and
navigation; the stacked logo for square or centred formats; the symbol alone once the brand is established
(app icons, avatars, favicons). The tagline is optional and is dropped below 200 px / 50 mm logo width.</p>""",
                         "Logo versions")

    def p_colorways(self):
        t = []
        for scheme, cls, cap in (("light", "", "G · Light background — black + gold"),
                                 ("dark", "k", "H · Dark background — white + gold"),
                                 ("gold-s", "", "Gold S with black AI brain"),
                                 ("black", "", "I · Monochrome black"),
                                 ("white", "k", "J · Monochrome white"),
                                 ("gold", "k", "Monochrome gold — foil and premium print")):
            t.append(f'<div class="tile {cls}" style="height:190px">'
                     f'{self.lock("horizontal", scheme, w=300)}<span class="cap">{cap}</span></div>')
        return self.page(f"""
<div class="eyebrow">05 · Colour versions</div><h1>Black and gold, nothing else.</h1>
<div class="grid3">{''.join(t)}</div>
<p style="margin-top:18px">The black-and-gold logo on white is the default. On black, switch the black elements to white
and keep the gold. Use single-colour versions where only one ink is available — documents, engraving,
embossing, foil, fax or one-colour print.</p>""", "Colour versions")

    def p_clearspace(self):
        bld = self.bld
        inner, bb = bld.lock[("horizontal", "light")]
        X = 25.0                                  # 1/4 symbol height
        x, y, w, h = bb
        vb = (x - X, y - X, w + 2 * X, h + 2 * X)
        guide = (f'<rect x="{x-X}" y="{y-X}" width="{w+2*X}" height="{h+2*X}" fill="#FBF6E6" '
                 f'stroke="{GOLD}" stroke-width="0.8" stroke-dasharray="3 2"/>'
                 f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#B5B5B5" stroke-width="0.6"/>')
        marks = "".join(
            f'<rect x="{mx}" y="{my}" width="{X}" height="{X}" fill="none" stroke="{GOLD}" stroke-width="0.8"/>'
            f'<text x="{mx+X/2}" y="{my+X/2+4}" font-family="Inter" font-size="11" font-weight="700" '
            f'text-anchor="middle" fill="{GOLD}">X</text>'
            for mx, my in ((x - X, y - X), (x + w, y + h)))
        svg = svg_el(guide + inner + marks, vb, w=470)
        sym_x = (0, 0, bld.b.symbol_width(100), 100)
        mini = svg_el(f'<rect x="0" y="0" width="{sym_x[2]}" height="25" fill="#FBF6E6"/>'
                      + bld.sym["light"][0], sym_x, h=110)
        return self.page(f"""
<div class="eyebrow">06 · Clear space and minimum size</div><h1>Give the logo room to think.</h1>
<div class="grid2" style="gap:48px;grid-template-columns:1.35fr 1fr">
<div><div class="tile" style="height:300px">{svg}</div>
<div style="display:flex;gap:24px;margin-top:20px;align-items:center">{mini}
<p style="margin:0"><b style="color:#0B0B0B">X = ¼ of the symbol height.</b> Keep at least X of clear
space on every side of every logo version. No text, image edge or other graphic may enter this zone.
Within a lockup, symbol and wordmark spacing is fixed — never adjust it.</p></div></div>
<div><h3>Minimum sizes</h3>
<table class="spec">
<tr><td>Primary (with tagline)</td><td>200 px / 50 mm wide</td></tr>
<tr><td>Horizontal</td><td>120 px / 30 mm wide</td></tr>
<tr><td>Stacked</td><td>64 px / 18 mm tall</td></tr>
<tr><td>Symbol</td><td>24 px / 7 mm tall</td></tr>
<tr><td>Below 24 px</td><td>Use the simplified favicon symbol</td></tr></table>
<h3 style="margin-top:22px">Backgrounds</h3>
<p>Light logo on white, transparent or very light neutral grey. Dark logo on Primary Black or
very dark imagery. On mid-tone or busy backgrounds use a solid black or white container.</p>
<h3 style="margin-top:14px">Placement</h3>
<p>Prefer the top-left or centre. Align the logo to the layout grid by the outer edge of the symbol,
not by the wordmark.</p></div></div>""", "Clear space")

    def p_misuse(self):
        hz, bb = self.bld.lock[("horizontal", "light")]

        def tile(inner_svg, cap, cls=""):
            return (f'<div class="tile {cls}" style="height:158px;overflow:hidden">{inner_svg}'
                    f'<span class="x">✕</span><span class="cap">{cap}</span></div>')
        x, y, w, h = bb
        recolor = hz.replace(GOLD, "#8A8A8A")
        rearranged_sym = self.bld.sym["light"]
        wordmark = hz.split('<g class="wordmark">')[1]
        tiles = [
            tile(svg_el(hz, bb, w=200, style="transform:scaleX(1.45) scaleY(.8)"), "Do not stretch or distort"),
            tile(svg_el(hz, bb, w=260, style="transform:rotate(-14deg)"), "Do not rotate"),
            tile(svg_el(recolor, bb, w=280), "Do not recolour"),
            tile(svg_el(hz, bb, w=280, style="filter:drop-shadow(6px 8px 6px rgba(0,0,0,.45))"),
                 "Do not add shadows, glows or 3D"),
            tile(svg_el('<g class="wordmark">' + wordmark + f'<g transform="translate({w+20} 0)">'
                        + rearranged_sym[0] + '</g>', (x + 100, y, w + 20, h), w=280),
                 "Do not rearrange the elements"),
            tile(svg_el(hz, bb, w=280), "Do not place on low-contrast or busy backgrounds",
                 cls="").replace('class="tile "', 'class="tile" style="background:repeating-linear-gradient('
                                 '45deg,#C9C9C6 0 14px,#8A8A8A 14px 28px);height:158px;overflow:hidden"'),
            tile(svg_el(hz.replace(f'fill="{BLACK}"', 'fill="none" stroke="#0B0B0B" stroke-width="1.2"')
                        .replace(f'fill="{GOLD}"', f'fill="none" stroke="{GOLD}" stroke-width="1.2"'), bb, w=280),
                 "Do not outline the wordmark"),
            tile(svg_el(hz.replace('<g class="symbol"', '<g class="symbol" opacity="0"'), bb, w=280),
                 "Do not use the wordmark without the symbol"),
            tile(f'<div style="display:flex;align-items:center;gap:14px">{self.sym("light", h=90)}'
                 f'<span style="font-family:Georgia,serif;font-style:italic;font-size:34px">Smart Analysis</span></div>',
                 "Do not change the typeface"),
        ]
        return self.page(f"""
<div class="eyebrow">07 · Misuse</div><h1>Protect the mark.</h1>
<div class="grid3" style="gap:16px">{''.join(tiles)}</div>""", "Misuse")

    def p_color(self):
        def card(name, hexc, fg, rows, cls=""):
            r_ = "".join(f'<tr><td style="color:{fg};opacity:.7">{a}</td><td style="color:{fg}">{b}</td></tr>'
                         for a, b in rows)
            return (f'<div style="background:{hexc};border-radius:14px;padding:28px;height:330px;'
                    f'display:flex;flex-direction:column;justify-content:space-between;{cls}">'
                    f'<div style="color:{fg};font-size:24px;font-weight:700">{name}</div>'
                    f'<table class="spec" style="font-size:13.5px">{r_}</table></div>')
        kc, gc = cmyk(BLACK), cmyk(GOLD)
        black = card("Primary Black", BLACK, "#fff", [
            ("HEX", BLACK), ("RGB", "11 · 11 · 11"),
            ("CMYK (rich black)", "60 · 40 · 40 · 100"),
            ("CMYK (text / small)", f"{kc[0]} · {kc[1]} · {kc[2]} · {kc[3]}"),
            ("Pantone", "Black 6 C (closest)")])
        gold = card("Premium Gold", GOLD, BLACK, [
            ("HEX", GOLD), ("RGB", "212 · 175 · 55"),
            ("CMYK", f"{gc[0]} · {gc[1]} · {gc[2]} · {gc[3]}"),
            ("Pantone (metallic)", "871 C — or gold foil"),
            ("Pantone (solid)", "7562 C (closest; proof before print)")])
        cr = [("Black on white", contrast(BLACK, WHITE), "All text sizes"),
              ("Gold on black", contrast(GOLD, BLACK), "All text sizes"),
              ("Gold on white", contrast(GOLD, WHITE), "Logo and large display only — never body text")]
        cr_rows = "".join(f'<tr><td>{a}</td><td><b style="color:#0B0B0B">{v:.1f} : 1</b></td><td>{u}</td></tr>'
                          for a, v, u in cr)
        return self.page(f"""
<div class="eyebrow">08 · Colour palette</div><h1>A strict two-colour palette.</h1>
<div style="display:grid;grid-template-columns:1fr 1fr 0.55fr;gap:20px">{black}{gold}
<div style="display:flex;flex-direction:column;gap:12px">
<div style="flex:1;border:1px solid {GRAY_LINE};border-radius:14px;padding:16px;font-size:12.5px">
<b>White</b><br><span style="color:#8A8A8A">#FFFFFF · backgrounds, reversed type</span></div>
<div style="flex:1;background:{GRAY_BG};border-radius:14px;padding:16px;font-size:12.5px">
<b>Neutral grey</b><br><span style="color:#8A8A8A">#F2F2F1 · preview backgrounds only</span></div>
<div style="flex:1.2;border-radius:14px;padding:16px;font-size:12.5px;background:{BLACK};color:#fff">
<b>Proportion</b><div style="display:flex;height:16px;margin-top:10px;border-radius:4px;overflow:hidden">
<i style="flex:60;background:#fff"></i><i style="flex:30;background:#3A3A3A"></i><i style="flex:10;background:{GOLD}"></i></div>
<span style="color:#CFCFCF">≈ 60 white/space · 30 black · 10 gold</span></div></div></div>
<div class="grid2" style="margin-top:22px;gap:40px">
<div><h3>Contrast (WCAG 2.x)</h3><table class="spec" style="white-space:nowrap">{cr_rows}</table></div>
<div><h3>Rules</h3><p>Black is structure: type, the S, backgrounds. Gold is meaning: the AI brain, the word
<i>Analysis</i>, a single highlight or rule per layout. Never introduce blue, green, purple, red or any other
accent. Master artwork uses flat fills; metallic gold is reserved for physical finishes and presentation mockups.</p></div></div>""",
                         "Colour")

    def p_type(self):
        specimen = "".join(
            f'<div style="display:flex;align-items:baseline;gap:20px;border-bottom:1px solid #ECECEA;padding:10px 0">'
            f'<span style="width:150px;font-size:12px;color:#8A8A8A">{lab}</span>'
            f'<span style="font-size:{s}px;font-weight:{wgt};letter-spacing:{ls};color:{c}">{txt}</span></div>'
            for lab, s, wgt, ls, c, txt in (
                ("Display · Bold 700", 44, 700, "-0.02em", BLACK, "Smarter decisions"),
                ("Heading · Bold 700", 28, 700, "-0.01em", BLACK, "Understand every pattern"),
                ("Subhead · Medium 500", 19, 500, "0", BLACK, TAGLINE),
                ("Body · Regular 400", 14.5, 400, "0", BLACK,
                 "Analyse datasets, generate insights and visualise results in seconds."),
                ("Label · SemiBold 600", 12, 600, "0.2em", GOLD, "AI-POWERED ANALYTICS")))
        return self.page(f"""
<div class="eyebrow">09 · Typography</div><h1>Inter, and only Inter.</h1>
<div class="grid2" style="grid-template-columns:1.25fr 1fr;gap:48px">
<div><div style="font-size:120px;font-weight:700;letter-spacing:-.03em;line-height:1">Aa<span style="color:{GOLD}">Gg</span></div>
<div style="font-size:15px;letter-spacing:.02em;margin:14px 0 18px;color:{GRAY_TEXT}">ABCDEFGHIJKLMNOPQRSTUVWXYZ<br>
abcdefghijklmnopqrstuvwxyz<br>0123456789 · % € $ → ( ) / @ &amp;</div>{specimen}</div>
<div><h3>Wordmark</h3><table class="spec">
<tr><td>Smart</td><td>Inter Bold, black (white on dark)</td></tr>
<tr><td>Analysis</td><td>Inter Bold, Premium Gold</td></tr>
<tr><td>Tracking</td><td>−1.5% (−15 / 1000 em)</td></tr>
<tr><td>Tagline</td><td>Inter Medium, +1% tracking</td></tr>
<tr><td>Case</td><td>Title case, as shown — never all caps</td></tr></table>
<h3 style="margin-top:20px">Usage</h3><table class="spec">
<tr><td>Headlines</td><td>Bold 700, −1 to −2% tracking</td></tr>
<tr><td>Subheads</td><td>Medium 500 or SemiBold 600</td></tr>
<tr><td>Body</td><td>Regular 400, 140–160% leading</td></tr>
<tr><td>Labels</td><td>SemiBold 600, uppercase, +15–20%</td></tr>
<tr><td>Fallback</td><td>Arial / Helvetica (email, Office)</td></tr></table>
<p style="margin-top:14px">Inter is free under the SIL Open Font License — rsms.me/inter. The logo files use outlined
type and need no font installed.</p></div></div>""", "Typography")

    def p_icons(self):
        imgs = "".join(
            f'<div style="text-align:center"><img src="{uri("icons/png/" + f)}" style="width:{s}px;height:{s}px;'
            f'display:block;margin:0 auto 10px"><span style="font-size:11px;color:#8A8A8A">{c}</span></div>'
            for f, s, c in (("app-icon-1024.png", 190, "App icon · primary"),
                            ("app-icon-gold-1024.png", 190, "App icon · gold"),
                            ("app-icon-light-1024.png", 190, "App icon · light")))
        fav = "".join(f'<img src="{uri("icons/png/favicon-" + str(p) + ".png")}" style="width:{p}px;height:{p}px">'
                      for p in (64, 32, 16))
        return self.page(f"""
<div class="eyebrow">10 · App icon and favicon</div><h1>Simplified for small sizes.</h1>
<div style="display:flex;gap:46px;align-items:flex-end;margin-top:10px">{imgs}
<div class="tile g" style="width:220px;height:190px;gap:22px;align-items:center">{fav}</div></div>
<div class="grid2" style="margin-top:34px;gap:40px">
<div><h3>Simplified symbol</h3><p>Below 24 px and inside icon containers the symbol uses heavier strokes (S 36,
brain 15 units), four lobes and a single circuit trace. Same silhouette, same colours — fewer details.</p></div>
<div><h3>Containers</h3><p>Rounded square, corner radius 22.37% of the side (iOS superellipse approximation).
The symbol fills 62% of the container height and is optically centred. A full-bleed square master is supplied
for platforms that apply their own mask.</p></div></div>""", "Icons")

    def p_card(self):
        return self.page(f"""
<div class="eyebrow">11 · Business card</div><h1>90 × 50 mm, double-sided.</h1>
<div class="grid2" style="grid-template-columns:1.3fr 1fr;gap:36px">
<img src="{uri("business-card/business-card-mockup.png")}" style="width:100%;border-radius:12px">
<div><table class="spec">
<tr><td>Trim size</td><td>90 × 50 mm</td></tr><tr><td>Bleed</td><td>3 mm each side (96 × 56 mm)</td></tr>
<tr><td>Safe area</td><td>3 mm inside trim (84 × 44 mm)</td></tr>
<tr><td>Front</td><td>Stacked logo + tagline, white + gold on black</td></tr>
<tr><td>Back</td><td>Name, title, contact, QR code</td></tr>
<tr><td>Stock</td><td>400–600 gsm uncoated or soft-touch</td></tr>
<tr><td>Finish (optional)</td><td>Gold foil for the AI brain and “Analysis”</td></tr>
<tr><td>Black</td><td>Rich black 60/40/40/100 for the front flood</td></tr></table>
<p style="margin-top:14px">Name: Inter Bold 10 pt · Title: Inter Medium 6.5 pt · Contact: Inter Regular 6 pt.
All text is live and editable in business-card-back.svg.</p></div></div>""", "Business card")

    def p_templates(self):
        return self.page(f"""
<div class="eyebrow">12 · Digital applications</div><h1>Consistent everywhere.</h1>
<div style="display:grid;grid-template-columns:1fr 1fr 0.62fr;gap:18px;align-items:start">
<div><img src="{uri("templates/presentation/title-slide.png")}" style="width:100%;border-radius:8px;border:1px solid {GRAY_LINE}">
<p style="font-size:11px;margin-top:6px">Presentation title slide · 16:9</p>
<img src="{uri("templates/social/linkedin-cover.png")}" style="width:100%;border-radius:6px;margin-top:6px">
<p style="font-size:11px;margin-top:6px">LinkedIn cover · 1128 × 191</p></div>
<div><img src="{uri("templates/social/product-announcement-template.png")}" style="width:100%;border-radius:8px;border:1px solid {GRAY_LINE}">
<p style="font-size:11px;margin-top:6px">Product announcement · 1200 × 675</p>
<img src="{uri("templates/email-signature/email-signature-preview.png")}" style="width:100%;border:1px solid {GRAY_LINE};border-radius:6px">
<p style="font-size:11px;margin-top:6px">Email signature · HTML</p></div>
<div><img src="{uri("templates/social/social-post-template.png")}" style="width:100%;border-radius:8px">
<p style="font-size:11px;margin-top:6px">Social post · 1080 × 1080</p>
<img src="{uri("templates/social/social-profile-icon.png")}" style="width:46%;border-radius:50%">
<p style="font-size:11px;margin-top:6px">Profile icon (circle-safe)</p></div></div>""", "Applications")

    def p_stationery(self):
        return self.page(f"""
<div class="eyebrow">13 · Stationery</div><h1>Letterhead.</h1>
<div class="grid2" style="grid-template-columns:0.62fr 1fr;gap:48px">
<img src="{uri("templates/stationery/letterhead-a4-preview.png")}" style="width:100%;box-shadow:0 10px 40px rgba(0,0,0,.14)">
<div><table class="spec"><tr><td>Format</td><td>A4, 210 × 297 mm</td></tr>
<tr><td>Margins</td><td>20 mm left and right</td></tr>
<tr><td>Logo</td><td>Horizontal, 12 mm tall, top left</td></tr>
<tr><td>Rule</td><td>Premium Gold, 0.4 mm</td></tr>
<tr><td>Body</td><td>Inter Regular 10 pt / 15 pt</td></tr>
<tr><td>Footer</td><td>Inter 7.5 pt, black</td></tr></table>
<p style="margin-top:14px">Edit letterhead-a4.svg in Illustrator, Figma or Inkscape, or print the PDF and
use it as a pre-printed sheet.</p></div></div>""", "Stationery")

    def p_files(self):
        return self.page(f"""
<div class="eyebrow">14 · Files</div><h1>Asset index.</h1>
<div class="grid3" style="gap:30px">
<div><h3>logos/</h3><p>svg/ and png/ for primary, horizontal, stacked, stacked-tagline and symbol in light,
dark, gold-s, mono-black, mono-white and mono-gold.</p>
<h3>icons/</h3><p>App icons (3 colourways + full-bleed), favicon.svg, favicon.ico, PNG sizes 16–1024,
apple-touch-icon.</p></div>
<div><h3>guidelines/</h3><p>This book, construction sheet, usage and spacing guide, misuse, colour palette and
typography sheets (PNG + PDF).</p><h3>business-card/</h3><p>Front/back SVG sources, print-ready PDF with bleed,
600 dpi previews, bleed and safe-area guide, mockup.</p></div>
<div><h3>templates/</h3><p>Website logos, social profile icon, LinkedIn logo and cover, social post, product
announcement, email signature, presentation title slide, A4 letterhead.</p>
<h3>source/</h3><p>build.py regenerates everything from the master geometry. Run with --website URL to
encode a real QR code on the business card.</p></div></div>
<div style="position:absolute;right:72px;bottom:80px">{self.lock("horizontal", "light", w=240)}</div>""", "Files")

    def all_pages(self):
        self.n = 0
        return [self.p_cover(), self.p_overview(), self.p_symbol(), self.p_construction(),
                self.p_lockups(), self.p_colorways(), self.p_clearspace(), self.p_misuse(),
                self.p_color(), self.p_type(), self.p_icons(), self.p_card(), self.p_templates(),
                self.p_stationery(), self.p_files()]

    def document(self):
        return f'<html><head><style>{BOOK_CSS}</style></head><body>{"".join(self.all_pages())}</body></html>'

    def single(self, page_html):
        return f'<html><head><style>{BOOK_CSS}</style></head><body>{page_html}</body></html>'


# ---------------------------------------------------------------------------
# Presentation board (3200 x 2000)
# ---------------------------------------------------------------------------
def presentation_board(bld):
    L = lambda k, s, **kw: svg_el(*bld.lock[(k, s)], **kw)
    S = lambda s, **kw: svg_el(*bld.sym[s], **kw)
    return f"""<html><head><style>{BASE_CSS}
body{{width:3200px;height:2000px;background:{GRAY_BG};padding:70px;display:grid;gap:36px;
grid-template-columns:1.25fr 1fr 1fr;grid-template-rows:1fr 0.82fr 0.82fr}}
.c{{border-radius:22px;overflow:hidden;position:relative;display:flex;align-items:center;justify-content:center;background:#fff}}
.k{{background:{BLACK}}} .cap{{position:absolute;left:28px;bottom:22px;font-size:20px;font-weight:500;color:#8A8A8A}}
img{{display:block}}
</style></head><body>
<div class="c k" style="grid-row:span 2;flex-direction:column;gap:70px">{L("stacked-tagline", "dark", h=520)}</div>
<div class="c" style="grid-column:span 2">{L("primary", "light", w=1300)}</div>
<div class="c" style="gap:60px">{S("light", h=330)}{S("gold-s", h=330)}<span class="cap">Symbol · black + gold / gold + black</span></div>
<div class="c" style="background:transparent;align-items:stretch;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:20px">
<div class="c" style="background:{BLACK};flex-direction:column;align-items:flex-start;padding:30px;justify-content:space-between;color:#fff">
<b style="font-size:32px">Primary Black</b><span style="font-size:24px;opacity:.8">#0B0B0B</span></div>
<div class="c" style="background:{GOLD};flex-direction:column;align-items:flex-start;padding:30px;justify-content:space-between">
<b style="font-size:32px">Premium Gold</b><span style="font-size:24px">#D4AF37</span></div>
<div class="c" style="grid-column:span 2;flex-direction:column;align-items:flex-start;padding:30px 36px;justify-content:center">
<div style="font-size:84px;font-weight:700;letter-spacing:-.03em;line-height:1">Inter <span style="color:{GOLD}">Aa</span></div>
<div style="font-size:24px;color:{GRAY_TEXT};margin-top:12px">Bold · Medium · Regular</div></div></div>
<div class="c" style="padding:0"><img src="{uri("business-card/business-card-mockup.png")}" style="width:100%;height:100%;object-fit:cover"></div>
<div class="c" style="gap:50px">
<img src="{uri("icons/png/app-icon-1024.png")}" style="width:250px"><img src="{uri("icons/png/app-icon-gold-1024.png")}" style="width:250px">
<div style="display:flex;flex-direction:column;gap:24px;align-items:center">
<img src="{uri("icons/png/favicon-64.png")}" style="width:64px"><img src="{uri("icons/png/favicon-32.png")}" style="width:32px">
<img src="{uri("icons/png/favicon-16.png")}" style="width:16px"></div><span class="cap">App icon · favicon</span></div>
<div class="c k" style="padding:0"><img src="{uri("templates/presentation/title-slide.png")}" style="width:100%"></div>
</body></html>"""
