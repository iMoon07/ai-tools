import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9612; PROF="/tmp/kilo/prof-final2"
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
def drag(x1,y1,x2,y2):
    send("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1)
    for i in range(1,7):
        send("Input.dispatchMouseEvent",type="mouseMoved",x=x1+(x2-x1)*i/6,y=y1+(y2-y1)*i/6,button="left")
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
ev("(()=>{const s=document.getElementById('preset'); s.value='canvas:blank'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(1.5)
ev("(()=>{const b=[...document.querySelectorAll('#templateLibrary [data-tpl-module=reverse-proxy]')][0]; b.click();})()"); time.sleep(1.5)
print("proxy:", ev("""JSON.stringify((()=>{const s=JSON.parse(localStorage.getItem('ruang.scene.v1')||'{}');
  return {nodes:Object.keys(s.nodes||{}).length, edges:(s.edges||[]).length,
          cables:(s.edges||[]).map(e=>e.cable||'-')};})())"""))
print("cardNodes:", ev("document.querySelectorAll('#stage .alur-module-node').length"),
      "boxes:", ev("document.querySelectorAll('#stage .alur-canvas-node').length"))
# chart template
ev("(()=>{const b=[...document.querySelectorAll('#templateLibrary [data-tpl-module=chart]')].pop(); b.click();})()"); time.sleep(1.5)
c = ev("""(()=>{const g=document.querySelector('#stage .alur-chart-node'); if(!g) return null;
  const r=g.getBoundingClientRect(); return {x:r.x+r.width/2,y:r.y+r.height/2,w:r.width,h:r.height};})()""")
print("chart node box:", c)
send("Input.dispatchMouseEvent",type="mousePressed",x=c['x'],y=c['y'],button="left",clickCount=1)
send("Input.dispatchMouseEvent",type="mouseReleased",x=c['x'],y=c['y'],button="left",clickCount=1)
time.sleep(0.8)
print("inspector:", ev("""(()=>{const t=document.querySelector('#inspectorTitle');
  const panel=document.querySelector('.inspector, #nodeInspector');
  return JSON.stringify({title:t?t.textContent:null,
    hasExpand:!!(panel&&panel.textContent.match(/Expand/)),
    hasLabel:!!document.getElementById('nodeLabel'),
    selected:document.querySelectorAll('#stage .is-selected').length});})()"""))
# drag chart node
send("Input.dispatchMouseEvent",type="mousePressed",x=c['x'],y=c['y'],button="left",clickCount=1)
for i in range(1,7):
    send("Input.dispatchMouseEvent",type="mouseMoved",x=c['x']+i*12,y=c['y']+i*8,button="left")
send("Input.dispatchMouseEvent",type="mouseReleased",x=c['x']+72,y=c['y']+48,button="left",clickCount=1)
time.sleep(0.8)
print("after drag:", ev("""(()=>{const s=JSON.parse(localStorage.getItem('ruang.scene.v1')||'{}');
  const n=Object.values(s.nodes||{}).find(x=>x.shape==='chart'); return n?JSON.stringify({x:n.x,y:n.y}):'gone';})()"""))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
