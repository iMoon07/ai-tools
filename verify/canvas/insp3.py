import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9822; PROF="/tmp/alur-probes/prof-insp3"
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
            d=r["params"]["exceptionDetails"]; exc.append(d.get("text","")+" "+(d.get("exception") or {}).get("description","")[:180])
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.0)
ev("document.getElementById('stage').dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,clientX:1200,clientY:800}))")
ev("document.querySelector('[data-tool=arrow]').click()"); time.sleep(0.8)
print("pick swatch:", json.dumps(ev("""(async()=>{
  const sws=document.querySelectorAll('#shapePanelBody .swatch');
  const titles=[].map.call(sws,b=>b.getAttribute('title')||b.getAttribute('aria-label')||'');
  sws[3].click();
  await new Promise(r=>setTimeout(r,500));
  let saved=null;
  try{ saved=JSON.parse(localStorage.getItem('ruang.scene.v1')||'null'); }catch(e){}
  return {titles:titles.slice(0,5), savedEdgeStyle: saved? JSON.stringify(saved.edgeStyle||null):'none'};
})()""")))

# width slider
print("width:", json.dumps(ev("""(async()=>{
  const r=document.querySelector('#shapePanelBody input[type=range]');
  if(!r) return 'no range';
  r.value='4';
  r.dispatchEvent(new Event('input',{bubbles:true}));
  await new Promise(r2=>setTimeout(r2,400));
  const saved=JSON.parse(localStorage.getItem('ruang.scene.v1')||'null');
  return {saved:JSON.stringify(saved.edgeStyle||null)};
})()""")))
print("exc:", exc if exc else "none")
proc.terminate()
