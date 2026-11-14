import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9541; PROF="/tmp/kilo/prof-lay"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1500,1000","--remote-allow-origins=*","about:blank"],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
import websocket
def http(p,method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=method),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)

def run(w,h,label):
    t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),method="PUT")
    ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=60,suppress_origin=True)
    n=[0]
    def send(m,**p):
        n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
        while True:
            r=json.loads(ws.recv())
            if r.get("id")==n[0]:
                if r.get("method")=="Runtime.exceptionThrown": print("  [exception]",r["params"]["exceptionDetails"].get("text"))
                if r.get("error"): raise RuntimeError(r["error"])
                return r.get("result",{})
    send("Runtime.enable"); send("Page.enable")
    send("Emulation.setDeviceMetricsOverride",width=w,height=h,deviceScaleFactor=1,mobile=w<700)
    send("Page.navigate",url="http://127.0.0.1:8123/topology.html")
    time.sleep(4)
    def ev(e):
        r=send("Runtime.evaluate",expression=e,returnByValue=True)
        res=r.get("result",{})
        if res.get("subtype")=="error": return "ERR "+str(res.get("description"))[:160]
        return res.get("value")
    print(f"== {label} ==")
    print("  layout:", ev("""(()=>{const g=id=>{const e=document.getElementById(id); if(!e) return null;
        const r=e.getBoundingClientRect(); return [Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)];};
      return JSON.stringify({stage:g('stage'), dock:g('dock'), board:g('board'),
        hOverflow: document.documentElement.scrollWidth > window.innerWidth + 1,
        bodyOverflow: document.body.scrollWidth > window.innerWidth + 1,
        dockToggle: getComputedStyle(document.getElementById('dockToggle')).display});})()"""))
    print("  empty state:", ev("""(()=>{const s=JSON.parse(document.getElementById('specBox').value);
      Object.keys(s.nodes).forEach(k=>delete s.nodes[k]);
      s.edges=[]; document.getElementById('specBox').value=JSON.stringify(s,null,2);
      document.getElementById('applyBtn').click();
      return document.getElementById('board').className;})()"""))
    time.sleep(1)
    print("  empty visible:", ev("getComputedStyle(document.getElementById('empty')).display"))
    ws.close()

run(1500,1000,"desktop")
run(390,844,"mobile")
proc.terminate()
