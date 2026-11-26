"""Shared design system for the A-L-Z profile.

Palette, typography, Lucide icons and small SVG helpers used by both
`build-assets.py` (static sections) and `update-projects.py` (automated
sections), so every generated image shares the same visual language.
Only the Python standard library is used.
"""
from __future__ import annotations

import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
WIDTH = 880  # README content width used as the base viewBox for full-width images

FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'SF Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

THEMES = {
    "light": {
        "page": "#FFFFFF",
        "card": "#F6F8FA",
        "header": "#F3F5F7",
        "raised": "#FFFFFF",
        "active": "#E6EAEF",
        "text": "#17212B",
        "muted": "#656D76",
        "border": "#D0D7DE",
        "icon": "#8B949E",
        "green": "#2DA44E",
        "green_soft": "#DAFBE1",
        "grid": "#D0D7DE",
        "heat": ["#EFF2F5", "#ACEEBB", "#4AC26B", "#2DA44E", "#116329"],
    },
    "dark": {
        "page": "#0D1117",
        "card": "#151B23",
        "header": "#151B23",
        "raised": "#0D1117",
        "active": "#262C36",
        "text": "#E6EDF3",
        "muted": "#9198A1",
        "border": "#30363D",
        "icon": "#6E7681",
        "green": "#3FB950",
        "green_soft": "#12261E",
        "grid": "#30363D",
        "heat": ["#1C2129", "#033A16", "#196C2E", "#2EA043", "#56D364"],
    },
}

# Lucide icons (ISC licence), 24x24 grid, stroke based.
LUCIDE = {
    "code": '<path d="m16 18 6-6-6-6"/><path d="m8 6-6 6 6 6"/>',
    "code-xml": '<path d="m18 16 4-4-4-4"/><path d="m6 8-4 4 4 4"/><path d="m14.5 4-5 16"/>',
    "wallet": '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
    "workflow": '<rect width="8" height="8" x="3" y="3" rx="2"/><path d="M7 11v4a2 2 0 0 0 2 2h4"/><rect width="8" height="8" x="13" y="13" rx="2"/>',
    "network": '<rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"/><path d="M12 12V8"/>',
    "map-pin": '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
    "lock": '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "radio-tower": '<path d="M4.9 16.1C1 12.2 1 5.8 4.9 1.9"/><path d="M7.8 4.7a6.14 6.14 0 0 0-.8 7.5"/><circle cx="12" cy="9" r="2"/><path d="M16.2 4.8c2 2 2.26 5.11.8 7.47"/><path d="M19.1 1.9a9.96 9.96 0 0 1 0 14.1"/><path d="M9.5 18h5"/><path d="m8 22 4-11 4 11"/>',
    "activity": '<path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"/>',
    "briefcase": '<path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/><rect width="20" height="14" x="2" y="6" rx="2"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
    "book-open": '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
    "mic": '<path d="M12 19v3"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><rect x="9" y="2" width="6" height="13" rx="3"/>',
    "message-circle": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "arrow-up-right": '<path d="M7 7h10v10"/><path d="M7 17 17 7"/>',
    "braces": '<path d="M8 3H7a2 2 0 0 0-2 2v5a2 2 0 0 1-2 2 2 2 0 0 1 2 2v5c0 1.1.9 2 2 2h1"/><path d="M16 21h1a2 2 0 0 0 2-2v-5c0-1.1.9-2 2-2a2 2 0 0 1-2-2V5a2 2 0 0 0-2-2h-1"/>',
    "folder-git": '<path d="M9 20H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h3.9a2 2 0 0 1 1.69.9l.81 1.2a2 2 0 0 0 1.67.9H20a2 2 0 0 1 2 2v5"/><circle cx="13" cy="12" r="2"/><path d="M18 19c-2.8 0-5-2.2-5-5v8"/><circle cx="20" cy="19" r="2"/>',
    "star": '<path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "building": '<rect width="16" height="20" x="4" y="2" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M12 6h.01"/><path d="M12 10h.01"/><path d="M12 14h.01"/><path d="M16 10h.01"/><path d="M16 14h.01"/><path d="M8 10h.01"/><path d="M8 14h.01"/>',
    "laptop": '<path d="M20 16V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v9m16 0H4m16 0 1.28 2.55a1 1 0 0 1-.9 1.45H3.62a1 1 0 0 1-.9-1.45L4 16"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
}

CHARS = ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~áéíóúñÁÉÍÓÚÑüÜ—·↗–’…'
WIDTHS = {
    400: [281, 288, 466, 633, 642, 982, 644, 300, 365, 365, 501, 662, 288, 460, 288, 360, 631, 407, 610, 618, 646, 608, 620, 566, 619, 620, 288, 302, 662, 662, 662, 511, 966, 690, 654, 730, 722, 601, 590, 746, 743, 269, 571, 672, 565, 903, 753, 765, 639, 765, 644, 642, 646, 744, 690, 985, 682, 679, 629, 365, 360, 365, 471, 456, 323, 562, 612, 571, 612, 583, 370, 613, 591, 242, 242, 549, 242, 876, 591, 600, 612, 612, 376, 528, 327, 591, 562, 818, 546, 562, 552, 426, 333, 426, 662, 562, 583, 242, 600, 591, 591, 690, 601, 269, 765, 744, 753, 591, 744, 1000, 288, 775, 500, 261, 864],
    500: [267, 304, 494, 639, 646, 993, 653, 313, 369, 369, 521, 667, 303, 462, 303, 370, 646, 415, 616, 627, 656, 618, 630, 571, 629, 630, 303, 315, 667, 667, 667, 527, 982, 709, 657, 733, 722, 603, 589, 748, 745, 272, 575, 688, 565, 913, 756, 767, 642, 769, 648, 646, 653, 740, 709, 1003, 701, 696, 641, 369, 370, 369, 477, 463, 337, 568, 618, 577, 618, 587, 379, 620, 602, 252, 252, 559, 252, 888, 602, 604, 618, 618, 387, 539, 340, 602, 575, 829, 557, 575, 559, 440, 346, 440, 667, 568, 587, 252, 604, 602, 602, 709, 603, 272, 767, 740, 756, 602, 740, 1000, 303, 778, 500, 277, 910],
    600: [252, 321, 523, 644, 650, 1004, 663, 326, 373, 373, 540, 673, 319, 465, 319, 379, 660, 423, 623, 636, 666, 629, 640, 576, 640, 640, 319, 329, 673, 673, 673, 543, 999, 728, 659, 737, 722, 605, 588, 749, 746, 277, 580, 703, 565, 922, 759, 769, 645, 773, 652, 650, 660, 736, 728, 1020, 720, 713, 652, 373, 379, 373, 481, 469, 351, 574, 624, 583, 624, 591, 389, 625, 612, 262, 262, 569, 262, 900, 612, 609, 624, 624, 397, 549, 353, 612, 587, 839, 569, 588, 566, 455, 359, 455, 673, 574, 591, 262, 609, 612, 612, 728, 605, 277, 769, 736, 759, 612, 736, 1000, 319, 780, 500, 294, 956],
    700: [237, 338, 552, 649, 655, 1016, 672, 339, 377, 377, 559, 679, 334, 468, 334, 388, 674, 431, 630, 646, 676, 639, 649, 582, 651, 649, 334, 343, 679, 679, 679, 560, 1016, 747, 662, 740, 722, 607, 587, 750, 747, 281, 584, 719, 565, 932, 762, 771, 648, 777, 657, 655, 667, 732, 747, 1038, 738, 731, 664, 377, 388, 377, 487, 476, 365, 581, 630, 588, 630, 596, 398, 632, 623, 271, 271, 580, 271, 913, 623, 613, 630, 630, 407, 560, 366, 623, 600, 850, 580, 602, 573, 469, 372, 469, 679, 581, 596, 271, 613, 623, 623, 747, 607, 281, 771, 732, 762, 623, 732, 1000, 334, 783, 500, 311, 1002],
}


def text_width(text: str, size: float, weight: int = 400, spacing: float = 0.0) -> float:
    """Approximate rendered width of `text` (Inter metrics, slight safety margin)."""
    table = WIDTHS.get(weight) or WIDTHS[min(WIDTHS, key=lambda w: abs(w - weight))]
    total = 0
    for char in text:
        index = CHARS.find(char)
        total += table[index] if index >= 0 else 640
    return total / 1000 * size * 1.03 + spacing * max(len(text) - 1, 0)


def wrap(text: str, size: float, weight: int, max_width: float) -> list[str]:
    words, lines, line = text.split(), [], ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if line and text_width(candidate, size, weight) > max_width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines or [""]


def esc(text: str) -> str:
    return escape(text, quote=True)


def text(x, y, content, size, color, weight=400, anchor="start", spacing=0, family=FONT, extra=""):
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    an = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text x="{x:g}" y="{y:g}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}"{ls}{an}{extra}>{esc(content)}</text>')


def icon(name, x, y, size, color, stroke=2.0):
    scale = size / 24
    return (f'<g transform="translate({x:g} {y:g}) scale({scale:.4f})" fill="none" stroke="{color}" '
            f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">{LUCIDE[name]}</g>')


_BRAND_CACHE: dict[str, str] = {}


def brand(name, x, y, size, color):
    """Official logo path (Simple Icons, CC0) stored locally in assets/icons/tech."""
    if name not in _BRAND_CACHE:
        source = (ASSETS / "icons" / "tech" / f"{name}.svg").read_text(encoding="utf-8")
        _BRAND_CACHE[name] = " ".join(re.findall(r'<path d="([^"]+)"', source))
    scale = size / 24
    return (f'<path transform="translate({x:g} {y:g}) scale({scale:.4f})" fill="{color}" '
            f'd="{_BRAND_CACHE[name]}"/>')


def rect(x, y, w, h, fill, stroke=None, rx=12, extra=""):
    st = f' stroke="{stroke}" stroke-width="1"' if stroke else ""
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx}" fill="{fill}"{st}{extra}/>'


def frame(x, y, w, h, t, fill="card", rx=12):
    """Card surface with a hairline border drawn inside the pixel grid."""
    return rect(x + 0.5, y + 0.5, w - 1, h - 1, t[fill], t["border"], rx)


def tile(x, y, size, t, name, icon_size=None, color=None):
    icon_size = icon_size or round(size * 0.48)
    offset = (size - icon_size) / 2
    return (rect(x + 0.5, y + 0.5, size - 1, size - 1, t["raised"], t["border"], 10)
            + icon(name, x + offset, y + offset, icon_size, color or t["text"], 1.75))


def pill(x, y, label, t, size=13, weight=500, icon_name=None, height=28, fill="raised", color=None, pad=12):
    """Rounded tag; returns (svg, width)."""
    icon_w = (size + 6) if icon_name else 0
    w = pad * 2 + icon_w + text_width(label, size, weight)
    parts = [rect(x + 0.5, y + 0.5, w - 1, height - 1, t[fill], t["border"], height / 2 if height < 32 else 10)]
    tx = x + pad
    if icon_name:
        parts.append(icon(icon_name, tx, y + (height - size - 1) / 2, size + 1, color or t["muted"], 2))
        tx += icon_w
    parts.append(text(tx, y + height / 2 + size * 0.36, label, size, color or t["muted"], weight))
    return "".join(parts), w


def svg(width, height, body, title, desc=""):
    d = f"<desc>{esc(desc)}</desc>" if desc else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:g}" height="{height:g}" '
            f'viewBox="0 0 {width:g} {height:g}" role="img" aria-label="{esc(title)}">'
            f"<title>{esc(title)}</title>{d}{body}</svg>\n")


def write(relative: str, content: str) -> Path:
    path = ASSETS / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")
    return path
