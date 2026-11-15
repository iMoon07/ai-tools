import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9996
tmp=tempfile.mkdtemp(prefix="e4")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox",
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
    if r.get("subtype")=="error": print("JS ERROR:",r.get("description"))
    return r.get("value")
def down(x,y): cmd("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", clickCount=1)
def move(x,y):
    cmd("Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y, button="left", buttons=1); time.sleep(0.05)
def up(x,y):
    cmd("Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y, button="left", clickCount=1); time.sleep(0.4)
def spec():
    return ev("""(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec')||'{}');
      return {se:s.selectedEdge,edges:(s.edges||[]).map(function(e){return {pts:e.points||null,from:e.from||null,to:e.to||null};})};})()""")
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")
m = ev("""(function(){var e=document.querySelector('.alur-canvas-edge');
  var b=e.getBoundingClientRect();return [Math.round(b.x+b.width/2),Math.round(b.y+b.height/2)];})()""")
print("before click:", spec())
down(m[0],m[1]); up(m[0],m[1])
print("after click :", spec())
down(m[0],m[1])
for k in range(1,13): move(m[0]+k*4, m[1]+k*7)
up(m[0]+48, m[1]+84)
print("after drag  :", spec())
down(m[0]+48,m[1]+84); up(m[0]+48,m[1]+84)
print("reselect    :", spec())
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
