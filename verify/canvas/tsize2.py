import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9597; PROF="/tmp/alur-probes/prof-ts2"
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
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=90,suppress_origin=True)
n=[0]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]:
            if r.get("method")=="Runtime.exceptionThrown":
                d=r["params"]["exceptionDetails"]; print("[EXC]",d.get("text"))
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
ev("(()=>{const b=[...document.querySelectorAll('[data-scene-module]')].find(x=>x.getAttribute('data-scene-module')==='table'); b.click();})()")
time.sleep(1.2)
print(json.dumps(ev("""(()=>{const st=document.getElementById('stage');
  const g=st.querySelector('.alur-table-node'); const t=st.querySelector('.alur-table');
  const fo=st.querySelector('.alur-table-fo'); const svg=st.querySelector('svg');
  const sr=st.getBoundingClientRect();
  const r=t.getBoundingClientRect();
  return {foW:fo.getAttribute('width'), foH:fo.getAttribute('height'),
          vb:svg.getAttribute('viewBox'),
          stageW:Math.round(sr.width),
          tableOnScreenW:Math.round(r.width), tableOnScreenH:Math.round(r.height),
          pctOfStage:Math.round(r.width/sr.width*100)+'%'};})()"""), indent=1))
ws.close(); proc.terminate()
