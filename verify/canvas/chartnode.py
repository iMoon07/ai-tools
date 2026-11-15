import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9502
tmp=tempfile.mkdtemp(prefix="cn")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=1600,1000","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
for _ in range(80):
    try:
        urllib.request.urlopen("http://127.0.0.1:%d/json/version"%PORT,timeout=1).read(); break
    except Exception: time.sleep(0.25)
tabs=json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json"%PORT).read())
page=[t for t in tabs if t["type"]=="page"][0]
c=websocket.create_connection(page["webSocketDebuggerUrl"],timeout=30)
i=[0]
def cmd(m,**p):
    i[0]+=1; c.send(json.dumps({"id":i[0],"method":m,"params":p}))
    while True:
        r=json.loads(c.recv())
        if r.get("id")==i[0]: return r.get("result",{})
def ev(e):
    r=cmd("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)["result"]
    if r.get("subtype")=="error": return {"__err":r.get("description")}
    return r.get("value")
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
print("scene:", ev("""(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec')||'{}');
  return {grid:s.grid, zoom:s.zoom, module:s.module, keys:Object.keys(s.nodes||{})};})()"""))
print("isCanvas:", ev("document.getElementById('stage').getAttribute('data-module')"))
ev("document.querySelector('[data-scene-module=\"chart\"]').click()")
time.sleep(1.0)
print("after chart:", ev("""(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec')||'{}');
  var out={grid:s.grid, zoom:s.zoom, panX:s.panX, panY:s.panY, nodes:[]};
  Object.keys(s.nodes||{}).forEach(function(k){var n=s.nodes[k];
    out.nodes.push({id:k,x:Math.round(n.x),y:Math.round(n.y),w:Math.round(n.w),h:Math.round(n.h),shape:n.shape,mod:n.module});});
  return out;})()"""))
print("grid el:", ev("""(function(){var g=document.querySelector('.alur-canvas-grid');
  if(!g) return 'none'; var cs=getComputedStyle(g);
  return {disp:cs.display,op:cs.opacity,vis:cs.visibility,w:Math.round(g.getBoundingClientRect().width),h:Math.round(g.getBoundingClientRect().height)};})()"""))
c.close(); proc.terminate()
