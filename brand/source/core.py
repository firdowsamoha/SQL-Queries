"""Smart Analysis brand core: master symbol geometry, Inter-to-path wordmark,
lockup composition and a headless-Chromium renderer for PNG/PDF export."""
import io
import math
from functools import lru_cache
from pathlib import Path

from PIL import Image

BLACK = "#0B0B0B"
GOLD = "#D4AF37"
WHITE = "#FFFFFF"

BRAND = "Smart Analysis"
TAGLINE = "Turn Your Data Into Smarter Decisions"

FONT_DIR = Path("/usr/share/fonts/opentype/inter")
FONTS = {
    "bold": FONT_DIR / "Inter-Bold.otf",
    "semibold": FONT_DIR / "Inter-SemiBold.otf",
    "medium": FONT_DIR / "Inter-Medium.otf",
    "regular": FONT_DIR / "Inter-Regular.otf",
}
# output folders, numbered so the package reads in order
DIRS = {
    "logos": "01-logos",
    "icons": "02-app-icons-and-favicon",
    "colors": "03-brand-colors",
    "typography": "04-typography",
    "business-card": "05-business-cards",
    "guidelines": "06-brand-guidelines",
    "templates": "07-templates",
    "previews": "08-previews",
}
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# ---------------------------------------------------------------------------
# Master symbol geometry (symbol units, before normalisation)
#
#   The S is two tangent circles (C1 upper, C2 lower) of radius R, stroked at
#   width W, with its upper terminal cut at -45deg.  The AI brain is a
#   scalloped ellipse contour wrapped around the S's upper bowl, and the two
#   are woven together: the brain's front lobe rises from inside the bowl and
#   arches OVER the head of the S,
#   the S's tip then runs UNDER the brain into its interior, and the brain's
#   last lobe tucks back UNDER the S at the spine.  A knockout gap (GAP)
#   separates every crossing.  Circuit traces radiate from a hub at the
#   centre of the upper bowl to three nodes inside the brain.
# ---------------------------------------------------------------------------
W = 32                     # S stroke width  ("X" in the guidelines)
R = 42                     # bowl centreline radius
C1 = (100.0, 82.0)
C2 = (100.0, 82.0 + 2 * R)
T_UPPER = -45              # upper terminal angle (tip sits inside the brain)
T_LOWER = 142              # lower terminal angle
BRAIN_E = (128.0, 74.0)    # brain ellipse centre
BRAIN_RX, BRAIN_RY = 56.0, 54.0
BRAIN_START = (80.0, 58.0) # front lobe rises from inside the upper bowl
BRAIN_ANGLES = [-100, -62, -24, 14, 52, 86]
BRAIN_OVER = 1             # number of front lobes drawn over the S
BRAIN_BULGE = 0.62
BRAIN_W = 11               # brain contour stroke
GAP = 5                    # knockout gap at every crossing
TRACE_W = 6.5              # circuit trace stroke
HUB = (100.0, 82.0)
NODES = [(142.0, 64.0), (142.0, 100.0), (152.0, 82.0)]
HUB_R, NODE_R = 8.5, 6.5

# simplified geometry for app icon / favicon (heavier strokes, fewer parts)
SIMPLE = dict(W=36, brain_w=15, brain_angles=[-96, -48, 0, 46, 86], over=1, gap=6,
              trace_w=9, nodes=[(152.0, 82.0)], hub_r=10, node_r=9)


def _pt(c, r, a):
    a = math.radians(a)
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def _f(p):
    return f"{p[0]:.2f} {p[1]:.2f}"


def s_path():
    a, b, c = _pt(C1, R, T_UPPER), _pt(C1, R, 90), _pt(C2, R, T_LOWER)
    return f"M{_f(a)} A{R} {R} 0 1 0 {_f(b)} A{R} {R} 0 1 1 {_f(c)}"


def s_lower_path():
    """Lower bowl only: the one stretch of the S the brain passes under."""
    b, c = _pt(C1, R, 90), _pt(C2, R, T_LOWER)
    return f"M{_f(b)} A{R} {R} 0 1 1 {_f(c)}"


def brain_points(angles=BRAIN_ANGLES):
    return [BRAIN_START] + [(BRAIN_E[0] + BRAIN_RX * math.cos(math.radians(a)),
                             BRAIN_E[1] + BRAIN_RY * math.sin(math.radians(a))) for a in angles]


def brain_path(pts):
    d = f"M{_f(pts[0])}"
    for p, q in zip(pts, pts[1:]):
        r = math.dist(p, q) * BRAIN_BULGE
        d += f" A{r:.2f} {r:.2f} 0 0 1 {_f(q)}"
    return d


def symbol_raw(s_color, brain_color, simple=False):
    """Symbol elements in raw geometry space.  The over/under weave is built
    with two luminance masks (userSpaceOnUse), which Illustrator imports as
    opacity masks and Figma as masks; all shapes stay true vectors."""
    if simple:
        g = SIMPLE
        traces = f"M{_f(HUB)} H{g['nodes'][0][0]:.2f}"
        nodes, hub_r, node_r = g["nodes"], g["hub_r"], g["node_r"]
        w, bw, tw, angles, over, gap = (g["W"], g["brain_w"], g["trace_w"], g["brain_angles"],
                                        g["over"], g["gap"])
    else:
        j = 124.0
        traces = (f"M{_f(HUB)} H{j} L140 66 M{j} {HUB[1]} L140 98 "
                  f"M{j} {HUB[1]} H150")
        nodes, hub_r, node_r = NODES, HUB_R, NODE_R
        w, bw, tw, angles, over, gap = W, BRAIN_W, TRACE_W, BRAIN_ANGLES, BRAIN_OVER, GAP
    pts = brain_points(angles)
    front = brain_path(pts[:over + 1])           # lobe arching over the head of the S
    back = brain_path(pts[over:])                # lobes behind, tucking under the spine
    s = s_path()
    k = "sa-s" if simple else "sa"
    box = 'maskUnits="userSpaceOnUse" x="-60" y="-60" width="400" height="400"'
    full = '<rect x="-60" y="-60" width="400" height="400" fill="#fff"/>'
    out = [
        f'<defs><mask id="{k}-under-s" {box}>{full}<path d="{s_lower_path()}" fill="none" stroke="#000" '
        f'stroke-width="{w + 2 * gap}"/></mask>'
        f'<mask id="{k}-under-brain" {box}>{full}<path d="{front}" fill="none" stroke="#000" '
        f'stroke-width="{bw + 2 * gap}" stroke-linecap="round"/></mask></defs>',
        f'<path id="brain-back" d="{back}" fill="none" stroke="{brain_color}" stroke-width="{bw}" '
        f'stroke-linecap="round" stroke-linejoin="round" mask="url(#{k}-under-s)"/>',
        f'<path id="letter-s" d="{s}" fill="none" stroke="{s_color}" stroke-width="{w}" '
        f'mask="url(#{k}-under-brain)"/>',
        f'<path id="brain-front" d="{front}" fill="none" stroke="{brain_color}" stroke-width="{bw}" '
        f'stroke-linecap="round" stroke-linejoin="round"/>',
        f'<path id="circuit-traces" d="{traces}" fill="none" stroke="{brain_color}" '
        f'stroke-width="{tw}" stroke-linecap="round" stroke-linejoin="round"/>',
        f'<circle cx="{HUB[0]}" cy="{HUB[1]}" r="{hub_r}" fill="{brain_color}"/>',
    ]
    out += [f'<circle cx="{x}" cy="{y}" r="{node_r}" fill="{brain_color}"/>' for x, y in nodes]
    return "\n".join(out)


# Colour schemes ------------------------------------------------------------
# keys: s, brain, smart, analysis, tagline
SCHEMES = {
    "light": dict(s=BLACK, brain=GOLD, smart=BLACK, analysis=GOLD, tagline=BLACK),
    "dark": dict(s=WHITE, brain=GOLD, smart=WHITE, analysis=GOLD, tagline=WHITE),
    "gold-s": dict(s=GOLD, brain=BLACK, smart=BLACK, analysis=GOLD, tagline=BLACK),
    "black": dict(s=BLACK, brain=BLACK, smart=BLACK, analysis=BLACK, tagline=BLACK),
    "white": dict(s=WHITE, brain=WHITE, smart=WHITE, analysis=WHITE, tagline=WHITE),
    "gold": dict(s=GOLD, brain=GOLD, smart=GOLD, analysis=GOLD, tagline=GOLD),
}


# ---------------------------------------------------------------------------
# Text to outlines (HarfBuzz shaping + fontTools outlines, kerning applied)
# ---------------------------------------------------------------------------
@lru_cache(None)
def _font(weight):
    import uharfbuzz as hb
    from fontTools.ttLib import TTFont
    path = str(FONTS[weight])
    tt = TTFont(path)
    face = hb.Face(hb.Blob.from_file_path(path))
    return tt, hb.Font(face), tt["head"].unitsPerEm


def font_metrics(weight="bold"):
    tt, _, upm = _font(weight)
    os2 = tt["OS/2"]
    return dict(cap=os2.sCapHeight / upm, x=os2.sxHeight / upm,
                asc=os2.sTypoAscender / upm, desc=-os2.sTypoDescender / upm)


def text_path(text, weight, size, x=0.0, y=0.0, tracking=0.0):
    """Return (svg path d, advance width) for text with baseline at y."""
    import uharfbuzz as hb
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    tt, font, upm = _font(weight)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})
    order = tt.getGlyphOrder()
    gs = tt.getGlyphSet()
    s = size / upm
    pen_x = x
    parts = []
    n = len(buf.glyph_infos)
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        name = order[info.codepoint]
        sp = SVGPathPen(gs, lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
        gx = pen_x + pos.x_offset * s
        gy = y - pos.y_offset * s
        gs[name].draw(TransformPen(sp, (s, 0, 0, -s, gx, gy)))
        if sp.getCommands():
            parts.append(sp.getCommands())
        pen_x += pos.x_advance * s + (tracking * size if i < n - 1 else 0)
    return " ".join(parts), pen_x - x


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------
class Renderer:
    def __enter__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(executable_path=CHROME)
        return self

    def __exit__(self, *a):
        self.browser.close()
        self._pw.stop()

    def page(self, w, h, scale=1):
        return self.browser.new_page(viewport={"width": int(w), "height": int(h)},
                                     device_scale_factor=scale)

    def html_png(self, html, out, w, h, scale=1, transparent=False):
        pg = self.page(w, h, scale)
        pg.set_content(html)
        pg.evaluate("document.fonts.ready")
        data = pg.screenshot(path=str(out) if out else None, omit_background=transparent,
                             full_page=False)
        pg.close()
        return data

    def svg_png(self, svg, out, w, h, transparent=True, bg=None):
        body_bg = bg or "transparent"
        html = (f'<html><head><style>html,body{{margin:0;background:{body_bg}}}'
                f'svg{{display:block;width:{w}px;height:{h}px}}</style></head>'
                f'<body>{svg}</body></html>')
        return self.html_png(html, out, w, h, transparent=transparent and bg is None)

    def html_pdf(self, html, out, width, height):
        pg = self.page(1200, 800)
        pg.set_content(html)
        pg.evaluate("document.fonts.ready")
        pg.pdf(path=str(out), width=width, height=height, print_background=True,
               margin=dict(top="0", right="0", bottom="0", left="0"),
               prefer_css_page_size=True)
        pg.close()

    def measure(self, inner, vb, scale=8):
        """Tight bounding box (including strokes) of SVG content, in user units."""
        x, y, w, h = vb
        pw, ph = int(w * scale), int(h * scale)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" '
               f'width="{pw}" height="{ph}">{inner}</svg>')
        png = self.svg_png(svg, None, pw, ph)
        bb = Image.open(io.BytesIO(png)).getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        l, t, r, b = bb
        return (x + l / scale, y + t / scale, (r - l) / scale, (b - t) / scale)


# ---------------------------------------------------------------------------
# Normalised symbol + lockups
# ---------------------------------------------------------------------------
class Brand:
    """Holds measured symbol bounds and builds every lockup from them."""

    def __init__(self, renderer):
        self.r = renderer
        self.bbox = renderer.measure(symbol_raw(BLACK, GOLD), (0, 0, 260, 260))
        self.bbox_simple = renderer.measure(symbol_raw(BLACK, GOLD, True), (0, 0, 260, 260))

    # symbol normalised to height h with top-left at (x, y)
    def symbol(self, scheme="light", x=0, y=0, h=100, simple=False):
        c = SCHEMES[scheme] if isinstance(scheme, str) else scheme
        bx, by, bw, bh = self.bbox_simple if simple else self.bbox
        k = h / bh
        return (f'<g class="symbol" transform="translate({x:.3f} {y:.3f}) scale({k:.5f}) '
                f'translate({-bx:.3f} {-by:.3f})">\n{symbol_raw(c["s"], c["brain"], simple)}\n</g>')

    def symbol_width(self, h=100, simple=False):
        bx, by, bw, bh = self.bbox_simple if simple else self.bbox
        return bw * h / bh

    def wordmark(self, scheme, x, baseline, size, tracking=-0.015):
        c = SCHEMES[scheme]
        d1, w1 = text_path("Smart", "bold", size, x, baseline, tracking)
        _, wsp = text_path("Smart ", "bold", size, 0, 0, tracking)
        d2, w2 = text_path("Analysis", "bold", size, x + wsp + tracking * size, baseline, tracking)
        total = wsp + tracking * size + w2
        svg = (f'<g class="wordmark"><path id="smart" d="{d1}" fill="{c["smart"]}"/>'
               f'<path id="analysis" d="{d2}" fill="{c["analysis"]}"/></g>')
        return svg, total

    def tagline(self, scheme, x, baseline, size, anchor="start", tracking=0.0):
        c = SCHEMES[scheme]
        _, w = text_path(TAGLINE, "medium", size, 0, 0, tracking)
        if anchor == "middle":
            x -= w / 2
        d, _ = text_path(TAGLINE, "medium", size, x, baseline, tracking)
        return f'<path id="tagline" d="{d}" fill="{c["tagline"]}"/>', w

    def lockup(self, kind, scheme="light"):
        """kind: horizontal | primary (horizontal + tagline) | stacked |
        stacked-tagline. Returns inner svg in a coordinate system where the
        symbol is 100 units tall."""
        H = 100
        cap = font_metrics()["cap"]
        sw = self.symbol_width(H)
        parts = [self.symbol(scheme, 0, 0, H)]
        if kind in ("horizontal", "primary"):
            size = 54
            gap = 0.30 * H
            if kind == "horizontal":
                base = H / 2 + cap * size / 2
            else:
                tsize = 16.5
                block = cap * size + 0.62 * size + cap * tsize
                top = H / 2 - block / 2
                base = top + cap * size
            wm, _ = self.wordmark(scheme, sw + gap, base, size)
            parts.append(wm)
            if kind == "primary":
                tl, _ = self.tagline(scheme, sw + gap + 2, base + 0.62 * size + cap * tsize, tsize,
                                     tracking=0.01)
                parts.append(tl)
        else:
            size = 46
            _, ww = self.wordmark(scheme, 0, 0, size)
            cx = sw / 2
            base = H + 0.42 * H + cap * size
            wm, _ = self.wordmark(scheme, cx - ww / 2, base, size)
            parts.append(wm)
            if kind == "stacked-tagline":
                tl, _ = self.tagline(scheme, cx, base + 0.75 * size, 14.5, anchor="middle",
                                     tracking=0.01)
                parts.append(tl)
        inner = "\n".join(parts)
        bb = self.r.measure(inner, (-400, -50, 1200, 500), scale=4)
        return inner, bb


def svg_doc(inner, bb, title, pad=0.0, width=None, height=None, bg=None, desc=None):
    x, y, w, h = bb
    x, y, w, h = x - pad, y - pad, w + 2 * pad, h + 2 * pad
    attrs = ""
    if width:
        attrs += f' width="{width}"'
    if height:
        attrs += f' height="{height}"'
    bgr = f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{bg}"/>' if bg else ""
    d = f"<desc>{desc}</desc>" if desc else ""
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x:.3f} {y:.3f} {w:.3f} {h:.3f}"{attrs}>\n'
            f'<title>{title}</title>{d}\n{bgr}{inner}\n</svg>\n')
