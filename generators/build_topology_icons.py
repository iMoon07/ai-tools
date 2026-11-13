#!/usr/bin/env python3
"""Build js/topology-icons.js (the inline SVG sprite) for topology diagrams.

Three icon families:
  * concept icons  - Lucide-style stroke icons (currentColor). Hand-written
                     symbols already in the sprite survive rebuilds; extra icons
                     live in ai-tools/tools/icons/<name>.svg and are added automatically.
  * brand icons    - Simple Icons / devicon logos pulled from the local logo repo
                     (../logo) and emitted as `i-si-<slug>` symbols. Brand colours
                     are preserved; single-colour logos that would disappear on the
                     dark background are lightened, multi-tone logos are untouched.

Adding a logo: drop the SVG in the logo repo (programming/ or stack/), then
run `python3 ai-tools/tools/build_topology_icons.py`. It is discovered automatically
and exposed as `i-si-<slug>`; no script edit is needed. The large `security/`
folder is not scanned wholesale; selected files are pulled through BRAND_EXTRA
(currently `wazuh`).

Adding a concept icon: drop `ai-tools/tools/icons/<name>.svg` (Lucide format)
and it is picked up automatically. No BRANDS entry needed.

Usage:  python3 ai-tools/tools/build_topology_icons.py [--logo-dir DIR] [--out FILE]
"""
import argparse
import json
import re
from pathlib import Path

DEFAULT_SITE = Path("/home/moon/Projects/imoon07.github.io")
DEFAULT_LOGO = Path("/home/moon/Projects/logo")
DEFAULT_OUT = DEFAULT_SITE / "js" / "topology-icons.js"
ICON_DIR = Path(__file__).resolve().parent / "icons"

# Brand logos are discovered automatically from the logo repo, so any SVG added
# there becomes available as `si-<slug>` without editing this script. Only a few
# files use a different public name than their filename.
BRAND_DIRS = ("programming", "stack")
# Security logos live in a large repo (hundreds of files); pull only the ones
# actually referenced by the diagrams, as `si-<slug>`.
BRAND_EXTRA = (
    ("security", ("wazuh",)),
)
BRAND_MAX_BYTES = 60 * 1024  # skip pathological files
BRAND_ALIASES = {
    "aws": "amazonwebservices",
    "gcp": "googlecloud",
    "java": "openjdk",
}

TITLE = re.compile(r"<title>.*?</title>", re.S)
FILL = re.compile(r'\bfill="([^"]*)"')
STROKE = re.compile(r'\bstroke="([^"]*)"')

# Logos that are badges: the dark fill is meant to contrast with a light tile
# inside the logo, so it must not be lightened.
KEEP_AS_IS = {"javascript"}

# Minimum relative luminance for a single-colour logo to stay readable on the
# dark node background (#111827). Darker fills are mixed toward white.
MIN_LUMA = 0.30


def _rgb(value):
    h = value.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        return None
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def _luma(rgb):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _visible(value):
    """Lighten a dark fill until it clears MIN_LUMA; leave others untouched."""
    rgb = _rgb(value)
    if rgb is None or value.strip().lower() in ("none", "transparent", "currentcolor"):
        return value
    if _luma(rgb) >= MIN_LUMA:
        return value
    r, g, b = rgb
    for _ in range(24):
        if _luma((r, g, b)) >= MIN_LUMA:
            break
        r = round(r + (255 - r) * 0.12)
        g = round(g + (255 - g) * 0.12)
        b = round(b + (255 - b) * 0.12)
    return "#%02X%02X%02X" % (r, g, b)


def _inner(svg_text):
    inner = re.sub(r"^.*?<svg\b[^>]*>", "", svg_text, count=1, flags=re.S)
    inner = re.sub(r"</svg>\s*$", "", inner, flags=re.S)
    inner = TITLE.sub("", inner)
    # Drop RDF/Inkscape metadata: it carries unbound namespace prefixes and is
    # useless in a UI sprite.
    inner = re.sub(r"<metadata\b.*?</metadata>", "", inner, flags=re.S)
    return inner.strip()


def _viewbox(svg_text):
    m = re.search(r'viewBox="([^"]+)"', svg_text)
    return m.group(1) if m else "0 0 24 24"


def _namespace(inner, prefix):
    """Prefix every id/url()/href="#..." so internal <defs> references in one
    logo cannot collide with another logo in the same sprite."""
    inner = re.sub(r'\bid="([^"]+)"', lambda m: 'id="%s-%s"' % (prefix, m.group(1)), inner)
    inner = re.sub(r'url\(#([^)]+)\)', lambda m: 'url(#%s-%s)' % (prefix, m.group(1)), inner)
    inner = re.sub(r'(xlink:)?href="#([^"]+)"',
                   lambda m: '%shref="#%s-%s"' % (m.group(1) or '', prefix, m.group(2)), inner)
    return inner


def concept_symbol(name, svg_text):
    inner = _namespace(_inner(svg_text), "c-" + name)
    return (f'<symbol id="i-{name}" viewBox="{_viewbox(svg_text)}" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round">{inner}</symbol>')


def brand_symbol(slug, svg_text):
    root_fill = None
    m = re.search(r'<svg\b[^>]*\bfill="([^"]*)"', svg_text)
    if m and m.group(1).lower() not in ("none", "transparent"):
        root_fill = m.group(1)

    inner = _inner(svg_text)
    inner = STROKE.sub("", inner)
    fills = sorted(set(FILL.findall(inner)))

    if slug in KEEP_AS_IS:
        # Badge logo: dark glyphs on a light tile, keep every colour.
        sym_fill = "currentColor"
    elif fills:
        # Paths carry their own colours (multi-tone logo): lighten dark ones.
        inner = FILL.sub(lambda x: 'fill="%s"' % _visible(x.group(1)), inner)
        sym_fill = "currentColor"
    elif root_fill:
        # Single-colour logo whose fill sits on the <svg> root.
        sym_fill = _visible(root_fill)
    else:
        # No colour anywhere: inherit the node's currentColor.
        sym_fill = "currentColor"

    inner = _namespace(inner, "b-" + slug)
    return (f'<symbol id="i-si-{slug}" viewBox="{_viewbox(svg_text)}" '
            f'fill="{sym_fill}">{inner}</symbol>')


def load_existing(sprite_path):
    if not sprite_path.exists():
        return []
    src = sprite_path.read_text(encoding="utf-8")
    m = re.search(r'window\.TOPOLOGY_SPRITE\s*=\s*("(?:[^"\\]|\\.)*")\s*;', src)
    if not m:
        return []
    sprite = json.loads(m.group(1))
    return re.findall(r"<symbol\b.*?</symbol>", sprite, re.S)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--logo-dir", default=str(DEFAULT_LOGO))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    logo_dir = Path(args.logo_dir)
    out = Path(args.out)

    existing = load_existing(out)
    have = {re.search(r'id="([^"]+)"', s).group(1) for s in existing}

    concept = [s for s in existing if 'id="i-si-' not in s]
    added_concept = []
    # Concept icons come from two places: tools/icons (local Lucide extras) and
    # <logo repo>/profession (role/occupation icons such as chef, hacker, doctor).
    sources = [ICON_DIR]
    if (logo_dir / "profession").is_dir():
        sources.append(logo_dir / "profession")
    for d in sources:
        for f in sorted(d.glob("*.svg")):
            name = "i-" + f.stem
            if name in have:
                continue
            have.add(name)
            concept.append(concept_symbol(f.stem, f.read_text(encoding="utf-8")))
            added_concept.append(f.stem)

    # Auto-discover every SVG in the brand folders. Nothing is hardcoded: drop a
    # file in the logo repo and rerun; it appears as i-si-<slug>.
    brands, missing, seen = [], [], set()
    for sub in BRAND_DIRS:
        d = logo_dir / sub
        if not d.is_dir():
            missing.append(f"folder {sub}")
            continue
        for f in sorted(d.glob("*.svg")):
            if f.stat().st_size > BRAND_MAX_BYTES:
                missing.append(f"{f.stem} (too large)")
                continue
            slug = BRAND_ALIASES.get(f.stem, f.stem)
            if slug in seen:
                continue
            seen.add(slug)
            try:
                brands.append(brand_symbol(slug, f.read_text(encoding="utf-8")))
            except Exception as exc:  # keep one bad file from breaking the build
                missing.append(f"{slug}: {exc}")

    # Selected logos from large folders (security/) that are actually used.
    for sub, names in BRAND_EXTRA:
        d = logo_dir / sub
        if not d.is_dir():
            missing.append(f"folder {sub}")
            continue
        for name in names:
            f = d / (name + ".svg")
            if not f.is_file():
                missing.append(f"{sub}/{name}")
                continue
            if f.stat().st_size > BRAND_MAX_BYTES:
                missing.append(f"{name} (too large)")
                continue
            slug = BRAND_ALIASES.get(name, name)
            if slug in seen:
                continue
            seen.add(slug)
            try:
                brands.append(brand_symbol(slug, f.read_text(encoding="utf-8")))
            except Exception as exc:
                missing.append(f"{slug}: {exc}")

    sprite = ('<svg xmlns="http://www.w3.org/2000/svg" '
              'xmlns:xlink="http://www.w3.org/1999/xlink" '
              'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
              'xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.0.dtd" '
              'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
              'xmlns:cc="http://creativecommons.org/ns#" '
              'xmlns:dc="http://purl.org/dc/elements/1.1/" '
              'style="position:absolute;width:0;height:0;overflow:hidden" '
              'aria-hidden="true" focusable="false">'
              + "".join(concept) + "".join(brands) + "</svg>")

    out.write_text(
        "/* Ikon topologi: Lucide (ISC) + Simple Icons (CC0). Tanpa emoji. */\n"
        "/* Dibuat oleh ai-tools/tools/build_topology_icons.py — jangan edit tangan. */\n"
        "window.TOPOLOGY_SPRITE = " + json.dumps(sprite) + ";\n",
        encoding="utf-8",
    )
    print(f"wrote {out} — concept={len(concept)} brand={len(brands)} "
          f"missing={len(missing)}")
    if added_concept:
        print("  new concept icons:", ", ".join(added_concept))
    for m in missing:
        print("  MISSING:", m)


if __name__ == "__main__":
    main()