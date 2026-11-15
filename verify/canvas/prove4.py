import json, time, urllib.request, subprocess, tempfile, base64, io
import websocket
from PIL import Image, ImageChops

PORT = 9793
tmp = tempfile.mkdtemp(prefix="prove4")
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
    "c1": {"x": 200, "y": 300, "w": 220, "h": 130, "text": "DB", "shape": "circle", "sloppiness": "artist"}},
    "edges": []}
ev("""(function(){var box=document.getElementById('drawCode');
  box.value='```draw\\n'+JSON.stringify(%s, null, 2)+'\\n```';
  document.getElementById('applyCode').click();})()""" % json.dumps(spec))
time.sleep(1.2)

print("== circle node: DOM path vs rough.ellipse with the renderer's seed ==")
print(json.dumps(ev("""(function(){
  function kitSeed(str){var s=String(str),h=2166136261>>>0;
    for(var i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return h>>>0;}
  var gEl=document.querySelector('[data-node-id="c1"]');
  var dom=[].slice.call(gEl.querySelectorAll('.alur-node-rough')).map(function(p){return p.getAttribute('d');});
  var w=220,h=130,seed=kitSeed('c1');
  var g=window.rough.generator();
  var opts={roughness:1,bowing:1,seed:seed,stroke:'#000',strokeWidth:1.5,
            fill:undefined,disableMultiStroke:false,preserveVertices:true};
  var lib=g.toPaths(g.ellipse(w/2,h/2,Math.max(2,w-4),Math.max(2,h-4),opts))
          .filter(function(p){return p&&p.d&&p.stroke!=='none';}).map(function(p){return p.d;});
  return {domPaths:dom.length, libPaths:lib.length,
          identical: dom.length===lib.length && dom.every(function(d,i){return d===lib[i];}),
          domCommands:(dom[0]||'').match(/[MLCQAZ]/g||[]).length};})()""")))

print("== laser: before/after pixel diff, light vs dark ==")
ST = ev("(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()")
print("stage:", ST)
def ptr(t, x, y, b=1):
    ev("""(function(){var s=document.getElementById('stage');
      s.dispatchEvent(new PointerEvent(%s,{bubbles:true,cancelable:true,clientX:%f,clientY:%f,button:0,buttons:%d,pointerId:1,pointerType:'mouse',isPrimary:true}));})()""" % (json.dumps(t), x, y, b))
def shot(clip):
    r = cmd("Page.captureScreenshot", format="png", clip=clip)
    return Image.open(io.BytesIO(base64.b64decode(r["data"]))).convert("RGB")

y = ST['y'] + ST['h'] - 90
x0, x1 = ST['x'] + 100, ST['x'] + 900
clip = {"x": x0, "y": y - 20, "width": x1 - x0, "height": 40, "scale": 1}

def run(light, blend=None):
    if light != ev("document.body.classList.contains('theme--light')"):
        ev("document.getElementById('themeToggle').click()"); time.sleep(0.6)
    ev("document.querySelector('[data-tool=\\\"laser\\\"]').click()")
    before = shot(clip)
    ptr("pointerdown", x0 + 40, y)
    for k in range(1, 18):
        ptr("pointermove", x0 + 40 + (x1 - x0 - 80) * k / 17, y)
    time.sleep(0.15)
    if blend:
        ev("document.querySelector('.alur-laser').style.mixBlendMode=%s" % json.dumps(blend))
        time.sleep(0.25)
    info = ev("""(function(){var g=document.querySelector('.alur-laser');
      return g?{blend:getComputedStyle(g).mixBlendMode}:null;})()""")
    after = shot(clip)
    ptr("pointerup", x1 - 40, y, 0)
    time.sleep(0.9)
    diff = ImageChops.difference(before, after).convert("L")
    changed = sum(1 for v in diff.getdata() if v > 18)
    total = diff.width * diff.height
    return info, changed, total

for light, blend in [(True, None), (True, 'screen'), (True, 'multiply'), (False, None)]:
    info, changed, total = run(light, blend)
    print(("light" if light else "dark"), "blend=", info, "changed:", changed, "/", total)
print("errs:", ev("window.__errs"))
proc.terminate()