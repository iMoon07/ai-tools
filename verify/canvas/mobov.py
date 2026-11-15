import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9650; PROF="/tmp/alur-probes/prof-mobov"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=390,844","--remote-allow-origins=*","--hide-scrollbars","about:blank"],
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
            exc.append(r["params"]["exceptionDetails"].get("text",""))
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=390,height=844,deviceScaleFactor=1,mobile=True)
send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3.4)
print(json.dumps(ev("""(()=>{
  const st=document.getElementById('stage');
  const wide=[...st.querySelectorAll('*')].filter(e=>{const b=e.getBoundingClientRect();return b.right>st.clientWidth+1;})
    .slice(0,8).map(e=>[e.tagName+'.'+(e.className||'').toString().slice(0,30), Math.round(e.getBoundingClientRect().right)]);
  return {vw:innerWidth, stage:[st.clientWidth, st.scrollWidth],
    board:[document.getElementById('board').clientWidth, document.getElementById('board').scrollWidth],
    prev:[document.getElementById('preview').clientWidth, document.getElementById('preview').scrollWidth],
    wide};
})()"""),indent=1))
print("exceptions:",exc)
ws.close(); proc.terminate()