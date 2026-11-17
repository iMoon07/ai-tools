"""Green verified mark: computed style + two-shot pixel diff of the ::before logo."""
import base64
import json
import subprocess
import sys
import tempfile
import time
import urllib.request

import websocket

W = int(sys.argv[1]) if len(sys.argv) > 1 else 390
PORT = 9915
tmp = tempfile.mkdtemp(prefix="ackmotion")
proc = subprocess.Popen([
    "chromium", "--no-sandbox", "--no-first-run", "--no-default-browser-check",
    "--window-position=0,0", "--window-size=%d,900" % (W + 40),
    "--disable-backgrounding-occluded-windows", "--disable-renderer-backgrounding",
    "--remote-debugging-port=%d" % PORT, "--remote-allow-origins=*",
    "--user-data-dir=" + tmp, "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(160):
    try:
        urllib.request.urlopen("http://127.0.0.1:%d/json/version" % PORT, timeout=1).read()
        break
    except Exception:
        time.sleep(0.25)
tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT).read())
c = websocket.create_connection([t for t in tabs if t["type"] == "page"][0]["webSocketDebuggerUrl"], timeout=60)
n = [0]


def cmd(m, **p):
    n[0] += 1
    c.send(json.dumps({"id": n[0], "method": m, "params": p}))
    while True:
        r = json.loads(c.recv())
        if r.get("id") == n[0]:
            return r.get("result", {})


def ev(e):
    r = cmd("Runtime.evaluate", expression=e, returnByValue=True).get("result", {})
    return r.get("value") if r.get("subtype") != "error" else {"__err": str(r.get("description"))[:200]}


def shot(tag):
    clip = ev("""(function(){
      var b=document.querySelector('[data-open-experience="recognition"]');
      var q=b.getBoundingClientRect(), d=getComputedStyle(b,'::before');
      var w=parseFloat(d.width), h=parseFloat(d.height);
      var x=q.left + parseFloat(d.left||'0'), y=q.top + parseFloat(d.top||'0');
      return {x:x, y:y, width:w, height:h, scale:2};
    })()""")
    if not isinstance(clip, dict) or "width" not in clip:
        print(tag, "clip failed:", clip)
        return None
    raw = cmd("Page.captureScreenshot", format="png",
              clip={"x": clip["x"], "y": clip["y"], "width": clip["width"],
                    "height": clip["height"], "scale": clip["scale"]},
              captureBeyondViewport=False).get("data")
    if not raw:
        print(tag, "no screenshot")
        return None
    data = base64.b64decode(raw)
    open("/tmp/alur-probes/ack_%s.png" % tag, "wb").write(data)
    return data


try:
    cmd("Page.enable")
    cmd("Runtime.enable")
    cmd("Emulation.setDeviceMetricsOverride", width=W, height=900, deviceScaleFactor=2, mobile=False)
    cmd("Page.navigate", url="http://127.0.0.1:8123/index.html#about")
    time.sleep(5.0)
    ev("document.getElementById('tabExperience').click()")
    time.sleep(1.0)
    info = ev("""(function(){
      var b=document.querySelector('[data-open-experience="recognition"]');
      var d=getComputedStyle(b,'::before');
      return {content:d.content, bg:d.backgroundImage, size:d.backgroundSize,
              color:d.backgroundColor, w:d.width, h:d.height, radius:d.borderRadius};
    })()""")
    print("ack ::before:", json.dumps(info))
    ev("window.scrollTo(0, document.querySelector('[data-open-experience=\"recognition\"]').getBoundingClientRect().top + scrollY - 120)")
    time.sleep(0.6)
    a = shot("a")
    time.sleep(1.2)
    b = shot("b")
    if a and b:
        from PIL import Image
        import io
        ia = Image.open(io.BytesIO(a)).convert("RGB")
        ib = Image.open(io.BytesIO(b)).convert("RGB")
        pa, pb = list(ia.getdata()), list(ib.getdata())
        changed = sum(1 for x, y in zip(pa, pb) if x != y)
        green = [p for p in pa if p[1] > p[0] + 24 and p[1] > p[2] + 24]
        print("frame %dx%d changed=%d greenPx=%d sample=%s" % (
            ia.width, ia.height, changed, len(green),
            sorted(set(green))[-1] if green else None))
finally:
    c.close()
    proc.terminate()