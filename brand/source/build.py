"""Build the complete Smart Analysis brand package.

    python3 brand/source/build.py [--website https://example.com]

Requires: playwright (Chromium), fonttools, uharfbuzz, Pillow, qrcode, and the
Inter font family installed (fc-list | grep Inter).  Every asset in brand/ is
regenerated from the master geometry in core.py.
"""
import argparse
import base64
import shutil
from pathlib import Path

from PIL import Image

from core import (BLACK, BRAND, GOLD, TAGLINE, WHITE, Brand, Renderer, svg_doc,
                  font_metrics)
import pages

ROOT = Path(__file__).resolve().parents[1]
OUT = {k: ROOT / k for k in ("logos", "icons", "previews", "guidelines",
                             "business-card", "templates")}

KINDS = ["primary", "horizontal", "stacked", "stacked-tagline"]
SCHEMES = {           # scheme key -> file suffix
    "light": "light",
    "dark": "dark",
    "gold-s": "gold-s",
    "black": "mono-black",
    "white": "mono-white",
    "gold": "mono-gold",
}
SCHEME_LABEL = {
    "light": "Black + gold, for light backgrounds",
    "dark": "White + gold, for dark backgrounds",
    "gold-s": "Gold S with black AI brain",
    "black": "Monochrome black",
    "white": "Monochrome white, for dark backgrounds",
    "gold": "Monochrome gold",
}
PREVIEW_BG = {"light": "#FFFFFF", "dark": BLACK, "gold-s": "#FFFFFF", "black": "#FFFFFF",
              "white": BLACK, "gold": BLACK}


def place(inner, bb, x, y, w=None, h=None):
    """Fit content with bounding box bb into a box at (x, y) of width w or height h."""
    bx, by, bw, bh = bb
    k = (w / bw) if w else (h / bh)
    return (f'<g transform="translate({x:.3f} {y:.3f}) scale({k:.5f}) '
            f'translate({-bx:.3f} {-by:.3f})">{inner}</g>'), bw * k, bh * k


def inline_svg(doc):
    return doc.split("\n", 1)[1] if doc.startswith("<?xml") else doc


def data_uri(path):
    mime = "image/png" if str(path).endswith(".png") else "image/svg+xml"
    return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


class Builder:
    def __init__(self, r, website=None):
        self.r = r
        self.b = Brand(r)
        self.website = website
        self.lock = {}       # (kind, scheme) -> (inner, bb)
        self.sym = {}        # scheme -> (inner, bb)

    # ------------------------------------------------------------------ logos
    def logos(self):
        b = self.b
        for scheme, suf in SCHEMES.items():
            sw = b.symbol_width(100)
            inner = b.symbol(scheme, 0, 0, 100)
            bb = (0, 0, sw, 100)
            self.sym[scheme] = (inner, bb)
            doc = svg_doc(inner, bb, f"{BRAND} symbol ({SCHEME_LABEL[scheme]})")
            p = write(OUT["logos"] / "svg" / f"smart-analysis-symbol-{suf}.svg", doc)
            self.r.svg_png(inline_svg(doc), OUT["logos"] / "png" / p.with_suffix(".png").name,
                           round(1600 * sw / 100), 1600)
            for kind in KINDS:
                inner, bb = b.lockup(kind, scheme)
                self.lock[(kind, scheme)] = (inner, bb)
                doc = svg_doc(inner, bb, f"{BRAND} {kind} logo ({SCHEME_LABEL[scheme]})")
                p = write(OUT["logos"] / "svg" / f"smart-analysis-{kind}-{suf}.svg", doc)
                w = 3000 if kind in ("primary", "horizontal") else 2000
                self.r.svg_png(inline_svg(doc), OUT["logos"] / "png" / p.with_suffix(".png").name,
                               w, round(w * bb[3] / bb[2]))
        # JPG copies (no transparency): flattened onto the background each colourway is made for
        for png in sorted((OUT["logos"] / "png").glob("*.png")):
            scheme = next(k for k, v in SCHEMES.items() if png.stem.endswith("-" + v))
            im = Image.open(png).convert("RGBA")
            pad = round(0.12 * min(im.size))
            bg = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), PREVIEW_BG[scheme])
            bg.alpha_composite(im, (pad, pad))
            out = OUT["logos"] / "jpg" / png.with_suffix(".jpg").name
            out.parent.mkdir(parents=True, exist_ok=True)
            bg.convert("RGB").save(out, quality=95, subsampling=0)
        # website logo (horizontal, no tagline) at fixed display heights
        for scheme in ("light", "dark"):
            inner, bb = self.lock[("horizontal", scheme)]
            doc = svg_doc(inner, bb, f"{BRAND} website logo", height=48)
            write(OUT["templates"] / "website" / f"website-logo-{scheme}.svg", doc)
            for hpx, tag in ((48, "@1x"), (96, "@2x")):
                self.r.svg_png(inline_svg(doc), OUT["templates"] / "website" /
                               f"website-logo-{scheme}{tag}.png", round(hpx * bb[2] / bb[3]), hpx)

    # ------------------------------------------------------------------ icons
    def app_icon_svg(self, size, container, scheme, radius=0.2237, simple=True, frac=0.62):
        b = self.b
        h = size * frac
        w = b.symbol_width(h, simple)
        sym = b.symbol(scheme, (size - w) / 2, (size - h) / 2, h, simple)
        rx = size * radius
        return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">\n'
                f'<title>{BRAND} app icon</title>\n'
                f'<rect width="{size}" height="{size}" rx="{rx:.2f}" fill="{container}"/>\n{sym}\n</svg>\n')

    def icons(self):
        d = OUT["icons"]
        variants = {
            "app-icon": (BLACK, "dark"),
            "app-icon-gold": (GOLD, "black"),
            "app-icon-light": (WHITE, "light"),
        }
        for name, (fill, scheme) in variants.items():
            doc = self.app_icon_svg(1024, fill, scheme)
            write(d / f"{name}.svg", doc)
            for px in (1024, 512, 192):
                self.r.svg_png(inline_svg(doc), d / "png" / f"{name}-{px}.png", px, px)
        # full-bleed square for iOS / stores (platform applies its own mask)
        doc = self.app_icon_svg(1024, BLACK, "dark", radius=0)
        write(d / "app-icon-square.svg", doc)
        self.r.svg_png(inline_svg(doc), d / "png" / "app-icon-square-1024.png", 1024, 1024)
        self.r.svg_png(inline_svg(doc), d / "png" / "apple-touch-icon-180.png", 180, 180)

        # favicon: simplified symbol in a black rounded tile, legible on light and dark tabs
        fav = self.app_icon_svg(64, BLACK, "dark", radius=0.22, frac=0.74)
        write(d / "favicon.svg", fav)
        favt_h = 64
        w = self.b.symbol_width(favt_h, True)
        favt = svg_doc(self.b.symbol("light", 0, 0, favt_h, True), (0, 0, w, favt_h),
                       f"{BRAND} favicon (transparent)")
        write(d / "favicon-transparent.svg", favt)
        imgs = []
        for px in (16, 32, 48, 64, 256):
            p = d / "png" / f"favicon-{px}.png"
            self.r.svg_png(inline_svg(fav), p, px, px)
            imgs.append(p)
        ico = Image.open(d / "png" / "favicon-256.png")
        ico.save(d / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

    # ------------------------------------------------------------- previews
    def previews(self):
        d = OUT["previews"]
        for scheme in ("light", "dark"):
            inner, bb = self.lock[("primary", scheme)]
            bg = PREVIEW_BG[scheme]
            svg = inline_svg(svg_doc(inner, bb, "preview", width=1500))
            html = (f'<body style="margin:0;background:{bg};display:flex;align-items:center;'
                    f'justify-content:center;width:2400px;height:1350px">{svg}</body>')
            self.r.html_png(html, d / f"primary-logo-{scheme}-preview.png", 2400, 1350)
        self.r.html_png(pages.variations_board(self), d / "all-logo-variations.png", 2400, 2200)

    # -------------------------------------------------------- business card
    def qr(self, x, y, size):
        if not self.website:
            c = size / 2
            return (f'<g id="qr-placeholder"><rect x="{x}" y="{y}" width="{size}" height="{size}" '
                    f'fill="none" stroke="{BLACK}" stroke-width="0.2" stroke-dasharray="0.8 0.6"/>'
                    f'<text x="{x + c}" y="{y + c - 0.6}" font-family="Inter, Arial, sans-serif" '
                    f'font-size="2" font-weight="600" text-anchor="middle" fill="{BLACK}">QR CODE</text>'
                    f'<text x="{x + c}" y="{y + c + 2.2}" font-family="Inter, Arial, sans-serif" '
                    f'font-size="1.5" text-anchor="middle" fill="{BLACK}">[Website URL]</text></g>')
        import qrcode
        q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_M)
        q.add_data(self.website)
        q.make(fit=True)
        m = q.get_matrix()
        n = len(m)
        k = size / n
        cells = "".join(f"M{x + j * k:.3f} {y + i * k:.3f}h{k:.3f}v{k:.3f}h{-k:.3f}z"
                        for i, row in enumerate(m) for j, v in enumerate(row) if v)
        return f'<path id="qr-code" d="{cells}" fill="{BLACK}"/>'

    def card_front(self):
        inner, bb = self.lock[("stacked-tagline", "dark")]
        g, w, h = place(inner, bb, 0, 0, h=27)
        g, w, h = place(inner, bb, 48 - w / 2, 28 - h / 2, h=27)
        return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="96mm" height="56mm" viewBox="0 0 96 56">\n'
                f'<title>{BRAND} business card - front (90x50 mm + 3 mm bleed)</title>\n'
                f'<rect id="background-bleed" width="96" height="56" fill="{BLACK}"/>\n'
                f'<g id="logo">{g}</g>\n</svg>\n')

    def card_back(self):
        sym, sbb = self.sym["light"]
        g, w, h = place(sym, sbb, 9, 9, h=10)
        F = 'font-family="Inter, Arial, sans-serif"'

        def t(y, txt, size, weight=400, fill=BLACK, x=9, extra=""):
            return (f'<text x="{x}" y="{y}" {F} font-size="{size}" font-weight="{weight}" '
                    f'fill="{fill}"{extra}>{txt}</text>')
        contact = [("E", "[Email Address]"), ("T", "[Phone Number]"), ("W", "[Website URL]")]
        rows = "".join(
            t(38.6 + i * 3.7, lab, 2.15, 700, GOLD) + t(38.6 + i * 3.7, val, 2.15, 400, BLACK, x=13)
            for i, (lab, val) in enumerate(contact))
        return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="96mm" height="56mm" viewBox="0 0 96 56">\n'
                f'<title>{BRAND} business card - back (90x50 mm + 3 mm bleed)</title>\n'
                f'<rect id="background-bleed" width="96" height="56" fill="{WHITE}"/>\n'
                f'<g id="symbol">{g}</g>\n'
                f'<g id="details">\n'
                f'{t(26.2, "[Full Name]", 3.5, 700)}\n'
                f'{t(30.2, "[Job Title]", 2.3, 500)}\n'
                f'<rect id="gold-rule" x="9" y="32.4" width="9" height="0.45" fill="{GOLD}"/>\n'
                f'{rows}\n</g>\n'
                f'{self.qr(72, 31, 15)}\n'
                f'</svg>\n')

    def business_card(self):
        d = OUT["business-card"]
        front, back = self.card_front(), self.card_back()
        write(d / "business-card-front.svg", front)
        write(d / "business-card-back.svg", back)
        # print PDF (vector, editable text, 96x56 mm incl. 3 mm bleed)
        html = ('<html><head><style>@page{size:96mm 56mm;margin:0}html,body{margin:0}'
                '.p{width:96mm;height:56mm;page-break-after:always;overflow:hidden}'
                '.p svg{display:block;width:96mm;height:56mm}</style></head><body>'
                f'<div class="p">{inline_svg(front)}</div><div class="p">{inline_svg(back)}</div>'
                '</body></html>')
        self.r.html_pdf(html, d / "business-card-print.pdf", "96mm", "56mm")
        # 600 dpi previews: with bleed and trimmed
        px_mm = 600 / 25.4
        for name, doc in (("front", front), ("back", back)):
            self.r.svg_png(inline_svg(doc), d / f"business-card-{name}-with-bleed.png",
                           round(96 * px_mm), round(56 * px_mm))
            trimmed = doc.replace('viewBox="0 0 96 56"', 'viewBox="3 3 90 50"') \
                         .replace('width="96mm" height="56mm"', 'width="90mm" height="50mm"')
            self.r.svg_png(inline_svg(trimmed), d / f"business-card-{name}.png",
                           round(90 * px_mm), round(50 * px_mm))
        self.r.html_png(pages.card_guide(front, back), d / "business-card-bleed-safe-guide.png",
                        1800, 760, scale=2)
        self.r.html_png(pages.card_mockup(front, back), d / "business-card-mockup.png",
                        2400, 1600)

    # ------------------------------------------------------------ templates
    def templates(self):
        d = OUT["templates"]
        F = 'font-family="Inter, Arial, sans-serif"'
        b = self.b

        # social / profile icons
        for name, size in (("social-profile-icon", 1080), ("linkedin-company-logo", 400)):
            sym, sbb = self.sym["dark"]
            g, w, h = place(sym, sbb, 0, 0, h=size * 0.56)
            g, _, _ = place(sym, sbb, (size - w) / 2, (size - h) / 2, h=size * 0.56)
            doc = (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" '
                   f'viewBox="0 0 {size} {size}"><title>{BRAND} {name}</title>'
                   f'<rect width="{size}" height="{size}" fill="{BLACK}"/>{g}</svg>\n')
            write(d / "social" / f"{name}.svg", doc)
            self.r.svg_png(inline_svg(doc), d / "social" / f"{name}.png", size, size)

        # LinkedIn cover 1128x191
        inner, bb = self.lock[("primary", "dark")]
        g, w, h = place(inner, bb, 0, 0, h=86)
        g, _, _ = place(inner, bb, 1128 - 72 - w, (191 - h) / 2, h=86)
        doc = (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="0 0 1128 191"><title>{BRAND} LinkedIn cover</title>'
               f'<rect width="1128" height="191" fill="{BLACK}"/>'
               f'<rect x="0" y="187" width="1128" height="4" fill="{GOLD}"/>{g}</svg>\n')
        write(d / "social" / "linkedin-cover.svg", doc)
        self.r.svg_png(inline_svg(doc), d / "social" / "linkedin-cover.png", 1128 * 2, 191 * 2)

        # social post 1080x1080
        hz, hbb = self.lock[("horizontal", "dark")]
        logo, _, _ = place(hz, hbb, 80, 80, h=54)
        doc = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080">
<title>{BRAND} social media post template (1080x1080)</title>
<rect width="1080" height="1080" fill="{BLACK}"/>
<g id="logo">{logo}</g>
<text id="eyebrow" x="80" y="400" {F} font-size="26" font-weight="600" letter-spacing="4" fill="{GOLD}">[CATEGORY / INSIGHT]</text>
<text id="headline" {F} font-size="76" font-weight="700" fill="{WHITE}" letter-spacing="-1.5">
<tspan x="80" y="490">[Your headline</tspan><tspan x="80" y="578">goes here in up to</tspan><tspan x="80" y="666">three lines]</tspan></text>
<text id="body" {F} font-size="30" font-weight="400" fill="{WHITE}">
<tspan x="80" y="760">[Supporting sentence that explains the insight</tspan><tspan x="80" y="802">in one or two short lines.]</tspan></text>
<rect id="gold-rule" x="80" y="940" width="64" height="4" fill="{GOLD}"/>
<text id="footer" x="80" y="1000" {F} font-size="26" font-weight="500" fill="{WHITE}">[Website URL]</text>
<text id="tagline" x="1000" y="1000" {F} font-size="22" font-weight="500" fill="{GOLD}" text-anchor="end">{TAGLINE}</text>
</svg>
'''
        write(d / "social" / "social-post-template.svg", doc)
        self.r.svg_png(inline_svg(doc), d / "social" / "social-post-template.png", 1080, 1080)

        # product announcement 1200x675 (light)
        hz, hbb = self.lock[("horizontal", "light")]
        logo, _, _ = place(hz, hbb, 64, 56, h=44)
        sym, sbb = self.sym["light"]
        big, w, h = place(sym, sbb, 0, 0, h=430)
        big, _, _ = place(sym, sbb, 1200 - 110 - w, (675 - h) / 2 + 10, h=430)
        doc = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675">
<title>{BRAND} product announcement template (1200x675)</title>
<rect width="1200" height="675" fill="{WHITE}"/>
<g id="logo">{logo}</g>
<g id="eyebrow"><rect x="64" y="200" width="300" height="44" rx="22" fill="{BLACK}"/>
<text x="214" y="228.5" {F} font-size="17" font-weight="600" letter-spacing="2.5" fill="{GOLD}" text-anchor="middle">PRODUCT ANNOUNCEMENT</text></g>
<text id="headline" {F} font-size="58" font-weight="700" fill="{BLACK}" letter-spacing="-1.2">
<tspan x="64" y="320">Introducing</tspan><tspan x="64" y="388">[Feature Name]</tspan></text>
<text id="description" {F} font-size="24" font-weight="400" fill="{BLACK}">
<tspan x="64" y="448">[One or two lines describing what is new</tspan><tspan x="64" y="482">and why it matters to your customers.]</tspan></text>
<g id="cta"><rect x="64" y="532" width="208" height="56" rx="8" fill="{BLACK}"/>
<text x="168" y="567" {F} font-size="20" font-weight="600" fill="{WHITE}" text-anchor="middle">[Learn more]</text></g>
<g id="symbol">{big}</g>
</svg>
'''
        write(d / "social" / "product-announcement-template.svg", doc)
        self.r.svg_png(inline_svg(doc), d / "social" / "product-announcement-template.png", 2400, 1350)

        # presentation title slide 1920x1080
        hz, hbb = self.lock[("horizontal", "dark")]
        logo, _, _ = place(hz, hbb, 120, 100, h=56)
        sym, sbb = self.sym["dark"]
        big, w, h = place(sym, sbb, 0, 0, h=720)
        big, _, _ = place(sym, sbb, 1920 - 200 - w, 180, h=720)
        doc = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080">
<title>{BRAND} presentation title slide (16:9)</title>
<rect width="1920" height="1080" fill="{BLACK}"/>
<g id="logo">{logo}</g>
<text id="title" {F} font-size="104" font-weight="700" fill="{WHITE}" letter-spacing="-2.5">
<tspan x="120" y="500">[Presentation</tspan><tspan x="120" y="620">Title]</tspan></text>
<text id="subtitle" x="120" y="710" {F} font-size="40" font-weight="500" fill="{GOLD}">[Subtitle or key message]</text>
<rect id="gold-rule" x="120" y="860" width="80" height="5" fill="{GOLD}"/>
<text id="presenter" x="120" y="920" {F} font-size="30" font-weight="600" fill="{WHITE}">[Presenter Name]  ·  [Job Title]</text>
<text id="date" x="120" y="964" {F} font-size="26" font-weight="400" fill="{WHITE}">[Date]</text>
<g id="symbol">{big}</g>
</svg>
'''
        write(d / "presentation" / "title-slide.svg", doc)
        self.r.svg_png(inline_svg(doc), d / "presentation" / "title-slide.png", 1920, 1080)

        # letterhead A4
        hz, hbb = self.lock[("horizontal", "light")]
        logo, _, _ = place(hz, hbb, 20, 18, h=12)
        body = "".join(f'<tspan x="20" dy="{6 if i else 0}">{line}</tspan>' for i, line in enumerate([
            "[Body text. Inter Regular 10 pt on 15 pt leading, set in black.]",
            "[Replace these placeholder lines with the content of your letter.]",
            "[Keep margins at 20 mm left and right so the page stays balanced.]"]))
        doc = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">
<title>{BRAND} letterhead (A4)</title>
<rect width="210" height="297" fill="{WHITE}"/>
<g id="logo">{logo}</g>
<g id="sender" {F} font-size="2.8" fill="{BLACK}" text-anchor="end">
<text x="190" y="21.5" font-weight="600">{BRAND}</text>
<text x="190" y="25.6">[Street Address, City, Postcode]</text>
<text x="190" y="29.7">[Email Address]  ·  [Phone Number]</text></g>
<rect id="gold-rule" x="20" y="38" width="170" height="0.4" fill="{GOLD}"/>
<g id="letter" {F} font-size="3.53" fill="{BLACK}">
<text x="20" y="56">[Date]</text>
<text x="20" y="70" font-weight="600">[Recipient Name]</text>
<text x="20" y="75.3">[Company]</text>
<text x="20" y="80.6">[Address]</text>
<text x="20" y="98">Dear [Name],</text>
<text x="20" y="110">{body}</text>
<text x="20" y="150">Kind regards,</text>
<text x="20" y="172" font-weight="600">[Full Name]</text>
<text x="20" y="177.3">[Job Title]</text></g>
<rect x="20" y="276" width="170" height="0.25" fill="{BLACK}"/>
<g id="footer" {F} font-size="2.6" fill="{BLACK}">
<text x="20" y="282.5" font-weight="600">{BRAND}<tspan font-weight="400">  ·  {TAGLINE}</tspan></text>
<text x="190" y="282.5" text-anchor="end">[Website URL]</text></g>
</svg>
'''
        write(d / "stationery" / "letterhead-a4.svg", doc)
        html = ('<html><head><style>@page{size:210mm 297mm;margin:0}html,body{margin:0}'
                'svg{display:block;width:210mm;height:297mm}</style></head><body>'
                f'{inline_svg(doc)}</body></html>')
        self.r.html_pdf(html, d / "stationery" / "letterhead-a4.pdf", "210mm", "297mm")
        self.r.svg_png(inline_svg(doc), d / "stationery" / "letterhead-a4-preview.png", 1240, 1754)

        # email signature
        sig_logo = d / "email-signature" / "email-signature-logo.png"
        sym, sbb = self.sym["light"]
        sdoc = svg_doc(sym, sbb, "signature")
        sig_logo.parent.mkdir(parents=True, exist_ok=True)
        self.r.svg_png(inline_svg(sdoc), sig_logo, round(144 * sbb[2] / sbb[3]), 144)
        sig = pages.email_signature("https://[your-domain]/email-signature-logo.png",
                                    round(72 * sbb[2] / sbb[3]))
        write(d / "email-signature" / "email-signature.html", sig)
        preview = sig.replace("https://[your-domain]/email-signature-logo.png", data_uri(sig_logo))
        self.r.html_png(f'<body style="margin:0;background:#fff;padding:32px">{preview}</body>',
                        d / "email-signature" / "email-signature-preview.png", 640, 220, scale=2)

    # ----------------------------------------------------------- guidelines
    def guidelines(self):
        d = OUT["guidelines"]
        write(d / "logo-construction-sheet.svg", pages.construction_svg(self))
        self.r.svg_png(inline_svg(pages.construction_svg(self)), d / "logo-construction-sheet.png",
                       3200, 2000, bg=WHITE)
        book = pages.Guidelines(self)
        for name, fn in (("logo-usage-and-spacing-guide", book.p_clearspace),
                         ("logo-misuse", book.p_misuse),
                         ("color-palette-sheet", book.p_color),
                         ("typography-specification-sheet", book.p_type)):
            self.r.html_png(book.single(fn()), d / f"{name}.png", pages.PW, pages.PH, scale=2)
            self.r.html_pdf(book.single(fn()), d / f"{name}.pdf", "297mm", "210mm")
        self.r.html_pdf(book.document(), d / "smart-analysis-brand-guidelines.pdf", "297mm", "210mm")
        self.r.html_png(pages.presentation_board(self), ROOT / "smart-analysis-brand-board.png",
                        3200, 2000)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--website", help="real company URL to encode in the business-card QR code")
    a = ap.parse_args()
    for k in ("logos", "icons", "previews", "guidelines", "business-card", "templates"):
        shutil.rmtree(OUT[k], ignore_errors=True)
    with Renderer() as r:
        bld = Builder(r, a.website)
        for step in ("logos", "icons", "previews", "business_card", "templates", "guidelines"):
            print("building", step)
            getattr(bld, step)()
    print("done")


if __name__ == "__main__":
    main()
