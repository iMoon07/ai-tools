import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9571; PROF="/tmp/kilo/prof-smoke"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1400,900","--remote-allow-origins=*","about:blank"],
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
                d=r["params"]["exceptionDetails"]; print("   [EXC]",d.get("text"),(d.get("exception") or {}).get("description","")[:120])
            return r.get("result",{})
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1400,height=900,deviceScaleFactor=1,mobile=False)
for url in ["index.html","draw.html","topology.html","references.html?ref=index","read.html?ref=index","about.html","blog.html"]:
    send("Page.navigate",url="http://127.0.0.1:8123/"+url); time.sleep(2.6)
    r=send("Runtime.evaluate",expression="({title:document.title,h:document.body.scrollHeight})",returnByValue=True)
    print(url, "->", r.get("result",{}).get("value"))
ws.close(); proc.terminate()
