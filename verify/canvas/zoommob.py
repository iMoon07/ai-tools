import json, sys, time, urllib.request, subprocess, tempfile
import websocket

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9866
W, H = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (390, 844)
tmp = tempfile.mkdtemp(prefix="zmob")
proc = subprocess.Popen([
    "chromium", "--headless=new", "--disable-gpu", "--no-sandbox",
    "--remote-debugging-port=%d" % PORT, "--remote-allow-origins=*",
    "--user-data-dir=" + tmp, "--window-size=%d,%d" % (W, H), "about:blank",
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def wait():
    for _ in range(80):
        try:
            urllib.request.urlopen("http://127.0.0.1:%d/json/version" % PORT, timeout=1).read()
            return True
        except Exception:
            time.sleep(0.25)
    return False

if not wait():
    print("no cdp"); sys.exit(1)

tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT).read())
page = [t for t in tabs if t["type"] == "page"][0]
c = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=30)
i = [0]
def cmd(method, **params):
    i[0] += 1
    c.send(json.dumps({"id": i[0], "method": method, "params": params}))
    while True:
        msg = json.loads(c.recv())
        if msg.get("id") == i[0]:
            return msg.get("result", {})
def ev(expr):
    r = cmd("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
    res = r.get("result", {})
    if res.get("subtype") == "error":
        print("JS ERROR:", res.get("description"))
    return res.get("value")

cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride", width=W, height=H, deviceScaleFactor=1, mobile=True)
cmd("Page.navigate", url="http://127.0.0.1:8123/draw.html")
time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")
ev("""localStorage.setItem('ruang.canvas.v1', JSON.stringify(Object.assign(JSON.parse(localStorage.getItem('ruang.canvas.v1')||'{}'), {zoom: 2.57}))); 'ok'""")
cmd("Page.reload"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")

print("viewport", W, "x", H, "->", ev("""(function(){
  var svg=document.querySelector('#stage svg');
  var vb=(svg.getAttribute('viewBox')||'').split(' ').map(Number);
  var zv=document.getElementById('zoomVal');
  return {pct:zv?zv.textContent.trim():'?', tag:zv?zv.tagName:'-',
          zoom: vb[2] ? Math.round(%d/vb[2]*1000)/1000 : null};
})()""" % W))

# click the zoom readout -> 100%
ev("document.getElementById('zoomVal').click()"); time.sleep(0.4)
print("after zoomVal click ->", ev("(function(){var svg=document.querySelector('#stage svg');var vb=(svg.getAttribute('viewBox')||'').split(' ').map(Number);return {pct:document.getElementById('zoomVal').textContent.trim(), zoom:vb[2]?Math.round(%d/vb[2]*1000)/1000:null};})()" % W))

# tap target of the new button
print("zoomVal box ->", ev("""(function(){var b=document.getElementById('zoomVal').getBoundingClientRect();return {w:Math.round(b.width),h:Math.round(b.height)};})()"""))

print("doc ->", ev("({sw:document.documentElement.scrollWidth, iw:innerWidth})"))
print("errors:", ev("window.__errs || []"))
c.close(); proc.terminate()
try: proc.wait(timeout=5)
except Exception: proc.kill()