#!/usr/bin/env python3
"""Search Google from a real, persistent browser and survive the /sorry/ page.

Google answers automated search with a reCAPTCHA interstitial
(/sorry/index?continue=...). The only reliable way through is a human solving
it once in a real browser, so this tool keeps one headed Chromium alive on a
persistent profile, parks on the challenge, and waits for it to clear:

  python3 ai-tools/fetch/google_search.py "anubis" --out snapshots/google/g.json
  python3 ai-tools/fetch/google_search.py "anubis" --wait 300 --num 20

The profile (~/.cache/alur/google-profile) keeps the solve, so later runs start
clean. --headless exists but will not clear /sorry/; it is there for debugging.

An IP that is already flagged stays flagged, so waiting on a human is often a
dead end. For that case the tool degrades: when Google answers /sorry/ and no
human clears it, the same query is retried on DuckDuckGo (HTML endpoint) and
Bing over plain HTTPS, which need no captcha. --engines picks the order.
"""
import argparse
import base64
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import websocket

PORT = 9899
PROFILE = Path.home() / ".cache" / "alur" / "google-profile"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/131.0.0.0 Safari/537.36")
CHALLENGE_URL = "/sorry/"
CHALLENGE_TEXT = ("unusual traffic", "our systems have detected", "recaptcha")
UA_HTTP = UA
ENGINES = ("google", "ddg", "bing")

RESULTS_JS = """
(function(){
  var out = [], seen = {};
  document.querySelectorAll('div#search div, div#rso div').forEach(function(blk){
    var h = blk.querySelector('a h3');
    if (!h) return;
    var a = h.closest('a');
    var href = a ? a.href : '';
    if (!href || href.indexOf('http') !== 0 || seen[href]) return;
    var title = (h.textContent || '').trim();
    if (!title || title.length < 4) return;
    seen[href] = 1;
    var p = blk.querySelector('[data-sncf], .VwiC3b, .lEBKkf, span');
    out.push({title: title, url: href, snippet: p ? (p.textContent || '').trim().slice(0, 300) : ''});
  });
  return out;
})()
"""


def _http_get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA_HTTP,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")


def _unquote_uddg(href):
    i = href.find("uddg=")
    if i < 0:
        return href
    return urllib.parse.unquote(href[i + 5:].split("&")[0])


def _strip(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def _query_tokens(query):
    stop = {"the", "a", "an", "of", "for", "and", "in", "on", "to", "with", "free"}
    return {t for t in re.findall(r"[a-z0-9]{3,}", query.lower()) if t not in stop}


def _relevant(row, tokens):
    """Bing sometimes answers a datacenter IP with results for an unrelated
    query; drop rows that share no term with what we asked for."""
    if not tokens:
        return True
    hay = (row["title"] + " " + row["snippet"]).lower()
    return any(t in hay for t in tokens)


def _unbind_bing(href):
    if "bing.com/ck/a" not in href:
        return href
    m = re.search(r"[?&]u=a1([^&]+)", href)
    if not m:
        return href
    raw = urllib.parse.unquote(m.group(1))
    raw += "=" * (-len(raw) % 4)
    try:
        return base64.urlsafe_b64decode(raw).decode("utf-8", "replace")
    except Exception:
        return href


def _parse_ddg(html, start):
    rows, seen = [], set()
    for m in re.finditer(r'<a\b[^>]*class="[^"]*result__a[^"]*"[^>]*>(.*?)</a>', html, re.S):
        tag = html[m.start():m.start(1)]
        hm = re.search(r'href="([^"]+)"', tag)
        if not hm:
            continue
        url = _unquote_uddg(hm.group(1).replace("&amp;", "&"))
        title = _strip(m.group(1))
        if not url.startswith("http") or not title or url in seen:
            continue
        seen.add(url)
        tail = html[m.end():m.end() + 4000]
        s = re.search(r'class="result__snippet"[^>]*>(.*?)</a>', tail, re.S)
        snip = _strip(s.group(1)) if s else ""
        rows.append({"title": title, "url": url, "snippet": snip[:300]})
    return rows


def _parse_bing(html, start, tokens=None):
    rows, seen = [], set()
    for blk in html.split('class="b_algo"')[1:]:
        m = re.search(r'<h2[^>]*>\s*<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', blk, re.S)
        if not m:
            continue
        url = _unbind_bing(m.group(1).replace("&amp;", "&"))
        title = _strip(m.group(2))
        if not url.startswith("http") or not title or url in seen:
            continue
        s = re.search(r'<p[^>]*>(.*?)</p>', blk, re.S)
        snip = _strip(s.group(1)) if s else ""
        row = {"title": title, "url": url, "snippet": snip[:300]}
        if not _relevant(row, tokens):
            continue
        seen.add(url)
        rows.append(row)
    return rows


def http_search(engine, query, num, start):
    tokens = _query_tokens(query)
    if engine == "ddg":
        url = "https://html.duckduckgo.com/html/?%s" % urllib.parse.urlencode(
            {"q": query, "s": start, "dc": start + 1})
        parse = _parse_ddg
    else:
        url = "https://www.bing.com/search?%s" % urllib.parse.urlencode(
            {"q": query, "count": min(max(num, 10), 50), "first": start + 1, "setlang": "en"})
        parse = _parse_bing
    try:
        html = _http_get(url)
    except Exception as e:
        return {"query": query, "start": start, "engine": engine,
                "error": "%s: %s" % (type(e).__name__, str(e)[:120])}
    if "result__a" not in html and "b_algo" not in html:
        return {"query": query, "start": start, "engine": engine,
                "error": "no results in page (%d bytes)" % len(html)}
    rows = parse(html, start) if engine == "ddg" else parse(html, start, tokens)
    if not rows:
        return {"query": query, "start": start, "engine": engine,
                "error": "parsed 0 results"}
    return {"query": query, "start": start, "engine": engine, "results": rows}


class Session:
    def __init__(self, port=PORT, headless=False, log=print):
        self.log = log
        PROFILE.parent.mkdir(parents=True, exist_ok=True)
        args = ["chromium", "--no-sandbox", "--no-first-run", "--no-default-browser-check",
                "--disable-blink-features=AutomationControlled", "--window-position=0,0",
                "--window-size=1400,900", "--lang=en-US",
                "--remote-debugging-port=%d" % port, "--remote-allow-origins=*",
                "--user-data-dir=%s" % PROFILE, "about:blank"]
        if headless:
            args.insert(1, "--headless=new")
        self.proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(200):
            try:
                urllib.request.urlopen("http://127.0.0.1:%d/json/version" % port, timeout=1).read()
                break
            except Exception:
                time.sleep(0.25)
        tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json" % port).read())
        page = [t for t in tabs if t["type"] == "page"][0]
        self.ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=300)
        self.i = 0
        self.cmd("Page.enable")
        self.cmd("Runtime.enable")
        self.cmd("Network.enable")
        self.cmd("Network.setUserAgentOverride", userAgent=UA, acceptLanguage="en-US,en;q=0.9",
                 platform="Linux x86_64")

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

    def url(self):
        return (self.ev("location.href") or "")

    def title(self):
        return (self.ev("document.title") or "").strip()

    def open(self, url, settle=3.0):
        self.cmd("Page.navigate", url=url)
        time.sleep(settle)

    def challenged(self):
        href = self.url()
        if CHALLENGE_URL in href:
            return True
        if self.title().lower().startswith("about this page"):
            return True
        head = (self.ev("document.body ? document.body.innerText.slice(0,1200) : ''") or "")
        return any(t in head.lower() for t in CHALLENGE_TEXT)

    def logged_in(self):
        return bool(self.ev("(document.cookie.indexOf('__Secure-1PSID') >= 0) ? 1 : 0"))

    def wait_login(self, timeout):
        """Hold the window open until a human signs in to Google."""
        self.log("    sign in to Google in the window (waiting up to %ds)" % int(timeout))
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.logged_in():
                self.log("    signed in")
                return True
            time.sleep(3.0)
        return self.logged_in()

    def wait_solved(self, timeout):
        """Block until the human clears the captcha, or the clock runs out."""
        deadline = time.time() + timeout
        last = -1
        while time.time() < deadline:
            left = int(deadline - time.time())
            if not self.challenged():
                return True
            if left != last:
                self.log("    captcha up, %ds left - solve it in the window" % left)
                last = left
            time.sleep(2.0)
        return not self.challenged()

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass
        self.proc.terminate()


def search(session, query, num, start, wait, tries=3, engines=ENGINES, log=print):
    order = [e for e in engines]
    last = {}
    for engine in order:
        if engine == "google":
            page = google_search_page(session, query, num, start, wait, tries, log)
        else:
            page = http_search(engine, query, num, start)
        if not page.get("error"):
            page.setdefault("engine", engine)
            return page
        last = page
        log("  ! %s: %s -> falling back" % (engine, page.get("error")))
    return last or {"query": query, "start": start, "error": "no engine tried"}


def google_search_page(session, query, num, start, wait, tries=3, log=print):
    url = "https://www.google.com/search?%s" % urllib.parse.urlencode(
        {"q": query, "num": num, "start": start, "hl": "en", "gbv": 1})
    for attempt in range(1, tries + 1):
        session.open(url)
        if session.challenged():
            if wait <= 0 or not session.wait_solved(wait):
                return {"query": query, "start": start, "engine": "google",
                        "error": "captcha not cleared"}
            continue
        rows = session.ev(RESULTS_JS) or []
        if isinstance(rows, dict) and rows.get("__err"):
            return {"query": query, "start": start, "engine": "google",
                    "error": rows["__err"]}
        return {"query": query, "start": start, "engine": "google", "results": rows}
    return {"query": query, "start": start, "engine": "google",
            "error": "captcha not cleared"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--num", type=int, default=10)
    ap.add_argument("--pages", type=int, default=1)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--wait", type=float, default=0.0,
                    help="seconds to wait for a human to clear the Google captcha "
                         "(0 = skip straight to the fallback engines)")
    ap.add_argument("--engines", default=",".join(ENGINES),
                    help="comma list tried in order; google needs the browser, "
                         "ddg/bing are plain HTTPS")
    ap.add_argument("--out", default="")
    ap.add_argument("--headless", action="store_true")
    ap.add_argument("--login", action="store_true",
                    help="open Google and wait for a human to sign in, then exit")
    args = ap.parse_args()

    engines = [e.strip() for e in args.engines.split(",") if e.strip()]
    pages = []
    if "google" in engines:
        session = Session(headless=args.headless)
        try:
            if args.login:
                session.open("https://accounts.google.com/ServiceLogin?hl=en", settle=2.0)
                session.wait_login(600)
                print("signed in: %s" % session.logged_in())
                return
            pages = [search(session, args.query, args.num,
                            args.start + i * args.num, args.wait,
                            engines=engines, log=print)
                     for i in range(max(1, args.pages))]
        finally:
            session.close()
    else:
        pages = [search(None, args.query, args.num, args.start + i * args.num,
                        args.wait, engines=engines, log=print)
                 for i in range(max(1, args.pages))]

    for page in pages:
        if page.get("error"):
            print("  ! %s (start %d): %s" % (page["query"], page["start"], page["error"]))
            continue
        print("  %s (start %d) via %s: %d hits"
              % (page["query"], page["start"], page.get("engine", "?"), len(page["results"])))
        for row in page["results"]:
            print("    - %s\n      %s" % (row["title"][:88], row["url"][:120]))

    if args.out:
        Path(args.out).write_text(json.dumps(pages, indent=1, ensure_ascii=False) + "\n",
                                  encoding="utf-8")
        print("wrote %s" % args.out)


if __name__ == "__main__":
    main()