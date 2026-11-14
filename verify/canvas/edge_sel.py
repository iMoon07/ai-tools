import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9622; PROF="/tmp/kilo/prof-edgesel"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1500,1000","--remote-allow-origins=*","about:blank"],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
pt = ev("""(()=>{const p=document.querySelector('#stage .alur-layer-edges [data-edge]');
  const L=p.getTotalLength(); const q=p.getPointAtLength(L*0.5); const m=p.getScreenCTM();
  return {x:q.x*m.a+q.y*m.c+m.e, y:q.x*m.b+q.y*m.d+m.f};})()""")
send("Input.dispatchMouseEvent",type="mousePressed",x=pt['x'],y=pt['y'],button="left",clickCount=1)
send("Input.dispatchMouseEvent",type="mouseReleased",x=pt['x'],y=pt['y'],button="left",clickCount=1)
time.sleep(0.8)
print(ev("""JSON.stringify([...document.querySelectorAll('#edgeInspector select')].map(s=>({
  label:(s.closest('label')||{}).textContent, value:s.value, opts:[...s.options].map(o=>o.value)})))"""))
ws.close(); proc.terminate()
