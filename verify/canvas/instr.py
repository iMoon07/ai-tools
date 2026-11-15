import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9640; PROF="/tmp/alur-probes/prof-instr"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1600,1000","--remote-allow-origins=*","about:blank"],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
import websocket
def http(p,method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=method),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),method="PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=90,suppress_origin=True)
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
send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3.4)

print("initial:", json.dumps(ev("""(()=>{const c=document.querySelector('#preview .topo-canvas');
  return c?{cssW:getComputedStyle(c).width, off:c.offsetWidth, inline:c.getAttribute('style'), svg:(c.querySelector('svg')||{}).getAttribute?c.querySelector('svg').getAttribute('width'):null}:null})()""")))

print("preview width:", ev("(()=>{const p=document.querySelector('#preview');const b=p.getBoundingClientRect();return [b.width, getComputedStyle(p).width, p.clientWidth]})()"))

# force a fixed width and relayout
print("force 670:", json.dumps(ev("""(()=>{const p=document.querySelector('#preview');const c=p.querySelector('.topo-canvas');
  p.style.width='670px'; if(window.Topology&&window.Topology.relayout) window.Topology.relayout(p);
  return 1})()""")))
time.sleep(1.5)
print("after force:", json.dumps(ev("""(()=>{const c=document.querySelector('#preview .topo-canvas');
  return {off:c.offsetWidth, inline:c.getAttribute('style'), svg:c.querySelector('svg').getAttribute('width')}})()""")))
ws.close(); proc.terminate()