import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9821; PROF="/tmp/alur-probes/prof-insp2"
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

# deselect everything, then pick the arrow tool
ev("document.getElementById('stage').dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,clientX:1200,clientY:800}))")
time.sleep(0.3)
ev("document.querySelector('[data-tool=arrow]').click()"); time.sleep(0.8)
print("arrow, nothing selected:", json.dumps(ev("""(()=>{const sp=document.getElementById('shapePanel');
 return {hidden:sp.hidden, title:document.getElementById('shapePanelTitle').textContent,
   labels:[].map.call(document.querySelectorAll('#shapePanelBody .shape-label'),x=>x.textContent),
   swatches:document.querySelectorAll('#shapePanelBody .swatch').length,
   selects:document.querySelectorAll('#shapePanelBody select').length,
   stageLeft:getComputedStyle(document.getElementById('stage')).left};})()""")))

# change colour + width through the panel
print("change colour:", json.dumps(ev("""(async()=>{
  const sw=[].filter.call(document.querySelectorAll('#shapePanelBody .swatch'),b=>/green|amber|red/.test(b.getAttribute('title')||b.style.background||''));
  const before=JSON.stringify(JSON.parse(document.getElementById('stage').getAttribute('data-spec')).edgeStyle||{});
  const target=document.querySelectorAll('#shapePanelBody .swatch')[2];
  target.click();
  await new Promise(r=>setTimeout(r,400));
  const spec=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));
  return {before, after:JSON.stringify(spec.edgeStyle||{})};
})()""")))
print("panel still open:", ev("!document.getElementById('shapePanel').hidden"))
print("exc:", exc if exc else "none")
proc.terminate()
