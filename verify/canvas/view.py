import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9481
W=int(sys.argv[1]); H=int(sys.argv[2])
tmp=tempfile.mkdtemp(prefix="vw")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=%d,%d"%(W,H),"about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
print("== %dx%d ==" % (W,H))
print("doc:", ev("({sw:document.documentElement.scrollWidth, iw:document.documentElement.clientWidth, sh:document.documentElement.scrollHeight, ih:document.documentElement.clientHeight})"))
print("stage:", ev("""(function(){var e=document.getElementById('stage');var b=e.getBoundingClientRect();
  var cs=getComputedStyle(e);return {x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height),pos:cs.position};})()"""))
print("svg:", ev("""(function(){var s=document.querySelector('#stage svg'); if(!s) return 'none';
  var b=s.getBoundingClientRect(); var vb=s.getAttribute('viewBox');
  return {w:Math.round(b.width),h:Math.round(b.height),vb:vb};})()"""))
print("layers:", ev("""(function(){var l=document.querySelectorAll('#stage svg > g'); var o=[];
  for(var k=0;k<l.length;k++){var b=l[k].getBoundingClientRect(); o.push({c:l[k].getAttribute('class'),w:Math.round(b.width),h:Math.round(b.height)});}
  return o.slice(0,6);})()"""))
print("zoom:", ev("(document.getElementById('zoomVal')||{}).textContent"))
print("docks open:", ev("document.querySelectorAll('.dock.is-open').length"))
c.close(); proc.terminate()
