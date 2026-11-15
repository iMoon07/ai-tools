import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9450
tmp=tempfile.mkdtemp(prefix="tb")
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
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
print("topbar children:", ev("""(function(){var t=document.querySelector('.topbar');var b=t.getBoundingClientRect();var o=[];
  Array.prototype.forEach.call(t.children,function(e){var r=e.getBoundingClientRect();
   o.push({c:(e.className||e.tagName).toString().slice(0,18),l:Math.round(r.left),r:Math.round(r.right),w:Math.round(r.width)});});
  return {w:Math.round(b.width),right:Math.round(b.right),kids:o};})()"""))
print("grid tools:", ev("""(function(){var l=document.querySelectorAll('#toolGrid .tool');
  return Array.prototype.map.call(l,function(b){return b.getAttribute('data-tool')||b.getAttribute('data-panel')||b.id||'?';});})()"""))
print("grid visible n:", ev("""(function(){var l=document.querySelectorAll('#toolGrid .tool');var n=0;
  for(var k=0;k<l.length;k++){if(l[k].getBoundingClientRect().width>0)n++;}return n;})()"""))
c.close(); proc.terminate()
