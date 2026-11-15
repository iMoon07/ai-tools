import json, sys, time, urllib.request, subprocess, tempfile
import websocket

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9863
tmp = tempfile.mkdtemp(prefix="zchk")
proc = subprocess.Popen([
    "chromium", "--headless=new", "--disable-gpu", "--no-sandbox",
    "--remote-debugging-port=%d" % PORT, "--remote-allow-origins=*",
    "--user-data-dir=" + tmp, "--window-size=1600,1000", "about:blank",
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
            if "error" in msg:
                print("CDP ERROR", method, msg["error"])
            return msg.get("result", {})

def ev(expr):
    r = cmd("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
    res = r.get("result", {})
    if res.get("subtype") == "error":
        print("JS ERROR:", res.get("description"))
    return res.get("value")

errs = []
def hook():
    ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")

cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride", width=1600, height=1000, deviceScaleFactor=1, mobile=False)

cmd("Page.navigate", url="http://127.0.0.1:8123/draw.html")
time.sleep(3)
hook()
ev("""localStorage.setItem('ruang.canvas.v1', JSON.stringify(Object.assign(JSON.parse(localStorage.getItem('ruang.canvas.v1')||'{}'), {zoom: 2.57}))); 'ok'""")
cmd("Page.reload")
time.sleep(3.5)
hook()

def state():
    return ev("""(function(){
      var svg=document.querySelector('#stage svg');
      var vb=(svg.getAttribute('viewBox')||'').split(' ').map(Number);
      return {pct:(document.getElementById('zoomVal')||{}).textContent,
              top:(document.getElementById('topStatus')||{}).textContent,
              vbW:vb[2], zoom: vb[2] ? Math.round(1600/vb[2]*1000)/1000 : null,
              panX:vb[0], panY:vb[1]};
    })()""")

def wheel(dx, dy, ctrl=False, shift=False):
    return ev("""(function(){
      var s=document.getElementById('stage'); var r=s.getBoundingClientRect();
      s.dispatchEvent(new WheelEvent('wheel',{bubbles:true,cancelable:true,
        clientX:r.left+r.width/2, clientY:r.top+r.height/2,
        deltaX:%d, deltaY:%d, ctrlKey:%s, shiftKey:%s, deltaMode:0}));
      return true;
    })()""" % (dx, dy, 'true' if ctrl else 'false', 'true' if shift else 'false'))

print("seed 257%   ->", state())

w = wheel(0, 120); time.sleep(0.25); print("plain wheel  ->", state())
wheel(0, 120, shift=True); time.sleep(0.25); print("shift wheel  ->", state())
wheel(0, -120, ctrl=True); time.sleep(0.25); print("ctrl up x1   ->", state())
wheel(0, -120, ctrl=True); time.sleep(0.25); print("ctrl up x2   ->", state())

for _ in range(15):
    wheel(0, -120, ctrl=True); time.sleep(0.04)
print("ctrl up x17  ->", state())

low = None
for _ in range(80):
    wheel(0, 120, ctrl=True); time.sleep(0.03)
print("ctrl down x80->", state())

ev("document.dispatchEvent(new KeyboardEvent('keydown',{key:'0',ctrlKey:true,bubbles:true}))")
time.sleep(0.3); print("Ctrl+0       ->", state())
ev("document.dispatchEvent(new KeyboardEvent('keydown',{key:'1',shiftKey:true,bubbles:true}))")
time.sleep(0.4); print("Shift+1 fit  ->", state())

print("doc:", ev("({sw:document.documentElement.scrollWidth, iw:innerWidth, sh:document.documentElement.scrollHeight, ih:innerHeight})"))
print("errors:", ev("window.__errs || []"))
c.close(); proc.terminate()
try: proc.wait(timeout=5)
except Exception: proc.kill()