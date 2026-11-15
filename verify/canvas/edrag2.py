import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9982
tmp=tempfile.mkdtemp(prefix="ed2")
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
def down(x,y):
    cmd("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", clickCount=1)
def move(x,y):
    cmd("Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y, button="left", buttons=1)
    time.sleep(0.05)
def up(x,y):
    cmd("Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y, button="left", clickCount=1)
    time.sleep(0.4)
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")
ev("""(function(){
  var sp={nodes:{
    a:{x:200,y:200,w:160,h:60,label:'A'},
    b:{x:600,y:200,w:160,h:60,label:'B'}
  },edges:[{from:'a',to:'b'}],selected:null};
  document.getElementById('stage').setAttribute('data-spec', JSON.stringify(sp));
  window.dispatchEvent(new Event('alur:spec'));
  return 'set';
})()""")
time.sleep(1.0)
def spec():
    return ev("""(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec')||'{}');
      return {se:s.selectedEdge,ses:s.selectedEdges,edges:(s.edges||[]).map(function(e){return {pts:e.points||null,from:e.from||null,to:e.to||null,curved:e.curved};})};})()""")
def selcls():
    return ev("""(function(){var l=document.querySelectorAll('.alur-canvas-edge');var o=[];
      for(var k=0;k<l.length;k++){o.push({i:l[k].getAttribute('data-edge'),cls:l[k].getAttribute('class')});}return o;})()""")
print("mid screen:", ev("""(function(){var e=document.querySelector('.alur-canvas-edge');
  var b=e.getBoundingClientRect();return {x:Math.round(b.x+b.width/2),y:Math.round(b.y+b.height/2),w:Math.round(b.width),h:Math.round(b.height)};})()"""))
m = ev("""(function(){var e=document.querySelector('.alur-canvas-edge');
  var b=e.getBoundingClientRect();return [Math.round(b.x+b.width/2),Math.round(b.y+b.height/2)];})()""")
print("click at", m)
down(m[0],m[1]); up(m[0],m[1])
print("after click:", spec())
print("classes:", selcls())
print("--- drag ---")
down(m[0],m[1])
for k in range(1,13):
    move(m[0]+k*5, m[1]+k*8)
up(m[0]+60, m[1]+96)
print("after drag:", spec())
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
