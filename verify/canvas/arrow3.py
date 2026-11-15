import json, time, urllib.request, subprocess, tempfile
import websocket
PORT = 9781
tmp = tempfile.mkdtemp(prefix="arw")
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
time.sleep(3.4)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.3)

SPEC = {"module": "canvas", "nodes": {
    "a": {"x": 140, "y": 140, "w": 190, "h": 80, "text": "API", "shape": "box"},
    "b": {"x": 620, "y": 360, "w": 190, "h": 80, "text": "DB", "shape": "box"}},
    "edges": [{"from": "a", "to": "b", "arrowEnd": True}]}

ev("""(function(){
  var box=document.getElementById('drawCode');
  box.value='```draw\\n'+JSON.stringify(%s, null, 2)+'\\n```';
  document.getElementById('applyCode').click();
})()""" % json.dumps(SPEC))
time.sleep(1.2)
print("stage", ev("(function(){var st=document.getElementById('stage');return {alur:!!st.__alur, html:st.innerHTML.length, svg:st.querySelectorAll('svg').length, all:st.querySelectorAll('*').length};})()"))
print("errs", ev("window.__errs"))
print("status", ev("(function(){var s=document.getElementById('codeStatus');return s?s.textContent:null;})()"))
print("applied", ev("(function(){return {nodes:document.querySelectorAll('.alur-canvas-node').length, edges:document.querySelectorAll('.alur-canvas-edge').length};})()"))

# select the arrow by clicking its cable
print("edge box", ev("""(function(){
  var e=document.querySelector('.alur-canvas-edge');
  if(!e) return null;
  var b=e.getBoundingClientRect();
  return {x:b.x+b.width/2,y:b.y+b.height/2,w:b.width,h:b.height};
})()"""))
eb = ev("""(function(){var e=document.querySelector('.alur-canvas-edge');var b=e.getBoundingClientRect();
 return {x:b.x+b.width/2,y:b.y+b.height/2};})()""")
ev("""(function(){var s=document.querySelector('.alur-canvas-edge');
 s.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,clientX:%f,clientY:%f,button:0,buttons:1,pointerId:1,pointerType:'mouse',isPrimary:true}));
 s.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,cancelable:true,clientX:%f,clientY:%f,button:0,buttons:0,pointerId:1,pointerType:'mouse',isPrimary:true}));})()""" % (eb["x"], eb["y"], eb["x"], eb["y"]))
time.sleep(0.8)

print("handles", ev("""(function(){
  var hs=[].slice.call(document.querySelectorAll('.alur-edge-handle'));
  return {n:hs.length, list:hs.map(function(h){return {k:h.getAttribute('data-edge-point'),
     t:h.getAttribute('transform'), r:h.querySelector('.alur-edge-hit').getAttribute('r')};})};
})()"""))
print("mid on path", ev("""(function(){
  var p=document.querySelector('.alur-canvas-edge');
  var m=document.querySelector('.alur-edge-handle.is-mid');
  if(!p||!m) return null;
  var mp=p.getPointAtLength(p.getTotalLength()/2);
  var t=(/translate\\(([-0-9.]+) ([-0-9.]+)\\)/).exec(m.getAttribute('transform'));
  return {path:[Math.round(mp.x*10)/10,Math.round(mp.y*10)/10],
          handle:[parseFloat(t[1]),parseFloat(t[2])]};
})()"""))

def ptr(t, x, y, buttons=1):
    ev("""(function(){var s=document.getElementById('stage');
      s.dispatchEvent(new PointerEvent(%s,{bubbles:true,cancelable:true,clientX:%f,clientY:%f,button:0,buttons:%d,pointerId:1,pointerType:'mouse',isPrimary:true}));})()"""
       % (json.dumps(t), x, y, buttons))

# --- drag the MIDDLE handle: must insert a real bend ---
mid = ev("""(function(){var m=document.querySelector('.alur-edge-handle.is-mid');
  var b=m.querySelector('.alur-edge-hit').getBoundingClientRect();
  return {x:b.x+b.width/2,y:b.y+b.height/2};})()""")
ptr("pointerdown", mid["x"], mid["y"])
for k in range(1, 11):
    ptr("pointermove", mid["x"] + 4 * k, mid["y"] - 9 * k)
ptr("pointerup", mid["x"] + 40, mid["y"] - 90, 0)
time.sleep(0.7)
print("after mid drag", ev("""(function(){
  var h=[].slice.call(document.querySelectorAll('.alur-edge-handle'));
  return {n:h.length, keys:h.map(function(x){return x.getAttribute('data-edge-point');})};
})()"""))

# --- drag the END handle onto node A: must re-attach ---
end = ev("""(function(){
  var h=[].slice.call(document.querySelectorAll('.alur-edge-handle'));
  var e=h[h.length-1];
  var b=e.querySelector('.alur-edge-hit').getBoundingClientRect();
  return {x:b.x+b.width/2,y:b.y+b.height/2};})()""")
na = ev("""(function(){var n=document.querySelector('.alur-canvas-node');
  var b=n.getBoundingClientRect();return {x:b.x+b.width/2,y:b.y+b.height/2};})()""")
ptr("pointerdown", end["x"], end["y"])
for k in range(1, 13):
    ptr("pointermove", end["x"] + (na["x"] - end["x"]) * k / 12, end["y"] + (na["y"] - end["y"]) * k / 12)
ptr("pointerup", na["x"], na["y"], 0)
time.sleep(0.8)
print("after end drag", ev("""(function(){
  return {errs: window.__errs.slice()};
})()"""))
proc.terminate()