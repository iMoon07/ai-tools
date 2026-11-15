#!/usr/bin/env python3
"""A Cloudflare-tolerant browsing session for IconScout.

Cloudflare answers the first few plain requests and then switches to a managed
challenge ("Just a moment..."). A real browser clears that by itself, so this
module keeps one headed Chromium alive, waits for the challenge to pass, and
persists the profile so later runs start already cleared. The resulting
cookies are exported so the fast `requests` path can be used until the next
challenge.

  python3 -m iconscout_session --url https://iconscout.com/free-lottie-animations/security
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import websocket

PORT = 9897
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0"
PROFILE = Path.home() / ".cache" / "alur" / "iconscout-profile"
STATE = Path.home() / ".config" / "alur" / "iconscout-state.json"
CHALLENGE = "just a moment"


def load_cookie(path="~/.config/alur/iconscout.env"):
    env = Path(path).expanduser()
    if not env.is_file():
        sys.exit("missing %s (ICONSCOUT_COOKIE=...)" % env)
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("ICONSCOUT_COOKIE="):
            return line.split("=", 1)[1].strip().strip("'\"")
    sys.exit("ICONSCOUT_COOKIE not found in %s" % env)


class Session:
    def __init__(self, port=PORT, headless=False, profile=PROFILE, log=print):
        self.log = log
        PROFILE.parent.mkdir(parents=True, exist_ok=True)
        STATE.parent.mkdir(parents=True, exist_ok=True)
        self.tmp = None
        args = ["chromium", "--no-sandbox", "--no-first-run", "--no-default-browser-check",
                "--disable-blink-features=AutomationControlled", "--window-position=0,0",
                "--window-size=1400,900", "--remote-debugging-port=%d" % port,
                "--remote-allow-origins=*", "--user-data-dir=%s" % profile, "about:blank"]
        if headless:
            args.insert(1, "--headless=new")
        self.proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(160):
            try:
                urllib.request.urlopen("http://127.0.0.1:%d/json/version" % port, timeout=1).read()
                break
            except Exception:
                time.sleep(0.25)
        tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json" % port).read())
        page = [t for t in tabs if t["type"] == "page"][0]
        self.ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=180)
        self.i = 0
        self.cmd("Page.enable")
        self.cmd("Runtime.enable")
        self.cmd("Network.enable")
        self.cmd("Network.setUserAgentOverride", userAgent=UA,
                 acceptLanguage="en-US,en;q=0.9", platform="Linux x86_64")
        self.seed_cookies()

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

    def seed_cookies(self):
        raw = load_cookie()
        for part in raw.split(";"):
            if "=" not in part:
                continue
            k, v = part.split("=", 1)
            self.cmd("Network.setCookie", name=k.strip(), value=v.strip(),
                     domain=".iconscout.com", path="/")

    def title(self):
        return (self.ev("document.title") or "").strip()

    def wait_clear(self, timeout=25.0, reloads=2):
        """Wait for the managed challenge to clear itself, reloading if needed."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if CHALLENGE not in self.title().lower():
                return True
            time.sleep(0.5)
        for attempt in range(reloads):
            self.log("    challenge still up, reload %d" % (attempt + 1))
            self.cmd("Page.reload", ignoreCache=False)
            deadline = time.time() + timeout
            while time.time() < deadline:
                if CHALLENGE not in self.title().lower():
                    return True
                time.sleep(0.5)
        return False

    def open(self, url, timeout=25.0, reloads=2):
        self.cmd("Page.navigate", url=url)
        ok = self.wait_clear(timeout=timeout, reloads=reloads)
        self.save_state()
        return ok

    def save_state(self):
        try:
            cookies = self.cmd("Network.getAllCookies").get("cookies", [])
            STATE.write_text(json.dumps({
                "ua": UA,
                "saved": time.time(),
                "cookies": [{"name": c["name"], "value": c["value"], "domain": c["domain"],
                             "path": c.get("path", "/")} for c in cookies
                            if "iconscout" in (c.get("domain") or "")],
            }, indent=1), encoding="utf-8")
        except Exception as exc:  # state is an optimisation, never fatal
            self.log("    (cookie state not saved: %s)" % exc)

    def cookies(self):
        try:
            state = json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            return []
        return state.get("cookies", [])

    def close(self):
        try:
            self.save_state()
            self.ws.close()
        except Exception:
            pass
        self.proc.terminate()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="https://iconscout.com/free-lottie-animations/security")
    ap.add_argument("--headless", action="store_true")
    args = ap.parse_args()
    s = Session(headless=args.headless)
    try:
        ok = s.open(args.url, timeout=30)
        print("title:", s.title())
        print("cleared:", ok)
        print("cookies:", len(s.cookies()))
    finally:
        s.close()


if __name__ == "__main__":
    main()