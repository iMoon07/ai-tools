import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket, base64
PORT=9629; PROF="/tmp/alur-probes/prof-shotcmp"
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
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=120,suppress_origin=True)
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
ev("(()=>{const s=document.getElementById('preset'); s.value='canvas:blank'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(1.2)
ev("document.querySelector('[data-scene-module=table]').click()"); time.sleep(1.2)
ev("document.querySelector('[data-scene-module=chart]').click()"); time.sleep(2.0)
r = send("Page.captureScreenshot",format="png")
open('/tmp/alur-probes/cmp.png','wb').write(base64.b64decode(r['data']))
print("saved", ev("JSON.stringify({grid:!!document.querySelector('.alur-canvas-grid'), vb:document.querySelector('#stage svg').getAttribute('viewBox')})"))
ws.close(); proc.terminate()
