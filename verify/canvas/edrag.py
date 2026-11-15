import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9981
tmp=tempfile.mkdtemp(prefix="ed")
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
def drag(x0,y0,x1,y1,steps=12):
    cmd("Input.dispatchMouseEvent", type="mousePressed", x=x0, y=y0, button="left", clickCount=1)
    for k in range(1,steps+1):
        cmd("Input.dispatchMouseEvent", type="mouseMoved",
            x=x0+(x1-x0)*k/steps, y=y0+(y1-y0)*k/steps, button="left", buttons=1)
        time.sleep(0.03)
    cmd("Input.dispatchMouseEvent", type="mouseReleased", x=x1, y=y1, button="left", clickCount=1)
    time.sleep(0.4)
def edges():
    return ev("""(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec')||'{}');
      return (s.edges||[]).map(function(e){return {pts:e.points||null,from:e.from||null,to:e.to||null,curved:e.curved};});})()""")
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
print("edges:", edges())
print("edge els:", ev("""(function(){var l=document.querySelectorAll('.alur-canvas-edge');var o=[];
  for(var k=0;k<l.length;k++){var e=l[k];o.push({i:e.getAttribute('data-edge'),pe:getComputedStyle(e).pointerEvents,sw:e.getAttribute('stroke-width'),stroke:e.getAttribute('stroke')});}
  return o;})()"""))
print("hit mid:", ev("""(function(){var e=document.querySelector('.alur-canvas-edge');
  if(!e) return null; var b=e.getBoundingClientRect();
  var el=document.elementFromPoint(b.x+b.width/2, b.y+b.height/2);
  return el?{tag:el.tagName,cls:el.getAttribute('class'),edge:el.getAttribute('data-edge')}:null;})()"""))
before = edges()
drag(480,230,480,340)
after = edges()
print("before:", before)
print("after :", after)
print("changed:", json.dumps(before)!=json.dumps(after))
print("sel:", ev("(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec')||'{}');return {se:s.selectedEdge,ses:s.selectedEdges};})()"))
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
