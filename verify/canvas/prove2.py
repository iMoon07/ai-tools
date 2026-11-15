import json, time, urllib.request, subprocess, tempfile, base64, io, math
import websocket
from PIL import Image

PORT = 9791
tmp = tempfile.mkdtemp(prefix="prove2")
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

print("== A. instrument the Rough.js generator prototype ==")
print(json.dumps(ev("""(function(){
  window.__calls = {generator:0, rectangle:0, ellipse:0, polygon:0, path:0, toPaths:0};
  var R = window.rough;
  var probe = R.generator();
  var proto = Object.getPrototypeOf(probe);
  ['rectangle','ellipse','polygon','path','toPaths'].forEach(function (m) {
    if (typeof proto[m] !== 'function' || proto[m].__wrapped) return;
    var f = proto[m];
    var w = function () { window.__calls[m]++; return f.apply(this, arguments); };
    w.__wrapped = true;
    proto[m] = w;
  });
  var og = R.generator;
  R.generator = function () {
    window.__calls.generator++;
    return og.apply(R, arguments);
  };
  return {proto: !!proto, keys: Object.keys(window.__calls)};})()""")))

print("== B. render a NEW node -> the renderer must call the library ==")
spec = {"module": "canvas", "nodes": {
    "a1": {"x": 140, "y": 140, "w": 200, "h": 110, "text": "API", "shape": "box"},
    "b1": {"x": 520, "y": 140, "w": 200, "h": 110, "text": "DB", "shape": "ellipse"}},
    "edges": []}
ev("""(function(){var box=document.getElementById('drawCode');
  box.value='```draw\\n'+JSON.stringify(%s, null, 2)+'\\n```';
  document.getElementById('applyCode').click();})()""" % json.dumps(spec))
time.sleep(1.2)
print(json.dumps(ev("window.__calls")))
print("rough paths:", ev("document.querySelectorAll('.alur-node-rough').length"))

print("== C. a different roughness changes the ink (same node, new seed key) ==")
spec2 = json.loads(json.dumps(spec))
spec2["nodes"]["a1"]["sloppiness"] = "cartoonist"
ev("""(function(){var box=document.getElementById('drawCode');
  box.value='```draw\\n'+JSON.stringify(%s, null, 2)+'\\n```';
  document.getElementById('applyCode').click();})()""" % json.dumps(spec2))
time.sleep(1.2)
print(json.dumps(ev("window.__calls")))
print("path now:", ev("(function(){var p=document.querySelector('.alur-node-rough');return p?(p.getAttribute('d')||'').slice(0,70):null;})()"))

print("== D. the DOM path is exactly what rough.svg() would produce ==")
print(json.dumps(ev("""(function(){
  var p=document.querySelector('.alur-node-rough');
  if(!p) return {err:'no path'};
  var domD=p.getAttribute('d');
  /* Same options the renderer uses: outline only, seeded, no fill. */
  var g=window.rough.generator();
  var draw=g.rectangle(0,0,200,110,{roughness:2,bowing:1,seed:12345,stroke:'#000',
    strokeWidth:1.5,fill:undefined,disableMultiStroke:false,preserveVertices:true});
  var paths=g.toPaths(draw).filter(function(x){return x && x.d && x.stroke!=='none';});
  return {domCommands:(domD.match(/[MLCQAZ]/g)||[]).length,
          libCommands:paths.map(function(x){return (x.d.match(/[MLCQAZ]/g)||[]).length;}),
          domIsCurved:/C/.test(domD), libIsCurved:paths.some(function(x){return /C/.test(x.d);}),
          samePrefix: paths.length ? domD.slice(0,12) === paths[0].d.slice(0,12) : null};})()""")))

print("== E. laser visibility, light vs dark, sampled on the beam ==")
ST = ev("(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y};})()")
def ptr(t, x, y, b=1):
    ev("""(function(){var s=document.getElementById('stage');
      s.dispatchEvent(new PointerEvent(%s,{bubbles:true,cancelable:true,clientX:%f,clientY:%f,button:0,buttons:%d,pointerId:1,pointerType:'mouse',isPrimary:true}));})()""" % (json.dumps(t), x, y, b))
def beam(light):
    if light != ev("document.body.classList.contains('theme--light')"):
        ev("document.getElementById('themeToggle').click()")
        time.sleep(0.5)
    ev("document.querySelector('[data-tool=\\\"laser\\\"]').click()")
    x0, y0, x1, y1 = ST['x'] + 120, ST['y'] + 760, ST['x'] + 1180, ST['y'] + 760
    ptr("pointerdown", x0, y0)
    for k in range(1, 16):
        ptr("pointermove", x0 + (x1 - x0) * k / 15, y0)
    time.sleep(0.2)
    info = ev("""(function(){var g=document.querySelector('.alur-laser');
      return g?{blend:getComputedStyle(g).mixBlendMode,
                core:getComputedStyle(g.querySelector('.laser-core')).stroke}:null;})()""")
    shot = cmd("Page.captureScreenshot", format="png",
               clip={"x": x0 + 20, "y": y0 - 12, "width": 900, "height": 24, "scale": 1})
    img = Image.open(io.BytesIO(base64.b64decode(shot["data"]))).convert("RGB")
    px = img.load()
    hits = []
    for x in range(0, img.width, 3):
        r, g_, b_ = px[x, img.height // 2]
        hits.append((r, g_, b_))
    nonbg = [h for h in hits if sum(h) < 720]
    print(("light" if light else "dark"), info, "sampled:", len(hits),
          "inked:", len(nonbg), "examples:", nonbg[:4])
    ptr("pointerup", x1, y1, 0)
    time.sleep(0.9)

beam(True)
beam(False)
print("errs:", ev("window.__errs"))
proc.terminate()