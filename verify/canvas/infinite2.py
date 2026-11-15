import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9851; PROF="/tmp/alur-probes/prof-inf2"
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
n=[0]; exc=[]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]: return r.get("result",{})
        if r.get("method")=="Runtime.exceptionThrown":
            d=r["params"]["exceptionDetails"]; exc.append(d.get("text","")+" "+(d.get("exception") or {}).get("description","")[:200])
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.0)

VB = "(()=>{const v=document.querySelector('#stage svg').viewBox.baseVal; return [Math.round(v.x),Math.round(v.y),Math.round(v.width)];})()"
print("vb start:", json.dumps(ev(VB)))

print("drag past right edge:", json.dumps(ev("""(async()=>{
  const stage=document.getElementById('stage'); const r=stage.getBoundingClientRect();
  const mk=(t,x,y)=>new PointerEvent(t,{bubbles:true,cancelable:true,pointerId:3,pointerType:'mouse',isPrimary:true,button:0,buttons:1,clientX:x,clientY:y});
  document.querySelector('[data-tool=line]').click();
  stage.dispatchEvent(mk('pointerdown', r.left+300, r.top+300));
  for (let i=0;i<16;i++) { window.dispatchEvent(mk('pointermove', r.right-30, r.top+320)); await new Promise(r=>setTimeout(r,40)); }
  const vb=document.querySelector('#stage svg').viewBox.baseVal;
  const mid={x:Math.round(vb.x), w:Math.round(vb.width)};
  window.dispatchEvent(mk('pointerup', r.right-30, r.top+320));
  await new Promise(r=>setTimeout(r,400));
  const s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));
  const e=(s.edges||[]).slice(-1)[0]||{};
  return {vbDuring:mid, vbAfter:(()=>{const v=document.querySelector('#stage svg').viewBox.baseVal; return Math.round(v.x);})(),
          endX: e.points? Math.round(e.points[e.points.length-1][0]) : null,
          endY: e.points? Math.round(e.points[e.points.length-1][1]) : null,
          edgeCount:(s.edges||[]).length};})()""")))
print("exc:", exc if exc else "none")
proc.terminate()
