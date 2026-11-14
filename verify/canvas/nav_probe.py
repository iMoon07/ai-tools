import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9557; PROF="/tmp/kilo/prof-nav"
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
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),method="PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=60,suppress_origin=True)
n=[0]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]:
            if r.get("method")=="Runtime.exceptionThrown":
                d=r["params"]["exceptionDetails"]; print("[EXC]",d.get("text"),(d.get("exception") or {}).get("description","")[:140])
            return r.get("result",{})
def ev(expr):
    r=send("Runtime.evaluate",expression=expr,returnByValue=True,awaitPromise=True)
    return r.get("result",{}).get("value")
send("Runtime.enable"); send("Page.enable")
for W,H,name in [(1500,1000,'desk'),(390,844,'mob')]:
    send("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=W<600)
    send("Page.navigate",url="http://127.0.0.1:8123/topology.html")
    time.sleep(3)
    print(name,"nav:",ev("[...document.querySelectorAll('.top-link')].map(a=>a.textContent.trim()+'->'+a.getAttribute('href'))"))
    print(name,"top-right:",ev("[...document.querySelectorAll('.top-right button')].map(b=>b.textContent.trim())"))
    print(name,"hOverflow:",ev("document.documentElement.scrollWidth > window.innerWidth + 1"))
    print(name,"topbar h:",ev("Math.round(document.querySelector('.topbar').getBoundingClientRect().height)"))
    print(name,"brand:",repr(ev("document.querySelector('.brand').textContent.trim()")))
    print(name,"starter select:",ev("!!document.getElementById('presetSel')"), ev("document.querySelectorAll('#presetSel option').length"))
ws.close(); proc.terminate()
