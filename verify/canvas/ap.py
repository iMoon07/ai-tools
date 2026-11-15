import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9852; PROF="/tmp/alur-probes/prof-ap"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",f"--user-data-dir={PROF}",
 "--no-first-run","--no-default-browser-check","--disable-gpu","--window-size=1600,1000",
 "--remote-allow-origins=*","--hide-scrollbars","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
import websocket
def http(p,m="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=m),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),"PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=60,suppress_origin=True)
n=[0]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]: return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.0)
print(json.dumps(ev("""(async()=>{
  const stage=document.getElementById('stage'); const r=stage.getBoundingClientRect();
  const mk=(t,x,y)=>new PointerEvent(t,{bubbles:true,cancelable:true,pointerId:3,pointerType:'mouse',isPrimary:true,button:0,buttons:1,clientX:x,clientY:y});
  document.querySelector('[data-tool=line]').click();
  stage.dispatchEvent(mk('pointerdown', r.left+300, r.top+300));
  for (let i=0;i<10;i++) { window.dispatchEvent(mk('pointermove', r.right-30, r.top+320)); await new Promise(x=>setTimeout(x,50)); }
  const frames=(window.__ap||[]).length;
  const vb=document.querySelector('#stage svg').viewBox.baseVal;
  window.dispatchEvent(mk('pointerup', r.right-30, r.top+320));
  return {post:(window.__ap2||[]).slice(0,5), dbg:(window.__apd||[]).slice(-1), last:(window.__ap||[]).slice(-3), rect:[Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height)],
          frames, vbX:Math.round(vb.x), raf:typeof requestAnimationFrame};
})()""")))
proc.terminate()
