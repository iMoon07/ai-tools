import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9886
tmp=tempfile.mkdtemp(prefix="zd")
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
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.2)
ev("""(function(){
  if(!window.__origSet){ window.__origSet = localStorage.setItem.bind(localStorage);
    localStorage.setItem = function(k,v){ if(k==='ruang.scene.v1') return; return window.__origSet(k,v); }; }
  var s=JSON.parse(localStorage.getItem('ruang.scene.v1')||'{}');
  s.zoom=2.57; s.module='canvas';
  window.__origSet('ruang.scene.v1', JSON.stringify(s));
  return 'seeded';})()""")
cmd("Page.reload"); time.sleep(3.5)
print("loaded:", ev("JSON.parse(localStorage.getItem('ruang.scene.v1')||'{}').zoom"))
print("view:", ev("""(function(){var s=document.querySelector('#stage svg');var vb=s.getAttribute('viewBox').split(' ').map(Number);return {vbW:vb[2],pct:document.getElementById('zoomVal').textContent,top:document.getElementById('topStatus').textContent};})()"""))
ev("""(function(){var s=document.getElementById('stage');var r=s.getBoundingClientRect();
 s.dispatchEvent(new WheelEvent('wheel',{bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2,deltaY:60,deltaMode:0}));return 1;})()""")
for k in range(12):
    time.sleep(0.3)
    z = ev("JSON.parse(localStorage.getItem('ruang.scene.v1')||'{}').zoom")
    print(k, "stored zoom:", z)
c.close(); proc.terminate()
