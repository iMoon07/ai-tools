import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9820; PROF="/tmp/alur-probes/prof-insp"
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

PROBE = """(()=>{const sp=document.getElementById('shapePanel');
 const btn=document.getElementById('inspectorToggle');
 const r=sp.getBoundingClientRect();
 return {hidden:sp.hidden, title:document.getElementById('shapePanelTitle').textContent,
   bodyLen:document.getElementById('shapePanelBody').textContent.trim().length,
   x:Math.round(r.x), w:Math.round(r.width),
   btn: btn? {on:btn.classList.contains('is-on'), pressed:btn.getAttribute('aria-pressed'), title:btn.title.slice(0,28)}:null,
   stageLeft:getComputedStyle(document.getElementById('stage')).left,
   ovfX: document.documentElement.scrollWidth>innerWidth};})()"""

send("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.0)
print("fresh desktop:", json.dumps(ev(PROBE)))

# select a node -> panel shows model/colour
print("select node:", json.dumps(ev("""(()=>{const nd=document.querySelector('#stage svg [data-node], #stage svg .alur-node');
 if(!nd) return 'no node el';
 nd.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,clientX:150,clientY:130}));
 return 'clicked';})()"""))[:120])
time.sleep(0.7)
print("after select:", json.dumps(ev(PROBE)))

# toggle off / on
ev("document.getElementById('inspectorToggle').click()"); time.sleep(0.5)
print("toggled off:", json.dumps(ev(PROBE)))
ev("document.getElementById('inspectorToggle').click()"); time.sleep(0.5)
print("toggled on:", json.dumps(ev(PROBE)))

# arrow tool on desktop: panel must stay with defaults
ev("document.querySelector('[data-tool=arrow]').click()"); time.sleep(0.7)
print("arrow tool:", json.dumps(ev(PROBE)))

# mobile default closed
send("Emulation.setDeviceMetricsOverride",width=390,height=844,deviceScaleFactor=2,mobile=True)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.8)
print("fresh mobile:", json.dumps(ev(PROBE)))
print("exc:", exc if exc else "none")
proc.terminate()
