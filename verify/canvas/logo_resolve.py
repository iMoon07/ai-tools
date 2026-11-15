import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9621; PROF="/tmp/alur-probes/prof-logo"
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
        if r.get("id")==n[0]: return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1400,height=900,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3.4)
print(json.dumps(ev("""(()=>{
  const L=window.AlurLogos;
  const names=['customer','waiter','warehouse','browser','node','postgres','database','server','lock','package','circle-dot','layers','cloud','zap','settings','globe','monitor','hard-drive','git-branch','radio','server-cog','si-docker'];
  const out={};
  names.forEach(n=>{ const r=L&&L.resolve?L.resolve(n):null; out[n]= r? (r.kind==='file'? r.href : r.ref) : 'NO-RESOLVE'; });
  return out;
})()"""),indent=1))
ws.close(); proc.terminate()