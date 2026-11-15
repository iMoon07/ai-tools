import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT = 9783
tmp = tempfile.mkdtemp(prefix="arw2")
proc = subprocess.Popen(["chromium", "--headless=new", "--disable-gpu", "--no-sandbox",
    "--hide-scrollbars", "--remote-debugging-port=%d" % PORT, "--remote-allow-origins=*",
    "--user-data-dir=" + tmp, "--window-size=1400,900", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(80):
    try:
        urllib.request.urlopen("http://127.0.0.1:%d/json/version" % PORT, timeout=1).read(); break
    except Exception:
        time.sleep(0.25)
tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT).read())
page = [t for t in tabs if t["type"] == "page"][0]
c = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=30)
i = [0]
def cmd(m, **p):
    i[0] += 1; c.send(json.dumps({"id": i[0], "method": m, "params": p}))
    while True:
        r = json.loads(c.recv())
        if r.get("id") == i[0]: return r.get("result", {})
def ev(e):
    r = cmd("Runtime.evaluate", expression=e, returnByValue=True, awaitPromise=True).get("result", {})
    return r.get("value") if r.get("subtype") != "error" else {"__err": r.get("description")}
cmd("Page.enable"); cmd("Runtime.enable")

SPEC = {"module": "canvas", "nodes": {
    "a": {"x": 140, "y": 140, "w": 190, "h": 80, "text": "API", "shape": "box"},
    "b": {"x": 620, "y": 360, "w": 190, "h": 80, "text": "DB", "shape": "box"}},
    "edges": [{"from": "a", "to": "b", "arrowEnd": True}]}

def load(w, h, mobile=False, elbow=False, curved=False):
    spec = json.loads(json.dumps(SPEC))
    if elbow: spec["edges"][0]["elbow"] = True
    if curved: spec["edges"][0]["curved"] = True
    cmd("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=mobile)
    cmd("Page.navigate", url="http://127.0.0.1:8123/draw.html?cb=" + str(time.time()))
    time.sleep(3.4)
    ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
    ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
    time.sleep(0.3)
    ev("""(function(){var box=document.getElementById('drawCode');
      box.value='```draw\\n'+JSON.stringify(%s, null, 2)+'\\n```';
      document.getElementById('applyCode').click();})()""" % json.dumps(spec))
    time.sleep(1.1)
    return ev("document.querySelectorAll('.alur-canvas-edge').length")

def ptr(t, x, y, buttons=1, ptype='mouse', sel='.alur-canvas-edge'):
    ev("""(function(){var s=document.querySelector(%s)||document.getElementById('stage');
      s.dispatchEvent(new PointerEvent(%s,{bubbles:true,cancelable:true,clientX:%f,clientY:%f,button:0,buttons:%d,pointerId:1,pointerType:%s,isPrimary:true}));})()"""
       % (json.dumps(sel), json.dumps(t), x, y, buttons, json.dumps(ptype)))

def select_edge():
    eb = ev("""(function(){var e=document.querySelector('.alur-canvas-edge');var b=e.getBoundingClientRect();
      return {x:b.x+b.width/2,y:b.y+b.height/2};})()""")
    ptr("pointerdown", eb["x"], eb["y"]); ptr("pointerup", eb["x"], eb["y"], 0)
    time.sleep(0.6)
    return ev("document.querySelectorAll('.alur-edge-handle').length")

def handles():
    return ev("""
      (function(){
        var out=[];
        var hs=document.querySelectorAll('.alur-edge-handle');
        for(var i=0;i<hs.length;i++){
          var t=(/translate\\(([-0-9.]+) ([-0-9.]+)\\)/).exec(hs[i].getAttribute('transform'));
          out.push({k:hs[i].getAttribute('data-edge-point'),
                    x:parseFloat(t[1]), y:parseFloat(t[2])});
        }
        return out;
      })()""")

def center_of(sel):
    return ev("""(function(){var e=document.querySelector(%s);var b=e.getBoundingClientRect();
      return {x:b.x+b.width/2,y:b.y+b.height/2};})()""" % json.dumps(sel))

def drag(x0, y0, x1, y1, steps=12, ptype='mouse', sel='.alur-canvas-edge'):
    ptr("pointerdown", x0, y0, 1, ptype, sel)
    for k in range(1, steps + 1):
        ptr("pointermove", x0 + (x1 - x0) * k / steps, y0 + (y1 - y0) * k / steps, 1, ptype, sel)
    ptr("pointerup", x1, y1, 0, ptype, sel)
    time.sleep(0.7)

def edge_d():
    return ev("(function(){var e=document.querySelector('.alur-canvas-edge');return e?e.getAttribute('d'):null;})()")

def state_edges():
    return ev("""(function(){var raw=JSON.parse(document.getElementById('drawCode').value
      .replace(/^```[a-zA-Z]*\\s*\\n/, '').replace(/\\n?```$/, ''));
      return raw.edges.map(function(e){return {from:e.from||null,to:e.to||null,
        points:e.points?e.points.length:0, elbow:!!e.elbow, curved:!!e.curved};});})()""")

for label, kw in [("straight", {}), ("curved", {"curved": True}), ("elbow", {"elbow": True})]:
    n = load(1400, 900, elbow=kw.get("elbow", False), curved=kw.get("curved", False))
    h = select_edge()
    hs = handles()
    if isinstance(hs, dict): print("  HANDLE ERR", hs); break
    d0 = edge_d()
    print("[%s] edges=%d handles=%d %s" % (label, n, h, [x["k"] for x in hs]))
    mid = [x for x in hs if x["k"] == "mid"][0]
    # midpoint must sit on the drawn path
    print("  mid on path:", ev("""(function(){
      var p=document.querySelector('.alur-canvas-edge');
      var mp=p.getPointAtLength(p.getTotalLength()/2);
      return Math.abs(mp.x-%f)<0.6 && Math.abs(mp.y-%f)<0.6;})()""" % (mid["x"], mid["y"])))
    # drag the middle handle
    drag(mid["x"], mid["y"], mid["x"] + 30, mid["y"] - 110, sel='.alur-edge-handle.is-mid')
    d1 = edge_d()
    print("  path changed:", d0 != d1, "handles now", [x["k"] for x in handles()])
    print("  edge model:", state_edges())
    # drop the end handle on node A -> re-attach
    end = [x for x in handles() if x["k"] != "mid"][-1]
    na = center_of(".alur-canvas-node")
    drag(end["x"], end["y"], na["x"], na["y"], sel='.alur-edge-handle:last-of-type')
    print("  after reattach:", state_edges())
    print("  errs:", ev("window.__errs"))

# touch: same three handles, drag works with pointerType touch
load(1400, 900)
h = select_edge()
print("[touch] handles=%d" % h)
hs = handles()
mid = [x for x in hs if x["k"] == "mid"][0]
d0 = edge_d()
drag(mid["x"], mid["y"], mid["x"] - 40, mid["y"] + 90, ptype='touch', sel='.alur-edge-handle.is-mid')
print("  touch path changed:", d0 != edge_d(), "errs:", ev("window.__errs"))

# mobile viewport
load(390, 780, mobile=True)
h = select_edge()
print("[mobile] handles=%d" % h)
hs = handles()
print("  hit r:", ev("(function(){var h=document.querySelector('.alur-edge-hit');return h?h.getAttribute('r'):null;})()"))
print("  docW:", ev("document.documentElement.scrollWidth"), "view:", ev("window.innerWidth"))
print("  errs:", ev("window.__errs"))
proc.terminate()