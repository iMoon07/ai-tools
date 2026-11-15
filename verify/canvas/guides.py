import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9855; PROF="/tmp/alur-probes/prof-guides"
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
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.8)

print(json.dumps(ev("""(async()=>{
  const s0=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));
  const ids=Object.keys(s0.nodes);
  const nd=document.querySelector('#stage svg .alur-canvas-node[data-node-id="'+ids[0]+'"]');
  const b=nd.getBoundingClientRect();
  const mk=(t,x,y)=>new PointerEvent(t,{bubbles:true,cancelable:true,pointerId:7,pointerType:'mouse',isPrimary:true,button:0,buttons:1,clientX:x,clientY:y});
  nd.dispatchEvent(mk('pointerdown', b.x+b.width/2, b.y+b.height/2));
  await new Promise(r=>setTimeout(r,80));
  let maxGuides=0;
  for (let i=1;i<=20;i++){
    window.dispatchEvent(mk('pointermove', b.x+b.width/2+i*4, b.y+b.height/2+i*0.5));
    await new Promise(r=>setTimeout(r,22));
    maxGuides=Math.max(maxGuides, document.querySelectorAll('#stage svg .alur-guide').length);
  }
  window.dispatchEvent(mk('pointerup', b.x+b.width/2+80, b.y+b.height/2+10));
  await new Promise(r=>setTimeout(r,300));
  const s1=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));
  return {id:ids[0], from:[s0.nodes[ids[0]].x, s0.nodes[ids[0]].y], to:[s1.nodes[ids[0]].x, s1.nodes[ids[0]].y],
          maxGuides, guidesAfter:document.querySelectorAll('#stage svg .alur-guide').length};})()""")))
print("exc:", exc if exc else "none")
proc.terminate()
