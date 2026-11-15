import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9989
W=int(sys.argv[1]); H=int(sys.argv[2]); MOBILE=W<700
tmp=tempfile.mkdtemp(prefix="p3")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox",
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
    if r.get("subtype")=="error": print("JS ERROR:",r.get("description"))
    return r.get("value")
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=MOBILE)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
print("== %dx%d ==" % (W,H))
print("dock:", ev("""(function(){var d=document.getElementById('panelScene');if(!d)return null;
  var b=d.getBoundingClientRect();return {x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height),ovf:getComputedStyle(d).overflowY};})()"""))
print("children:", ev("""(function(){var d=document.getElementById('panelScene');var o=[];
  Array.prototype.forEach.call(d.children,function(e){var b=e.getBoundingClientRect();
    o.push({c:(e.className||'').toString().slice(0,24),h:Math.round(b.height),b:Math.round(b.bottom)});});return o;})()"""))
print("body:", ev("""(function(){var d=document.querySelector('#panelScene .dock-body');var b=d.getBoundingClientRect();
  return {h:Math.round(b.height),sh:d.scrollHeight,ovf:getComputedStyle(d).overflowY};})()"""))
print("export:", ev("""(function(){var e=document.getElementById('exportBox');var b=e.getBoundingClientRect();
  return {h:Math.round(b.height),b:Math.round(b.bottom),open:!!e.open};})()"""))
c.close(); proc.terminate()
