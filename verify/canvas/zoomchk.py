import json, os, socket, subprocess, sys, tempfile, time, urllib.request

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9861
tmp = tempfile.mkdtemp(prefix="zchk")
proc = subprocess.Popen([
    "chromium", "--headless=new", "--disable-gpu", "--no-sandbox",
    "--remote-debugging-port=%d" % PORT, "--remote-allow-origins=*", "--user-data-dir=" + tmp,
    "--window-size=1600,1000", "about:blank",
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def wait():
    for _ in range(80):
        try:
            urllib.request.urlopen("http://127.0.0.1:%d/json/version" % PORT, timeout=1).read()
            return True
        except Exception:
            time.sleep(0.25)
    return False

def ws():
    import websocket
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT).read())
    page = [t for t in tabs if t["type"] == "page"][0]
    return websocket.create_connection(page["webSocketDebuggerUrl"], timeout=30)

def cmd(c, i, method, **params):
    i += 1
    c.send(json.dumps({"id": i, "method": method, "params": params}))
    while True:
        msg = json.loads(c.recv())
        if msg.get("id") == i:
            return msg.get("result", {})

def ev(c, i, expr):
    r = cmd(c, i, "Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
    return r.get("result", {}).get("value")

try:
    if not wait():
        print("no cdp"); sys.exit(1)
    c = ws(); i = 0
    cmd(c, i, "Page.enable"); cmd(c, i, "Runtime.enable")
    cmd(c, i, "Emulation.setDeviceMetricsOverride", width=1600, height=1000,
        deviceScaleFactor=1, mobile=False)

    # seed a scene whose persisted zoom is absurd (257%)
    cmd(c, i, "Page.navigate", url="http://127.0.0.1:8123/draw.html")
    time.sleep(3)
    ev(c, i, """localStorage.setItem('ruang.canvas.v1', JSON.stringify(Object.assign(JSON.parse(localStorage.getItem('ruang.canvas.v1')||'{}'), {zoom: 2.57, panX: 0, panY: 0}))); 'ok'""")
    cmd(c, i, "Page.reload")
    time.sleep(3.5)

    out = ev(c, i, """(function(){
      var g = function(){ var e=document.getElementById('zoomVal'); return e?e.textContent.trim():'?'; };
      return { zoomVal:g(), top:(document.getElementById('topStatus')||{}).textContent, spec:JSON.parse(localStorage.getItem('ruang.canvas.v1')||'{}').zoom };
    })()""")
    print("seed 257% ->", out)

    # wheel over canvas centre (plain) must pan only
    def wheel(dx, dy, ctrl=False, shift=False):
        return ev(c, i, """(function(){
          var s=document.getElementById('stage'); var r=s.getBoundingClientRect();
          var e=new WheelEvent('wheel',{bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2,deltaX:%d,deltaY:%d,ctrlKey:%s,shiftKey:%s,deltaMode:0});
          s.dispatchEvent(e);
          return {panX:state.spec.panX, panY:state.spec.panY, zoom:state.spec.zoom, zv:(document.getElementById('zoomVal')||{}).textContent};
        })()""" % (dx, dy, 'true' if ctrl else 'false', 'true' if shift else 'false'))

    before = ev(c, i, "({panX:state.spec.panX,panY:state.spec.panY,zoom:state.spec.zoom})")
    r1 = wheel(0, 120); time.sleep(0.2)
    r2 = wheel(0, 120, shift=True); time.sleep(0.2)
    r3 = wheel(0, -120, ctrl=True); time.sleep(0.3)
    r4 = wheel(0, -120, ctrl=True); time.sleep(0.3)
    print("before:", before)
    print("plain wheel dy=120 :", r1)
    print("shift wheel        :", r2)
    print("ctrl wheel up x2   :", r3, r4)

    # hold ctrl+wheel up 15 more times: must never exceed 100%
    last = None
    for _ in range(15):
        last = wheel(0, -120, ctrl=True); time.sleep(0.05)
    print("after 15 more up   :", last)

    # ctrl+wheel down a lot: must bottom out at 10%
    low = None
    for _ in range(60):
        low = wheel(0, 120, ctrl=True); time.sleep(0.03)
    print("after 60 down      :", low)

    # shortcuts
    ev(c, i, "document.dispatchEvent(new KeyboardEvent('keydown',{key:'0',ctrlKey:true,bubbles:true}))")
    time.sleep(0.3)
    print("Ctrl+0            :", ev(c, i, "({zoom:state.spec.zoom, zv:(document.getElementById('zoomVal')||{}).textContent})"))
    ev(c, i, "document.dispatchEvent(new KeyboardEvent('keydown',{key:'1',shiftKey:true,bubbles:true}))")
    time.sleep(0.4)
    print("Shift+1 fit       :", ev(c, i, "({zoom:state.spec.zoom, zv:(document.getElementById('zoomVal')||{}).textContent})"))

    ov = ev(c, i, "({ovfX:document.documentElement.scrollWidth>innerWidth+1, ovfY:document.documentElement.scrollHeight>innerHeight+1})")
    print("overflow:", ov)
    print("errors:", ev(c, i, "window.__errs ? window.__errs.length : 0"))
    c.close()
finally:
    proc.terminate()
    try: proc.wait(timeout=5)
    except Exception: proc.kill()