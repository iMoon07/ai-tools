#!/usr/bin/env python3
"""Download free Lottie animations from IconScout through a real browser.

Plain HTTP gets a Cloudflare challenge after a few dozen requests, so the
listing and the download both run in Chromium with the logged-in session from
~/.config/alur/iconscout.env (ICONSCOUT_COOKIE=...). The cookie is read from
that file only and never printed.

  python3 ai-tools/fetch/iconscout_motion_browser.py --tag security --pages 1 \
      --out assets/lottie/inbox
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import websocket

PORT = 9896
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0"
LIST_URL = "https://iconscout.com/free-lottie-animations/{tag}?page={page}"

ITEMS_JS = """
(function(){
  var pre = 'https://iconscout.com/free-lottie-animation/';
  var out = [];
  document.querySelectorAll('script[type="application/ld+json"]').forEach(function(s){
    var d;
    try { d = JSON.parse(s.textContent); } catch (e) { return; }
    if (!d || d['@type'] !== 'ImageObject') return;
    var page = d.acquireLicensePage || '';
    if (page.indexOf(pre) !== 0) return;
    var rest = page.slice(pre.length);
    var us = rest.lastIndexOf('_');
    if (us < 0) return;
    out.push({slug: rest.slice(0, us), item_id: parseInt(rest.slice(us + 1), 10),
      detail: page, name: (d.name || ''), author: ((d.creator || {}).name || ''),
      credit: (d.creditText || ''), license: (d.license || ''),
      copyright: (d.copyrightNotice || ''), preview: (d.contentUrl || '')});
  });
  return out;
})()
"""

DOWNLOAD_JS = """
(function(){
  var b = [].slice.call(document.querySelectorAll('button')).filter(function(x){
    return /^Download Lottie JSON/i.test((x.textContent || '').trim());
  })[0];
  if (!b) return 'no-button';
  b.click();
  return 'clicked';
})()
"""


def load_cookie(path):
    env = Path(path).expanduser()
    if not env.is_file():
        sys.exit("missing %s (ICONSCOUT_COOKIE=...)" % env)
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("ICONSCOUT_COOKIE="):
            return line.split("=", 1)[1].strip().strip("'\"")
    sys.exit("ICONSCOUT_COOKIE not found in %s" % env)


class Browser:
    def __init__(self, cookie, download_dir):
        self.dl = Path(download_dir)
        self.dl.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.mkdtemp(prefix="icdl")
        self.proc = subprocess.Popen(["chromium", "--no-sandbox", "--no-first-run",
            "--disable-blink-features=AutomationControlled", "--window-position=0,0",
            "--window-size=1400,900", "--remote-debugging-port=%d" % PORT,
            "--remote-allow-origins=*", "--user-data-dir=" + self.tmp, "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(160):
            try:
                urllib.request.urlopen("http://127.0.0.1:%d/json/version" % PORT, timeout=1).read()
                break
            except Exception:
                time.sleep(0.25)
        tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT).read())
        page = [t for t in tabs if t["type"] == "page"][0]
        self.ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=120)
        self.i = 0
        self.cmd("Network.enable")
        self.cmd("Network.setCookies", cookies=[{
            "name": k.strip(), "value": v.strip(), "domain": ".iconscout.com", "path": "/"}
            for k, v in (p.split("=", 1) for p in cookie.split(";") if "=" in p)])
        self.cmd("Network.setUserAgentOverride", userAgent=UA,
                 acceptLanguage="en-US,en;q=0.9", platform="Linux x86_64")
        self.cmd("Browser.setDownloadBehavior", behavior="allow", downloadPath=str(self.dl))

    def cmd(self, method, **params):
        self.i += 1
        self.ws.send(json.dumps({"id": self.i, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.i:
                return msg.get("result", {})

    def ev(self, expr):
        res = self.cmd("Runtime.evaluate", expression=expr, returnByValue=True,
                       awaitPromise=True).get("result", {})
        if res.get("subtype") == "error":
            return {"__err": str(res.get("description"))[:200]}
        return res.get("value")

    def goto(self, url, wait=3.0):
        self.cmd("Page.navigate", url=url)
        for _ in range(int(wait * 4) + 8):
            time.sleep(0.25)
            title = self.ev("document.title") or ""
            if "Just a moment" not in title and title:
                break
        time.sleep(0.4)

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass
        self.proc.terminate()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", action="append", default=None)
    ap.add_argument("--pages", type=int, default=1)
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "assets" / "lottie" / "inbox"))
    ap.add_argument("--cookie-file", default="~/.config/alur/iconscout.env")
    ap.add_argument("--delay", type=float, default=1.6)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    meta_path = out / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else []

    browser = Browser(load_cookie(args.cookie_file), out / "_dl")
    try:
        items = []
        for tag in (args.tag or ["hacker"]):
            for page in range(1, args.pages + 1):
                browser.goto(LIST_URL.format(tag=tag, page=page))
                got = browser.ev(ITEMS_JS) or []
                if isinstance(got, dict):
                    sys.exit("listing failed: %s" % got)
                print("%s page %d: %d items" % (tag, page, len(got)), flush=True)
                items.extend(got)
                time.sleep(0.8)

        known = {row.get("item_id") for row in meta}
        for item in items:
            if item["item_id"] in known or len(meta) >= args.limit:
                continue
            target = out / ("%s.json" % item["slug"])
            print("  · %s" % item["slug"], flush=True)
            if not target.is_file():
                before = set(p.name for p in (out / "_dl").iterdir())
                browser.goto(item["detail"], wait=2.5)
                status = browser.ev(DOWNLOAD_JS)
                if status != "clicked":
                    print("    ! %s (%s)" % (status, item["slug"]), flush=True)
                    continue
                saved = None
                for _ in range(30):
                    time.sleep(0.5)
                    new = [p for p in (out / "_dl").iterdir() if p.name not in before]
                    done = [p for p in new if not p.name.endswith(".crdownload")]
                    if done:
                        saved = done[0]
                        break
                if not saved:
                    print("    ! no file for %s" % item["slug"], flush=True)
                    continue
                shutil.move(str(saved), str(target))
                time.sleep(args.delay)
            meta.append({
                "slug": item["slug"], "item_id": item["item_id"], "name": item["name"],
                "author": item["author"], "credit": item["credit"], "license": item["license"],
                "copyright": item["copyright"], "source": item["detail"],
                "preview": item["preview"], "file": target.name,
            })
            known.add(item["item_id"])
            meta_path.write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n",
                                 encoding="utf-8")
            print("    + %-44s %7d B  by %s" % (item["slug"], target.stat().st_size,
                                                item["author"] or "?"), flush=True)
    finally:
        browser.close()
    print("total: %d -> %s" % (len(meta), out))


if __name__ == "__main__":
    main()