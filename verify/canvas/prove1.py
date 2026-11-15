import json, time, urllib.request, subprocess, tempfile, base64, io
import websocket
from PIL import Image

PORT = 9790
tmp = tempfile.mkdtemp(prefix="prove")
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

print("== 1. library present ==")
print(json.dumps(ev("""(function(){
  return {rough: typeof window.rough,
          generator: typeof (window.rough && window.rough.generator),
          svg: typeof (window.rough && window.rough.svg),
          version: (window.rough && window.rough.version) || null};})()""")))

print("== 2. renderer calls rough.js ==")
ev("""(function(){
  window.__calls = {generator:0, rectangle:0, ellipse:0, polygon:0, path:0};
  var R = window.rough;
  var origGen = R.generator;
  R.generator = function () {
    window.__calls.generator++;
    var g = origGen.apply(R, arguments);
    ['rectangle','ellipse','polygon','path'].forEach(function (m) {
      if (typeof g[m] === 'function' && !g[m].__wrapped) {
        var f = g[m];
        var w = function () { window.__calls[m]++; return f.apply(g, arguments); };
        w.__wrapped = true;
        g[m] = w;
      }
    });
    return g;
  };
  return true;})()""")
# force a fresh render by re-applying the scene
ev("""(function(){var b=document.getElementById('applyCode'); if(b) b.click(); return true;})()""")
time.sleep(1.0)
print(json.dumps(ev("window.__calls")))

SPEC = {"module": "canvas", "nodes": {
    "a": {"x": 140, "y": 140, "w": 200, "h": 110, "text": "API", "shape": "box", "sloppiness": "artist"},
    "b": {"x": 520, "y": 140, "w": 200, "h": 110, "text": "DB", "shape": "ellipse", "sloppiness": "artist"},
    "c": {"x": 140, "y": 340, "w": 200, "h": 110, "text": "Q", "shape": "diamond", "sloppiness": "artist"},
    "d": {"x": 520, "y": 340, "w": 200, "h": 110, "text": "P", "shape": "pill", "sloppiness": "artist"}},
    "edges": [{"from": "a", "to": "b", "arrowEnd": True, "sloppiness": "artist"}]}

def apply(spec):
    ev("""(function(){var box=document.getElementById('drawCode');
      box.value='```draw\\n'+JSON.stringify(%s, null, 2)+'\\n```';
      document.getElementById('applyCode').click();})()""" % json.dumps(spec))
    time.sleep(1.1)

def stats():
    return ev("""(function(){
      var rough=[].slice.call(document.querySelectorAll('.alur-node-rough'));
      var boxes=[].slice.call(document.querySelectorAll('.alur-canvas-node .alur-node-box'));
      return {nodes:document.querySelectorAll('.alur-canvas-node').length,
              roughPaths:rough.length,
              lens:rough.map(function(p){return (p.getAttribute('d')||'').length;}),
              boxStrokes:boxes.slice(0,4).map(function(b){return b.getAttribute('stroke');}),
              first:rough.length?(rough[0].getAttribute('d')||'').slice(0,90):null};})()""")

print("== 3. rough actually draws the outline ==")
apply(SPEC)
print("artist :", json.dumps(stats()))

print("== 4. architect (explicit off) is clean ==")
clean = json.loads(json.dumps(SPEC))
for k in clean["nodes"]:
    clean["nodes"][k]["sloppiness"] = "architect"
clean["edges"][0]["sloppiness"] = "architect"
apply(clean)
print("architect:", json.dumps(stats()))

print("== 5. cartoonist = artist, rougher ==")
cart = json.loads(json.dumps(SPEC))
for k in cart["nodes"]:
    cart["nodes"][k]["sloppiness"] = "cartoonist"
apply(cart)
print("cartoonist:", json.dumps(stats()))

print("== 6. default (no sloppiness at all) is rough ==")
dflt = json.loads(json.dumps(SPEC))
for k in dflt["nodes"]:
    del dflt["nodes"][k]["sloppiness"]
del dflt["edges"][0]["sloppiness"]
apply(dflt)
print("default:", json.dumps(stats()))

print("== 7. geometry really differs from a plain rect ==")
print(json.dumps(ev("""(function(){
  var p=document.querySelector('.alur-node-rough');
  if(!p) return null;
  var d=p.getAttribute('d')||'';
  return {isPlainRect:/^M 0 0 L 200 0 L 200 110 L 0 110 Z$/.test(d),
          commands:(d.match(/[MLCQAZ]/g)||[]).length,
          decimals:!!/\\./.test(d),
          sample:d.slice(0,120)};})()""")))

print("== 8. laser in light mode is visible ==")
ev("if(!document.body.classList.contains('theme--light')) document.getElementById('themeToggle').click();")
time.sleep(0.5)
print("light body:", ev("document.body.classList.contains('theme--light')"),
      "core:", ev("getComputedStyle(document.body).getPropertyValue('--laser-core').trim()"))
ev("document.querySelector('[data-tool=\\\"laser\\\"]').click()")
ST = ev("(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y};})()")
def ptr(t, x, y, b=1):
    ev("""(function(){var s=document.getElementById('stage');
      s.dispatchEvent(new PointerEvent(%s,{bubbles:true,cancelable:true,clientX:%f,clientY:%f,button:0,buttons:%d,pointerId:1,pointerType:'mouse',isPrimary:true}));})()""" % (json.dumps(t), x, y, b))
ptr("pointerdown", ST['x'] + 120, ST['y'] + 500)
for k in range(1, 12):
    ptr("pointermove", ST['x'] + 120 + 70 * k, ST['y'] + 500 - 12 * k)
time.sleep(0.25)
print("laser group:", ev("""(function(){var g=document.querySelector('.alur-laser');
  if(!g) return null;
  return {blend:getComputedStyle(g).mixBlendMode,
          layers:g.querySelectorAll('.alur-laser-path').length,
          core:g.querySelector('.laser-core')?getComputedStyle(g.querySelector('.laser-core')).stroke:null};})()"""))
shot = cmd("Page.captureScreenshot", format="png", clip={"x": ST['x'] + 150, "y": ST['y'] + 380,
                                                          "width": 700, "height": 180, "scale": 1})
img = Image.open(io.BytesIO(base64.b64decode(shot["data"]))).convert("RGB")
px = list(img.getdata())
dark = [p for p in px if sum(p) < 600]
print("size:", img.size, "non-white pixels:", len(dark), "of", len(px),
      "sample:", dark[:3])
ptr("pointerup", ST['x'] + 890, ST['y'] + 368, 0)
time.sleep(0.9)
print("laser gone after release:", ev("document.querySelectorAll('.alur-laser').length"))
print("errs:", ev("window.__errs"))
proc.terminate()