#!/usr/bin/env python3
"""Render Lottie JSON to an animated WebP the canvas can use.

The Alur renderer paints logos as <image href>, and a Lottie JSON cannot run
there: scripts and JS animation are not allowed inside an SVG image. An
animated WebP does animate in that slot (verified: Chromium repaints it), so
each JSON is rendered frame by frame with lottie-web and re-encoded.

  python3 ai-tools/generators/lottie_to_webp.py --in logo/_inbox/lottie \
      --out logo/motion --fps 12 --seconds 4 --size 64
"""
import argparse
import base64
import io
import json
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

VENDOR = Path(__file__).resolve().parent.parent / "vendor" / "lottie.min.js"
PORT = 9893


def start_chromium():
    tmp = tempfile.mkdtemp(prefix="lot")
    proc = subprocess.Popen(["chromium", "--headless=new", "--disable-gpu", "--no-sandbox",
        "--hide-scrollbars", "--window-size=400,400", "--remote-debugging-port=%d" % PORT,
        "--remote-allow-origins=*", "--user-data-dir=" + tmp, "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(120):
        try:
            urllib.request.urlopen("http://127.0.0.1:%d/json/version" % PORT, timeout=1).read()
            return proc
        except Exception:
            time.sleep(0.25)
    proc.terminate()
    sys.exit("chromium did not start")


class Page:
    def __init__(self):
        import websocket
        tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT).read())
        page = [t for t in tabs if t["type"] == "page"][0]
        self.ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=120)
        self.i = 0

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
            raise RuntimeError(res.get("description", "eval failed")[:300])
        return res.get("value")

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass


# lottie's canvas renderer builds its own <canvas> inside the container, so the
# container must be an element with a size, never the canvas itself.
HARNESS = """
(function(){
  if (window.__anim && window.__anim.destroy) { try { window.__anim.destroy(); } catch (e) {} }
  var box = document.getElementById('box') || (function(){
    var d = document.createElement('div');
    d.id = 'box';
    d.style.cssText = 'width:%dpx;height:%dpx';
    document.body.appendChild(d);
    return d;
  })();
  box.innerHTML = '';
  var anim = lottie.loadAnimation({
    container: box, renderer: 'canvas', loop: false, autoplay: false,
    animationData: window.__data,
    rendererSettings: { clearCanvas: true, preserveAspectRatio: 'xMidYMid meet' }
  });
  window.__anim = anim;
  return {total: anim.totalFrames, fps: anim.frameRate};
})()
"""


def render(page, data, size, fps, seconds):
    payload = json.dumps(data, separators=(",", ":"))
    page.ev("window.__data = " + payload + "; 1")
    info = page.ev(HARNESS % (size, size))
    total = float(info.get("total") or 0)
    native = float(info.get("fps") or 30) or 30
    # play at the animation's own speed, take `seconds` worth of frames
    step = max(1.0, native / max(1.0, fps))
    count = max(2, int(round(seconds * fps)))
    out = []
    for k in range(count):
        frame = min(total - 0.01, k * step)
        if frame < 0:
            break
        page.ev("window.__anim.goToAndStop(%f, true); 1" % frame)
        url = page.ev("(function(){var c= document.querySelectorAll('#box canvas');"
                      " return c.length ? c[c.length-1].toDataURL('image/png') : '';})()")
        out.append(base64.b64decode(url.split(",", 1)[1]))
    return out, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", default="/home/moon/Projects/logo/_inbox/lottie")
    ap.add_argument("--out", default="/home/moon/Projects/logo/motion")
    ap.add_argument("--fps", type=float, default=12)
    ap.add_argument("--seconds", type=float, default=4)
    ap.add_argument("--size", type=int, default=64)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--quality", type=int, default=72)
    args = ap.parse_args()

    from PIL import Image

    src = Path(args.src)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    files = sorted(src.glob("*.json"))
    if args.limit:
        files = files[: args.limit]
    print("rendering %d files -> %s" % (len(files), out))

    proc = start_chromium()
    page = Page()
    page.cmd("Page.enable")
    page.cmd("Runtime.enable")
    page.ev("document.write('<body style=margin:0>')")
    page.ev((VENDOR.read_text(encoding="utf-8", errors="ignore")))
    if page.ev("typeof lottie") != "object":
        sys.exit("lottie-web did not load")

    made, failed = 0, []
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            failed.append((path.name, "bad json: %s" % exc))
            continue
        if not isinstance(data, dict) or "layers" not in data:
            failed.append((path.name, "not a lottie file"))
            continue
        try:
            pngs, total = render(page, data, args.size, args.fps, args.seconds)
        except Exception as exc:
            failed.append((path.name, str(exc)[:120]))
            continue
        ims = [Image.open(io.BytesIO(p)).convert("RGBA") for p in pngs]
        ims = [im for im in ims if im.getbbox()]
        if not ims:
            failed.append((path.name, "empty frames"))
            continue
        delay = int(round(1000 / args.fps))
        target = out / (path.stem + ".webp")
        ims[0].save(target, "WEBP", save_all=True, append_images=ims[1:], loop=0,
                    duration=delay, quality=args.quality, method=4, allow_mixed=True)
        made += 1
        print("  + %-42s %3d frames %6d B" % (target.name, len(ims), target.stat().st_size))

    page.close()
    proc.terminate()
    print("done: %d rendered, %d failed" % (made, len(failed)))
    for name, why in failed[:12]:
        print("  ! %s: %s" % (name, why))


if __name__ == "__main__":
    main()