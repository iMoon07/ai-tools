import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9890
tmp=tempfile.mkdtemp(prefix="dt")
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
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")

print("nodes:", ev("document.querySelectorAll('#stage .alur-canvas-node').length"))
print("selected dom:", ev("document.querySelectorAll('#stage .alur-canvas-node.is-selected').length"))

# click the first node
ev("""(function(){
  var n=document.querySelector('#stage .alur-canvas-node'); if(!n) return 'none';
  var r=n.getBoundingClientRect();
  var svg=document.querySelector('#stage svg');
  var ev=new PointerEvent('pointerdown',{bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2,pointerId:1,button:0,isPrimary:true});
  n.dispatchEvent(ev);
  var up=new PointerEvent('pointerup',{bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2,pointerId:1,button:0,isPrimary:true});
  n.dispatchEvent(up);
  return 'clicked';})()""")
time.sleep(0.4)
print("after click, selected dom:", ev("document.querySelectorAll('#stage .alur-canvas-node.is-selected').length"))

for press in range(1,5):
    ev("document.dispatchEvent(new KeyboardEvent('keydown',{key:'Delete',bubbles:true}))")
    time.sleep(0.35)
    print("press",press,"-> nodes:", ev("document.querySelectorAll('#stage .alur-canvas-node').length"),
          "selected:", ev("document.querySelectorAll('#stage .alur-canvas-node.is-selected').length"))
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
