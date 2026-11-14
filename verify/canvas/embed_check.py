import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9647; PROF="/tmp/kilo/prof-embed"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1400,1000","--remote-allow-origins=*","about:blank"],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def http(p,method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=method),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),method="PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=90,suppress_origin=True)
n=[0]; errs=[]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]:
            if r.get("method")=="Runtime.exceptionThrown":
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text")); print("   [EXC]", d.get("text"), (d.get("exception") or {}).get("description","")[:180])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1400,height=1000,deviceScaleFactor=1,mobile=False)
for url in ("read.html","references.html"):
    errs.clear()
    send("Page.navigate",url="http://127.0.0.1:8123/"+url); time.sleep(4.5)
    print(url, "->", ev("""(()=>{const h=[...document.querySelectorAll('[data-module]')];
      const r=h.map(x=>({mod:x.getAttribute('data-module'),ready:x.hasAttribute('data-ready'),
        svg:!!x.querySelector('svg'),nodes:x.querySelectorAll('[data-node-id]').length}));
      return JSON.stringify({hosts:h.length,r:JSON.stringify(r),h:document.body.scrollHeight});})()"""))
    print("   exceptions:", len(errs), errs[:2])
ws.close(); proc.terminate()
