#!/usr/bin/env python3
"""Download free Lottie animations from IconScout, Cloudflare-tolerant.

Plain HTTP gets challenged after a few dozen requests, so a real browser clears
the challenge once (ai-tools/browser/iconscout_session.py, persistent profile)
and the fast `requests` path reuses its cookies. When a request is challenged
again the browser falls back to clicking "Download Lottie JSON".

  python3 ai-tools/fetch/iconscout_motion.py --tag security --tag network \
      --pages 1 --limit 60 --out assets/lottie/inbox

Needs a logged-in session in ~/.config/alur/iconscout.env (ICONSCOUT_COOKIE=...).
"""
import argparse
import json
import re
import shutil
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "browser"))
from iconscout_session import UA, Session  # noqa: E402

LIST_URL = "https://iconscout.com/free-lottie-animations/{tag}?page={page}"
API = "https://iconscout.com/api/v2/items/%s/download?"
LICENSE_BODY = {"format": "json", "license_id": 71, "source": "web"}

ITEMS_JS = """
(function(){
  var pre = 'https://iconscout.com/free-lottie-animation/';
  var out = [];
  document.querySelectorAll('script[type="application/ld+json"]').forEach(function(s){
    var d; try { d = JSON.parse(s.textContent); } catch (e) { return; }
    if (!d || d['@type'] !== 'ImageObject') return;
    var page = d.acquireLicensePage || '';
    if (page.indexOf(pre) !== 0) return;
    var rest = page.slice(pre.length), us = rest.lastIndexOf('_');
    if (us < 0) return;
    out.push({slug: rest.slice(0, us), item_id: parseInt(rest.slice(us + 1), 10),
      detail: page, name: (d.name || ''), author: ((d.creator || {}).name || ''),
      credit: (d.creditText || ''), license: (d.license || ''),
      copyright: (d.copyrightNotice || ''), preview: (d.contentUrl || '')});
  });
  return out;
})()
"""

# the page state is minified (id:bf,uuid:"..."), so hand back a slice and let
# Python pick the uuid out of it — a JS regex literal survived transport badly.
UUID_JS = """(function(){
  var h = document.documentElement.innerHTML;
  var i = h.indexOf('item:{');
  return i < 0 ? '' : h.slice(i, i + 160);
})()"""

UUID_RE = re.compile(r'uuid:"([0-9a-f-]{36})"')

CLICK_JS = """
(function(){
  var b = [].slice.call(document.querySelectorAll('button')).filter(function(x){
    return /^Download Lottie JSON/i.test((x.textContent || '').trim());
  })[0];
  if (!b) return 'no-button';
  b.click();
  return 'clicked';
})()
"""


def http_session(cookies):
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    for c in cookies:
        s.cookies.set(c["name"], c["value"], domain=c.get("domain") or ".iconscout.com",
                      path=c.get("path") or "/")
    return s


def save_from_api(s, item):
    r = s.post(API % item["uuid"], json=LICENSE_BODY, timeout=(10, 30),
               headers={"Referer": "https://iconscout.com/", "X-Requested-With": "XMLHttpRequest"})
    if r.status_code != 200:
        return None, "api %d" % r.status_code
    try:
        url = r.json().get("response", {}).get("download", {}).get("url")
    except ValueError:
        return None, "api envelope"
    if not url:
        return None, "no url"
    body = s.get(url, timeout=(10, 90))
    if body.status_code != 200 or not body.content:
        return None, "cdn %d" % body.status_code
    return body.content, ""


def save_via_browser(session, item, out, delay=1.5):
    if not session.open(item["detail"], timeout=25):
        return None, "challenge"
    session.ev("1")
    slice_ = session.ev(UUID_JS) or ""
    hit = UUID_RE.search(slice_)
    if not hit:
        return None, "no uuid"
    uuid = hit.group(1)
    item["uuid"] = uuid
    dl = out / "_dl"
    dl.mkdir(parents=True, exist_ok=True)
    session.cmd("Browser.setDownloadBehavior", behavior="allow", downloadPath=str(dl))
    before = {p.name for p in dl.iterdir()}
    if session.ev(CLICK_JS) != "clicked":
        return None, "no button"
    for _ in range(40):
        time.sleep(0.5)
        done = [p for p in dl.iterdir() if p.name not in before and not p.name.endswith(".crdownload")]
        if done:
            return done[0].read_bytes(), ""
    return None, "no file"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", action="append", default=None)
    ap.add_argument("--pages", type=int, default=1)
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "assets" / "lottie" / "inbox"))
    ap.add_argument("--delay", type=float, default=0.8)
    ap.add_argument("--headless", action="store_true")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    meta_path = out / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else []

    session = Session(headless=args.headless, log=lambda m: print(m, flush=True))
    s = http_session(session.cookies())
    try:
        items = []
        for tag in (args.tag or ["hacker"]):
            for page in range(1, args.pages + 1):
                if not session.open(LIST_URL.format(tag=tag, page=page), timeout=25):
                    print("%s page %d: challenge not cleared" % (tag, page), flush=True)
                    continue
                s = http_session(session.cookies())  # refresh cookies after a challenge
                got = session.ev(ITEMS_JS) or []
                print("%s page %d: %d items" % (tag, page, len(got)), flush=True)
                items.extend(got)
                time.sleep(0.6)

        known = {row.get("item_id") for row in meta}
        done = 0
        for item in items:
            if item["item_id"] in known or len(meta) >= args.limit:
                continue
            target = out / ("%s.json" % item["slug"])
            if target.is_file():
                meta.append(dict(item, file=target.name))
                known.add(item["item_id"])
                continue
            print("  · %s" % item["slug"], flush=True)
            # the uuid is not in the listing and the page state is minified, so
            # let the page itself do the download and read the file back
            data, why = save_via_browser(session, item, out, args.delay)
            if data is None:
                print("    ! %s (%s)" % (why, item["slug"]), flush=True)
                time.sleep(2.0)
                continue
            target.write_bytes(data)
            done += 1
            meta.append(dict(item, file=target.name))
            known.add(item["item_id"])
            meta_path.write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n",
                                 encoding="utf-8")
            print("    + %-44s %7d B  by %s" % (item["slug"], len(data), item["author"] or "?"),
                  flush=True)
            time.sleep(args.delay)
        print("new: %d, total meta: %d" % (done, len(meta)))
    finally:
        session.close()


if __name__ == "__main__":
    main()