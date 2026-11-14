import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9619; PROF="/tmp/kilo/prof-arrowtypes"
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
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
def drag(x1,y1,x2,y2,steps=8):
    send("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1)
    for i in range(1,steps+1):
        send("Input.dispatchMouseEvent",type="mouseMoved",x=x1+(x2-x1)*i/steps,y=y1+(y2-y1)*i/steps,button="left")
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
def heads():
    return ev("""JSON.stringify([...document.querySelectorAll('#stage .alur-edge-head')].map(h=>({
      kind:h.getAttribute('data-arrow-kind'), tag:h.tagName, d:(h.getAttribute('d')||'').slice(0,28),
      fill:h.getAttribute('fill'), vis:getComputedStyle(h).visibility, op:getComputedStyle(h).opacity})))""")
print("initial heads:", heads())
# select first edge
ev("""(()=>{const e=document.querySelector('#stage .alur-edge'); if(e){e.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,clientX:1,clientY:1}));}})()""")
time.sleep(0.5)
print("edgeInspector visible:", ev("(()=>{const h=document.getElementById('edgeInspector'); return h? h.textContent.slice(0,60):'none';})()"))
for t in ('arrow','triangle','circle','diamond','bar','none','arrow'):
    ev(f"""(()=>{{const s=document.getElementById('edgeType'); if(!s) return 'no select';
      s.value='{t}'; s.dispatchEvent(new Event('change',{{bubbles:true}})); return s.value;}})()""")
    time.sleep(0.9)
    print(f"type {t}:", ev("document.querySelectorAll('#stage .alur-edge-head').length"), heads()[:200])
print("exceptions:", len(errs))
ws.close(); proc.terminate()
