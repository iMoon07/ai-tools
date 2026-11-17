#!/usr/bin/env python3
"""Fetch brand logos for the local logo-svg collection.

Sources, tried in order for every candidate in
ai-tools/data/logo_candidates.tsv:

  1. simple-icons  (cdn.simpleicons.org, coloured with the brand hex) -- the
     widest reliable set of tech/programming marks.
  2. Iconify       (api.iconify.design) -- aggregates theSVG, selfh.st, SVG
     Porn, Custom Brand Icons and friends for brands simple-icons dropped.

Files land in <logo-dir>/<category>/<slug>.svg. Anything already in the
collection is skipped, so re-running is safe. The report is written to
ai-tools/data/logo_fetch_report.json.

Usage:
  python3 ai-tools/fetch/fetch_brand_logos.py --only stack,programming
  python3 ai-tools/fetch/fetch_brand_logos.py --only stack --source si
"""
import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_LOGO = Path("/home/moon/Projects/logo")
CANDIDATES = HERE.parent / "data" / "logo_candidates.tsv"
REPORT = HERE.parent / "data" / "logo_fetch_report.json"

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"
SI_JSON = "https://cdn.jsdelivr.net/npm/simple-icons@13/_data/simple-icons.json"
SI_CDN = "https://cdn.simpleicons.org/%s/%s"
ICONIFY = "https://api.iconify.design"
CATEGORIES = ("security", "stack", "programming", "brands", "profession", "motion")

# Iconify collections worth trusting for a brand mark, best colour set first.
PREFERRED = [
    "thesvg-color", "svgl", "svgl-color", "logos", "selfhst", "cbi",
    "streamline-logos", "simple-icons", "devicon", "skill-icons", "cib",
    "file-icons", "catppuccin", "fa6-brands", "fa7-brands", "bxl",
]
SKIP_ICONS = re.compile(r"(dark|light|mono|outline|alt|old|new|beta|deprecat)", re.I)
# "Apache Kafka" is a candidate "kafka": compare on the distinctive words.
NOISE = {"apache", "the", "project", "software", "foundation", "inc", "labs",
         "technologies", "official", "logo", "icon"}


def get(url, timeout=25, retries=3, backoff=1.5):
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as exc:
            last = exc
            time.sleep(backoff * (attempt + 1))
    raise last


def slugify(value):
    value = value.lower().replace("&", " and ")
    value = re.sub(r"['’.]", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-{2,}", "-", value).strip("-")


def tokens(value):
    return [t for t in re.split(r"[-_ ]+", value.lower()) if t]


def load_si():
    """slug/alias -> (hex, title)."""
    try:
        data = json.loads(get(SI_JSON, 60, retries=2))
    except Exception as exc:
        print("simple-icons index unavailable: %s" % exc)
        return {}
    index = {}
    for item in data.get("icons", []):
        title, hexv = item.get("title", ""), item.get("hex")
        if not title or not hexv:
            continue
        keys = {slugify(title)}
        words = [w for w in tokens(title) if w not in NOISE]
        if words:
            keys.add("-".join(words))
        for alias in (item.get("aliases", {}) or {}).get("aka", []):
            keys.add(slugify(alias))
        for key in keys:
            index.setdefault(key, (hexv, title))
    return index


def si_lookup(slug, name, si_index):
    for key in [slug, slugify(name)] + ["-".join(t) for t in [tokens(name)]]:
        key = "-".join([t for t in tokens(key) if t not in NOISE]) or key
        if key in si_index:
            return si_index[key]
    return None


def iconify_pick(icons, query):
    want = tokens(query)
    if not want:
        return None
    best = None
    for icon in icons:
        prefix, _, name = icon.partition(":")
        have = tokens(name)
        if not have or any(t not in have for t in want):
            continue
        extra = len(have) - len(want)
        rank = PREFERRED.index(prefix) if prefix in PREFERRED else len(PREFERRED)
        if SKIP_ICONS.search(name):
            rank += 5
        score = (extra, rank, len(name), name)
        if best is None or score < best[0]:
            best = (score, icon)
    return best[1] if best else None


def iconify_search(name):
    url = "%s/search?query=%s&limit=40" % (ICONIFY, urllib.parse.quote(name))
    try:
        return json.loads(get(url, 30, retries=2)).get("icons", []) or []
    except Exception:
        return []


def is_mono(body):
    text = body.decode("utf-8", "replace")
    if "currentColor" in text:
        return True
    colors = {c.lower() for c in re.findall(
        r'(?:fill|stroke)\s*[:=]\s*["\']?(#[0-9a-fA-F]{3,8})', text)}
    colors -= {"#000000", "#000", "#ffffff", "#fff"}
    return not colors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--logo-dir", default=str(DEFAULT_LOGO))
    ap.add_argument("--only", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--source", default="both", choices=("both", "si", "iconify"))
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    logo = Path(args.logo_dir)
    only = {c.strip() for c in args.only.split(",") if c.strip()}
    rows = []
    for line in CANDIDATES.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        slug, cat, name = (p.strip() for p in parts[:3])
        if only and cat not in only:
            continue
        rows.append((slug, cat, name))
    if args.limit:
        rows = rows[:args.limit]

    existing = set()
    for f in logo.rglob("*"):
        if f.is_file():
            existing.add(f.stem.lower())

    si_index = load_si() if args.source in ("both", "si") else {}
    print("candidates %d, existing %d, simple-icons %d" % (
        len(rows), len(existing), len(si_index)))

    results = {"fetched": [], "exists": [], "missing": [], "failed": [], "mono": []}
    todo = []
    for slug, cat, name in rows:
        if slug.lower() in existing:
            results["exists"].append({"slug": slug, "category": cat})
        else:
            todo.append((slug, cat, name))

    def work(item):
        slug, cat, name = item
        if si_index:
            hit = si_lookup(slug, name, si_index)
            if hit:
                hexv, title = hit
                try:
                    body = get(SI_CDN % (slug, hexv), retries=3)
                    return ("ok", slug, cat, name, "simple-icons:%s" % title, body)
                except Exception:
                    pass
        if args.source == "si":
            return ("missing", slug, cat, name, None, None)
        icon = iconify_pick(iconify_search(name), name)
        if not icon:
            return ("missing", slug, cat, name, None, None)
        try:
            body = get("%s/%s.svg" % (ICONIFY, icon), retries=3, backoff=2.5)
        except Exception as exc:
            return ("failed", slug, cat, name, icon, str(exc)[:120])
        return ("ok", slug, cat, name, icon, body)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for kind, slug, cat, name, src, payload in pool.map(work, todo):
            if kind == "missing":
                results["missing"].append({"slug": slug, "name": name, "category": cat})
                print("MISS  %-26s %s" % (slug, name), flush=True)
            elif kind == "failed":
                results["failed"].append({"slug": slug, "icon": src, "why": payload})
                print("FAIL  %-26s %s" % (slug, src), flush=True)
            elif args.dry_run:
                print("HIT   %-26s %s" % (slug, src), flush=True)
                results["fetched"].append({"slug": slug, "category": cat, "icon": src, "dry": True})
            else:
                target = logo / cat / (slug + ".svg")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload)
                mono = is_mono(payload)
                results["fetched"].append({"slug": slug, "category": cat, "icon": src,
                                           "bytes": len(payload), "mono": mono})
                if mono:
                    results["mono"].append({"slug": slug, "category": cat, "icon": src})
                print("OK    %-26s %-36s %s" % (
                    slug, src, "mono" if mono else "colour"), flush=True)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(results, indent=1), encoding="utf-8")
    print("\nfetched %d (mono %d), exists %d, missing %d, failed %d -> %s" % (
        len(results["fetched"]), len(results["mono"]), len(results["exists"]),
        len(results["missing"]), len(results["failed"]), REPORT))


if __name__ == "__main__":
    main()