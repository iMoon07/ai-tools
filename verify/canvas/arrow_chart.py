import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9616; PROF="/tmp/alur-probes/prof-arrowchart"
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
ev("(()=>{const s=document.getElementById('preset'); s.value='canvas:blank'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(1.5)
vb0 = ev("document.querySelector('#stage svg').getAttribute('viewBox')")
print("viewBox before:", vb0)
ev("(()=>{const b=[...document.querySelectorAll('#templateLibrary [data-tpl-module=flow]')][0]; b.click();})()"); time.sleep(1.5)
vb1 = ev("document.querySelector('#stage svg').getAttribute('viewBox')")
print("viewBox after flow tpl:", vb1, "| same:", vb0 == vb1)
# arrow tool between first two nodes
pos = ev("""(()=>{const gs=[...document.querySelectorAll('#stage g[data-node-id]')].slice(0,2);
  return gs.map(g=>{const r=g.getBoundingClientRect(); return {x:r.x+r.width/2,y:r.y+r.height/2};});})()""")
if len(pos) == 2:
    ev("document.querySelector('.tool[data-tool=arrow]').click()"); time.sleep(0.3)
    e0 = ev("document.querySelectorAll('#stage .alur-edge').length")
    h0 = ev("document.querySelectorAll('#stage .alur-edge-head').length")
    drag(pos[0]['x'], pos[0]['y'], pos[1]['x'], pos[1]['y'])
    time.sleep(1.2)
    print("arrow:", e0, "->", ev("document.querySelectorAll('#stage .alur-edge').length"),
          "heads:", h0, "->", ev("document.querySelectorAll('#stage .alur-edge-head').length"))
# chart render
ev("document.querySelector('[data-scene-module=chart]').click()"); time.sleep(1.6)
print("chart svg:", ev("""(()=>{const g=document.querySelector('#stage .alur-chart-node'); if(!g) return 'none';
  const s=g.querySelector('.alur-module-embed svg'); if(!s) return 'no svg';
  return JSON.stringify({bars:s.querySelectorAll('rect').length, texts:s.querySelectorAll('text').length,
    sample:[...s.querySelectorAll('text')].slice(0,6).map(t=>t.textContent)});})()"""))
print("viewBox end:", ev("document.querySelector('#stage svg').getAttribute('viewBox')"))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
