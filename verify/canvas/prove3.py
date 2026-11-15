import json, time, urllib.request, subprocess, tempfile, base64, io
import websocket
from PIL import Image

PORT = 9792
tmp = tempfile.mkdtemp(prefix="prove3")
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
cmd("Emulation.setDeviceMetricsOverride", width=1400, height=900, deviceScaleFactor=1, mobile=False)
cmd("Page.navigate", url="http://127.0.0.1:8123/draw.html?cb=" + str(time.time()))
time.sleep(3.6)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")

spec = {"module": "canvas", "nodes": {
    "a1": {"x": 140, "y": 140, "w": 200, "h": 110, "text": "API", "shape": "box", "sloppiness": "artist"},
    "b1": {"x": 520, "y": 140, "w": 200, "h": 110, "text": "DB", "shape": "ellipse", "sloppiness": "artist"},
    "c1": {"x": 140, "y": 340, "w": 200, "h": 110, "text": "Q", "shape": "diamond", "sloppiness": "artist"}},
    "edges": []}
ev("""(function(){var box=document.getElementById('drawCode');
  box.value='```draw\\n'+JSON.stringify(%s, null, 2)+'\\n```';
  document.getElementById('applyCode').click();})()""" % json.dumps(spec))
time.sleep(1.2)

print("== exact match: DOM path vs the same Rough.js call with the renderer's seed ==")
print(json.dumps(ev("""(function(){
  function kitSeed(str){
    var s=String(str), h=2166136261>>>0;
    for(var i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}
    return h>>>0;
  }
  function roundedRectPath(w,h,radius){
    var r=Math.max(0,Math.min(radius,Math.min(w,h)/2));
    if(!r) return 'M 0 0 L '+w+' 0 L '+w+' '+h+' L 0 '+h+' Z';
    return 'M '+r+' 0 L '+(w-r)+' 0 A '+r+' '+r+' 0 0 1 '+w+' '+r+
      ' L '+w+' '+(h-r)+' A '+r+' '+r+' 0 0 1 '+(w-r)+' '+h+
      ' L '+r+' '+h+' A '+r+' '+r+' 0 0 1 0 '+(h-r)+
      ' L 0 '+r+' A '+r+' '+r+' 0 0 1 '+r+' 0 Z';
  }
  var out=[];
  [['a1','box'],['b1','ellipse'],['c1','diamond']].forEach(function(pair){
    var id=pair[0], kind=pair[1];
    var gEl=document.querySelector('[data-node-id="'+id+'"]');
    if(!gEl) { out.push({id:id, err:'no node'}); return; }
    var dom=[].slice.call(gEl.querySelectorAll('.alur-node-rough')).map(function(p){return p.getAttribute('d');});
    var w=200,h=110,seed=kitSeed(id);
    var g=window.rough.generator();
    var opts={roughness:1,bowing:1,seed:seed,stroke:'#000',strokeWidth:1.5,
              fill:undefined,disableMultiStroke:false,preserveVertices:true};
    var draw = kind==='ellipse' ? g.ellipse(w/2,h/2,Math.max(2,w-4),Math.max(2,h-4),opts)
             : kind==='diamond' ? g.polygon([[w/2,0],[w,h/2],[w/2,h],[0,h/2]],opts)
             : g.path(roundedRectPath(w,h,0),opts);
    var lib=g.toPaths(draw).filter(function(p){return p && p.d && p.stroke!=='none';})
              .map(function(p){return p.d;});
    out.push({id:id, kind:kind, domPaths:dom.length, libPaths:lib.length,
              identical: dom.length===lib.length && dom.every(function(d,i){return d===lib[i];})});
  });
  return out;})()""")))

print("== laser: light theme, screen vs multiply ==")
ST = ev("(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y};})()")
def ptr(t, x, y, b=1):
    ev("""(function(){var s=document.getElementById('stage');
      s.dispatchEvent(new PointerEvent(%s,{bubbles:true,cancelable:true,clientX:%f,clientY:%f,button:0,buttons:%d,pointerId:1,pointerType:'mouse',isPrimary:true}));})()""" % (json.dumps(t), x, y, b))
if not ev("document.body.classList.contains('theme--light')"):
    ev("document.getElementById('themeToggle').click()"); time.sleep(0.5)
ev("document.querySelector('[data-tool=\\\"laser\\\"]').click()")
x0, y0, x1, y1 = ST['x'] + 120, ST['y'] + 760, ST['x'] + 1180, ST['y'] + 760
ptr("pointerdown", x0, y0)
for k in range(1, 16):
    ptr("pointermove", x0 + (x1 - x0) * k / 15, y0)
time.sleep(0.2)

def sample():
    shot = cmd("Page.captureScreenshot", format="png",
               clip={"x": x0 + 20, "y": y0 - 12, "width": 900, "height": 24, "scale": 1})
    img = Image.open(io.BytesIO(base64.b64decode(shot["data"]))).convert("RGB")
    px = img.load()
    vals = [px[x, img.height // 2] for x in range(0, img.width, 3)]
    inked = [v for v in vals if sum(v) < 720]
    return len(inked), len(vals), inked[:2]

print("screen (old):", ev("document.querySelector('.alur-laser').style.mixBlendMode='screen'") or "set")
time.sleep(0.3); print("   inked:", sample())
ev("document.querySelector('.alur-laser').style.mixBlendMode='multiply'")
time.sleep(0.3); print("multiply (new):", sample())
ptr("pointerup", x1, y1, 0); time.sleep(0.9)
print("errs:", ev("window.__errs"))
proc.terminate()