import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9993
W,H=1600,1000
tmp=tempfile.mkdtemp(prefix="tl")
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
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("document.querySelector('[data-panel=\"scene\"]').click()")
time.sleep(0.6)
print(ev("""(function(){var out=[];
 var shell=document.querySelector('.scene-shell');
 Array.prototype.forEach.call(shell.children,function(e){var b=e.getBoundingClientRect();
  out.push({c:(e.className||e.tagName).toString().slice(0,22),h:Math.round(b.height),open:e.open});});
 return out;})()"""))
print("sceneControls:", ev("""(function(){var e=document.getElementById('sceneControls');
  return {h:Math.round(e.getBoundingClientRect().height),kids:e.children.length,html:e.innerHTML.length};})()"""))
print("chartSection open:", ev("document.getElementById('chartSection').open"))
print("18px el:", ev("""(function(){var d=document.getElementById('panelScene');var out=[];
  Array.prototype.forEach.call(d.querySelectorAll('*'),function(e){var b=e.getBoundingClientRect();
   if(b.width>600&&b.height>0&&b.height<20&&!(e.className||'').toString()) out.push({t:e.tagName,h:Math.round(b.height),txt:(e.textContent||'').slice(0,20)});});
  return out.slice(0,6);})()"""))
c.close(); proc.terminate()
