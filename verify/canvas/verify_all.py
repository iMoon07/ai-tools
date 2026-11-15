import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9628; PROF="/tmp/alur-probes/prof-verifyall"
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
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text")); print("   [EXC]", d.get("text"), (d.get("exception") or {}).get("description","")[:180])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
def drag(x1,y1,x2,y2,steps=10):
    send("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1)
    for i in range(1,steps+1):
        send("Input.dispatchMouseEvent",type="mouseMoved",x=x1+(x2-x1)*i/steps,y=y1+(y2-y1)*i/steps,button="left")
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
print("template groups:", ev("""JSON.stringify([...document.querySelectorAll('#templateLibrary .template-group')].map(d=>({
  name:d.querySelector('summary').textContent.trim(), items:d.querySelectorAll('[data-tpl-module]').length})))"""))
ev("(()=>{const s=document.getElementById('preset'); s.value='canvas:blank'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(1.2)
# two unconnected boxes
ev("document.querySelector('.tool[data-tool=box]').click()")
stg = ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y};})()")
drag(stg['x']+200, stg['y']+260, stg['x']+320, stg['y']+320); time.sleep(0.8)
ev("document.querySelector('.tool[data-tool=select]').click()"); time.sleep(0.2)
ev("document.querySelector('.tool[data-tool=box]').click()")
drag(stg['x']+700, stg['y']+260, stg['x']+820, stg['y']+320); time.sleep(0.9)
pos = ev("""(()=>[...document.querySelectorAll('#stage g[data-node-id]')].map(g=>{const r=g.getBoundingClientRect();
  return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};}))()""")
print("boxes:", len(pos))
ev("document.querySelector('.tool[data-tool=arrow]').click()"); time.sleep(0.3)
drag(pos[0]['x'],pos[0]['y'],pos[1]['x'],pos[1]['y']); time.sleep(1.2)
print("node->node:", ev("""(()=>{const s=JSON.parse(localStorage.getItem('ruang.scene.v1')||'{}');
  return JSON.stringify({edges:(s.edges||[]).length,last:(s.edges||[]).slice(-1)[0]});})()"""),
  "heads:", ev("document.querySelectorAll('#stage .alur-edge-head').length"),
  "| status:", ev("document.getElementById('statusTool').textContent"))
# chart background like table
ev("document.querySelector('[data-scene-module=chart]').click()"); time.sleep(1.6)
print("chart node:", ev("""(()=>{const g=document.querySelector('#stage .alur-chart-node'); if(!g) return 'none';
  const r=g.querySelector('.alur-chart-box');
  return JSON.stringify({fill:r.getAttribute('fill'),stroke:r.getAttribute('stroke'),rx:r.getAttribute('rx'),
    svg:!!g.querySelector('.alur-module-embed svg')});})()"""))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
