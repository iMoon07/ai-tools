import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9666; PROF="/tmp/kilo/prof-gridm"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=390,844","--remote-allow-origins=*","about:blank"],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def http(p,method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=method),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),method="PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=120,suppress_origin=True)
n=[0]; errs=[]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]:
            if r.get("method")=="Runtime.exceptionThrown":
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text")); print("   [EXC]", d.get("text"), (d.get("exception") or {}).get("description","")[:200])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:300])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=390,height=844,deviceScaleFactor=2,mobile=True)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.5)
print("viewBar:", ev("(()=>{const b=document.getElementById('viewBar');const r=b.getBoundingClientRect();const c=getComputedStyle(b);return {box:[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)],display:c.display,vis:c.visibility};})()"))
print("gridToggle visible:", ev("(()=>{const b=document.getElementById('gridToggle');const r=b.getBoundingClientRect();const c=getComputedStyle(b);return {box:[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)],display:c.display};})()"))
print("grid on:", ev("JSON.parse(document.getElementById('stage').getAttribute('data-spec')).grid"))
ev("document.getElementById('mobileFab').click()"); time.sleep(0.6)
print("menu open:", ev("(()=>{const m=document.getElementById('mobileMenu');const b=document.getElementById('gridToggleMobile');if(!b) return 'missing';const r=b.getBoundingClientRect();return {box:[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)],on:b.classList.contains('is-on')};})()"))
ev("document.getElementById('gridToggleMobile').click()"); time.sleep(0.7)
print("after mobile toggle:", ev("JSON.parse(document.getElementById('stage').getAttribute('data-spec')).grid"),
      "| rect:", ev("(()=>{const g=document.querySelector('#stage .alur-canvas-grid');return g?[g.getAttribute('width'),g.getAttribute('height')]:null;})()"),
      "| btn on:", ev("document.getElementById('gridToggleMobile').classList.contains('is-on')"))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
