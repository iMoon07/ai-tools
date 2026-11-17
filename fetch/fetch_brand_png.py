#!/usr/bin/env python3
"""Fill the gaps in the logo collection with raster marks.

Most of the commercial security vendors never published an SVG logo, so the
remaining candidates are fetched as PNG from the browser favicon of their
official site (Google's 192px renderer, DuckDuckGo as fallback). They live in
their own folders so they stay distinguishable from the SVG sets:

  security-tools/      open-source tools and OSS projects
  security-enterprise/ commercial vendors and products

Domains come from ai-tools/data/logo_domains.tsv; when the file has no domain
the tool asks Wikidata for the official website (P856).

Usage:
  python3 ai-tools/fetch/fetch_brand_png.py --only security-tools,security-enterprise
  python3 ai-tools/fetch/fetch_brand_png.py --dry-run
"""
import argparse
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_LOGO = Path("/home/moon/Projects/logo")
DOMAINS = HERE.parent / "data" / "logo_domains.tsv"
REPORT = HERE.parent / "data" / "logo_png_report.json"

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"
GOOGLE = "https://www.google.com/s2/favicons?domain=%s&sz=256"
DDG = "https://icons.duckduckgo.com/ip3/%s.ico"
UNAVATAR = "https://unavatar.io/%s"
WIKI = ("https://www.wikidata.org/w/api.php?action=wbsearchentities"
        "&search=%s&language=en&format=json&limit=6")
WIKI_ENTITY = ("https://www.wikidata.org/w/api.php?action=wbgetentities"
               "&ids=%s&props=claims&format=json")
NEW_FOLDERS = ("security-tools", "security-enterprise")
# Generic hosts serve their own favicon, not the project's mark.
SKIP_DOMAINS = {"github.com", "gitlab.com", "bitbucket.org", "readthedocs.io",
                "docs.github.com", "google.github.io"}
SKIP_SUFFIX = (".readthedocs.io",)
MIN_SIDE = 48


def get(url, timeout=25, retries=3, backoff=1.2):
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read(), r.headers.get("Content-Type", "")
        except Exception as exc:
            last = exc
            time.sleep(backoff * (attempt + 1))
    raise last


def official_site(name):
    """Best-effort P856 lookup on Wikidata."""
    try:
        body, _ = get(WIKI % urllib.parse.quote(name), retries=2)
        data = json.loads(body)
    except Exception:
        return None
    for hit in data.get("search", [])[:6]:
        desc = (hit.get("description") or "").lower()
        if not any(w in desc for w in ("software", "company", "product", "tool",
                                       "suite", "platform", "security")):
            continue
        qid = hit.get("id")
        try:
            ent, _ = get(WIKI_ENTITY % qid, retries=2)
            claims = json.loads(ent)["entities"][qid]["claims"]
        except Exception:
            continue
        for claim in claims.get("P856", []):
            url = claim["mainsnak"].get("datavalue", {}).get("value")
            if url:
                return urllib.parse.urlparse(url).netloc or url
    return None


def fetch_png(domain):
    """Try the favicon endpoints; fall back to unavatar (often returns the SVG)."""
    for url in (UNAVATAR % domain, GOOGLE % domain, DDG % domain):
        try:
            body, ctype = get(url, retries=2)
        except Exception:
            continue
        if "svg" in ctype or body.lstrip()[:5] == b"<?xml" or b"<svg" in body[:400]:
            return body, "svg"
        if "image" not in ctype and body[:4] not in (b"\x89PNG", b"\x00\x00\x01\x00"):
            continue
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(body))
            if min(img.size) < MIN_SIDE:
                continue
            return body, list(img.size)
        except Exception:
            if body[:4] == b"\x89PNG":
                return body, None
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--logo-dir", default=str(DEFAULT_LOGO))
    ap.add_argument("--only", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    logo = Path(args.logo_dir)
    only = {c.strip() for c in args.only.split(",") if c.strip()}

    rows = []
    for line in DOMAINS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        slug, cat, name = parts[0].strip(), parts[1].strip(), parts[2].strip()
        domain = parts[3].strip() if len(parts) > 3 else ""
        if only and cat not in only:
            continue
        rows.append((slug, cat, name, domain))

    existing = set()
    for f in logo.rglob("*"):
        if f.is_file():
            existing.add(f.stem.lower())

    results = {"saved": [], "exists": [], "missing": [], "failed": []}
    todo = [r for r in rows if r[0].lower() not in existing]
    for slug, cat, name, domain in rows:
        if slug.lower() in existing:
            results["exists"].append({"slug": slug})

    def work(item):
        slug, cat, name, domain = item
        if domain.lower() in SKIP_DOMAINS or domain.lower().endswith(SKIP_SUFFIX):
            domain = None
        if not domain:
            domain = official_site(name)
        if not domain:
            return ("missing", slug, cat, name, None, None)
        body, size = fetch_png(domain)
        if not body:
            return ("missing", slug, cat, name, domain, None)
        return ("ok", slug, cat, name, domain, (body, size))

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for kind, slug, cat, name, domain, payload in pool.map(work, todo):
            if kind == "missing":
                results["missing"].append({"slug": slug, "name": name,
                                           "category": cat, "domain": domain})
                print("MISS  %-26s %s" % (slug, domain or name), flush=True)
            elif args.dry_run:
                results["saved"].append({"slug": slug, "domain": domain, "dry": True})
                print("HIT   %-26s %s" % (slug, domain), flush=True)
            else:
                body, size = payload
                ext = "svg" if size == "svg" else "png"
                target = logo / cat / (slug + "." + ext)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(body)
                results["saved"].append({"slug": slug, "category": cat, "domain": domain,
                                         "ext": ext, "bytes": len(body),
                                         "size": None if ext == "svg" else size})
                print("OK    %-26s %-28s %s" % (
                    slug, domain, ext), flush=True)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(results, indent=1), encoding="utf-8")
    print("\nsaved %d, exists %d, missing %d, failed %d -> %s" % (
        len(results["saved"]), len(results["exists"]),
        len(results["missing"]), len(results["failed"]), REPORT))


if __name__ == "__main__":
    main()