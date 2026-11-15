import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9631; PROF="/tmp/alur-probes/prof-readw"
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
n=[0]; exc=[]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]: return r.get("result",{})
        if r.get("method")=="Runtime.exceptionThrown":
            d=r["params"]["exceptionDetails"]; exc.append(d.get("text",""))
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
send("Runtime.enable"); send("Page.enable")
for w,h,tag in ((1600,1000,'desktop'),(390,844,'mobile')):
    send("Emulation.setDeviceMetricsOverride",width=w,height=h,deviceScaleFactor=1,mobile=w<600)
    send("Page.navigate",url="http://127.0.0.1:8123/read.html?ref=index"); time.sleep(4.0)
    print(tag, json.dumps(ev("""(()=>{
      const g=s=>{const e=document.querySelector(s); if(!e) return null; const b=e.getBoundingClientRect(); return [Math.round(b.width),Math.round(b.height)];};
      return {prose:g('.prose'), content:g('#content'), layout:g('.article-layout'),
              topo:g('.topology'), canvas:g('.topo-canvas'),
              vw:innerWidth};
    })()""")))
print("exceptions:", exc)
ws.close(); proc.terminate()