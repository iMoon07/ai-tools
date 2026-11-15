#!/usr/bin/env python3
"""Crawl IconScout for free Lottie animations, then download them in bulk.

Phase 1 crawls listing pages and keeps the item links whose slug matches a
keyword. Phase 2 opens each link once, reads its own JSON-LD for the credits,
and clicks "Download Lottie JSON". Nothing is guessed from the listing: the
listing's JSON-LD points at *related* items, so the hrefs are the only reliable
source of links.

  python3 ai-tools/fetch/iconscout_pull.py --crawl --tags security,network,ai
  python3 ai-tools/fetch/iconscout_pull.py --download --limit 100 \
      --out assets/lottie/inbox

Needs a logged-in session in ~/.config/alur/iconscout.env (ICONSCOUT_COOKIE=...).
"""
import argparse
import json
import re
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "browser"))
from iconscout_session import UA, Session  # noqa: E402

LIST_URL = "https://iconscout.com/free-lottie-animations/{tag}?page={page}"
SEARCH_URL = "https://iconscout.com/free-lottie-animations/{q}"
LINKS = "links.json"
DEFAULT_KEYWORDS = ("hacker", "cyber", "security", "malware", "phish", "virus", "network",
                    "server", "data", "cloud", "encrypt", "lock", "shield", "bug", "ai")

# The listing renders cards without anchors, but every card carries an
# ImageObject with acquireLicensePage — that is the link list.
LINKS_JS = """
(function(){
  var seen = {}, out = [];
  document.querySelectorAll('script[type="application/ld+json"]').forEach(function(s){
    var d; try { d = JSON.parse(s.textContent); } catch (e) { return; }
    if (!d || d['@type'] !== 'ImageObject') return;
    var url = d.acquireLicensePage || '';
    if (!url || seen[url]) return;
    seen[url] = 1;
    out.push({url: url, title: (d.creditText || '').slice(0, 90),
              author: (d.creator || {}).name || '', license: d.license || '',
              credit: d.creditText || '', preview: d.contentUrl || ''});
  });
  return out;
})()
"""

DETAIL_JS = """
(function(){
  var out = {author: '', license: '', credit: '', name: ''};
  document.querySelectorAll('script[type="application/ld+json"]').forEach(function(s){
    var d; try { d = JSON.parse(s.textContent); } catch (e) { return; }
    if (!d || d['@type'] !== 'ImageObject') return;
    out.author = (d.creator || {}).name || '';
    out.license = d.license || '';
    out.credit = d.creditText || '';
    out.name = d.name || '';
  });
  return out;
})()
"""

# The download button is hydrated by client-side JS, so it appears a moment
# after load. Without this wait every page reports "no download button".
CLICK_JS = """
(function(){
  var b = [].slice.call(document.querySelectorAll('button')).filter(function(x){
    return /download\\s*lottie\\s*json/i.test((x.textContent || '').trim());
  })[0];
  if (!b) return 'no-button';
  b.click();
  return 'clicked';
})()
"""

READY_JS = """
(function(){
  return [].slice.call(document.querySelectorAll('button')).some(function(x){
    return /download\\s*lottie\\s*json/i.test((x.textContent || '').trim());
  }) ? 'ready' : 'no-button';
})()
"""


def wait_ready(session, timeout=25):
    """Poll until the download button is hydrated, or give up."""
    end = time.time() + timeout
    while time.time() < end:
        if session.ev(READY_JS) == "ready":
            return True
        time.sleep(1.0)
    return False


def crawl(session, tags, pages, keywords, out_path):
    seen, rows = set(), []
    for tag in tags:
        for page in range(1, pages + 1):
            url = LIST_URL.format(tag=tag, page=page)
            if not session.open(url, timeout=25):
                print("  %s p%d: challenge not cleared" % (tag, page), flush=True)
                continue
            got = session.ev(LINKS_JS) or []
            keep = [r for r in got if r["url"] not in seen]
            for r in keep:
                seen.add(r["url"])
            print("  %s p%d: %d links (%d new)" % (tag, page, len(got), len(keep)), flush=True)
            rows.extend(keep)
            time.sleep(0.8)

    rx = re.compile("|".join(keywords), re.I)
    picked = [r for r in rows if rx.search(r["url"])]
    out_path.write_text(json.dumps(picked, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("crawled %d links, %d match %s -> %s" % (len(rows), len(picked), ",".join(keywords), out_path))
    return picked


def download(session, links, out, limit, delay):
    dl = out / "_dl"
    dl.mkdir(parents=True, exist_ok=True)
    session.cmd("Browser.setDownloadBehavior", behavior="allow", downloadPath=str(dl))
    meta_path = out / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else []
    known = {row.get("source") for row in meta}
    made = 0
    for item in links:
        if len(meta) >= limit:
            break
        url = item["url"]
        if url in known:
            continue
        slug = url.rstrip("/").split("/")[-1]
        target = out / ("%s.json" % slug)
        print("  · %s" % slug, flush=True)
        if not session.open(url, timeout=25):
            print("    ! challenge (%s)" % slug, flush=True)
            time.sleep(3.0)
            continue
        info = session.ev(DETAIL_JS) or {}
        before = {p.name for p in dl.iterdir()}
        if not wait_ready(session, timeout=20):
            print("    ! no download button (%s)" % slug, flush=True)
            time.sleep(1.0)
            continue
        saved = None
        for _ in range(40):
            time.sleep(0.5)
            done = [p for p in dl.iterdir() if p.name not in before and not p.name.endswith(".crdownload")]
            if done:
                saved = done[0]
                break
        if not saved:
            print("    ! no file (%s)" % slug, flush=True)
            continue
        shutil.move(str(saved), str(target))
        meta.append({"slug": slug, "source": url, "file": target.name,
                     "name": info.get("name", ""), "author": info.get("author", ""),
                     "license": info.get("license", ""), "credit": info.get("credit", "")})
        meta_path.write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        made += 1
        print("    + %-46s %7d B  by %s" % (slug, target.stat().st_size, info.get("author") or "?"),
              flush=True)
        time.sleep(delay)
    print("downloaded %d (meta %d)" % (made, len(meta)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crawl", action="store_true")
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--tags", default="security,network,ai")
    ap.add_argument("--pages", type=int, default=2)
    ap.add_argument("--keywords", default=",".join(DEFAULT_KEYWORDS))
    ap.add_argument("--limit", type=int, default=80)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "assets" / "lottie" / "inbox"))
    ap.add_argument("--links", default="")
    ap.add_argument("--delay", type=float, default=1.2)
    ap.add_argument("--headless", action="store_true")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    links_path = Path(args.links) if args.links else (out / LINKS)

    session = Session(headless=args.headless, log=lambda m: print(m, flush=True))
    try:
        if args.crawl or not links_path.is_file():
            tags = [t.strip() for t in args.tags.split(",") if t.strip()]
            keywords = [k.strip() for k in args.keywords.split(",") if k.strip() and k.strip() != "all"]
            crawl(session, tags, args.pages, keywords, links_path)
        if args.download:
            links = json.loads(links_path.read_text(encoding="utf-8"))
            print("download: %d links from %s" % (len(links), links_path), flush=True)
            download(session, links, out, args.limit, args.delay)
    finally:
        session.close()


if __name__ == "__main__":
    main()