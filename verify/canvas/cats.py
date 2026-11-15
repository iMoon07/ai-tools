import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9483
tmp=tempfile.mkdtemp(prefix="ct")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=390,844","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
cmd("Emulation.setDeviceMetricsOverride",width=390,height=844,deviceScaleFactor=1,mobile=True)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.2)
ev("document.querySelector('[data-panel=\"assets\"]').click()")
time.sleep(0.7)
print("cats:", ev("""(function(){var e=document.getElementById('logoCats'); if(!e) return 'missing';
  var b=e.getBoundingClientRect(); var cs=getComputedStyle(e);
  return {disp:cs.display,wrap:cs.flexWrap,ovx:cs.overflowX,y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height),
    sw:e.scrollWidth,cw:e.clientWidth,n:e.children.length};})()"""))
print("chips:", ev("""(function(){var e=document.getElementById('logoCats');var o=[];
  for(var k=0;k<e.children.length;k++){var b=e.children[k].getBoundingClientRect();
    o.push({t:e.children[k].textContent.trim().slice(0,10),x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height)});}
  return o.slice(0,12);})()"""))
print("parent:", ev("""(function(){var e=document.getElementById('logoCats');var p=e.parentElement;
  var b=p.getBoundingClientRect(); var cs=getComputedStyle(p);
  return {cls:p.className,disp:cs.display,h:Math.round(b.height),ov:cs.overflow};})()"""))
c.close(); proc.terminate()
