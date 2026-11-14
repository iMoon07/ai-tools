import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9511; PROF="/tmp/kilo/prof-paint"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1200,1000","--remote-allow-origins=*","about:blank"],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
import websocket
def http(p,method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=method),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),method="PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=60,suppress_origin=True)
n=[0]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]:
            if r.get("error"): raise RuntimeError(r["error"])
            if r.get("method")=="Runtime.exceptionThrown": print("[exception]",r["params"]["exceptionDetails"].get("text"))
            return r.get("result",{})
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1200,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/read.html?url="+urllib.parse.quote("http://127.0.0.1:8123/docs/.tmp-paint.md",safe=""))
time.sleep(7)
r=send("Runtime.evaluate",returnByValue=True,expression="""JSON.stringify({
  edges:[...document.querySelectorAll('.topo-canvas path')].map(p=>({
    cls:p.getAttribute('class'), stroke:p.getAttribute('stroke'),
    sw:p.getAttribute('stroke-width'), dash:p.getAttribute('stroke-dasharray'),
    motion:p.dataset.motion||null })),
  badges:[...document.querySelectorAll('.topo-badge, .topo-edge-badge')].map(b=>b.textContent),
  dots:document.querySelectorAll('.topo-dot').length
})""")
print(r["result"]["value"])
ws.close(); proc.terminate()
