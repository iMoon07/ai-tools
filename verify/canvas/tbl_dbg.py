import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9603; PROF="/tmp/kilo/prof-tbldbg"
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
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:240])
    return res.get("value")
def drag(x1,y1,x2,y2):
    send("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1)
    for i in range(1,7):
        send("Input.dispatchMouseEvent",type="mouseMoved",x=x1+(x2-x1)*i/6,y=y1+(y2-y1)*i/6,button="left")
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
print("blank:", ev("(()=>{const s=document.getElementById('preset'); s.value='canvas:blank'; s.dispatchEvent(new Event('change',{bubbles:true})); return document.querySelectorAll('#stage [data-node-id]').length;})()"))
time.sleep(1.0)
print("hook:", ev("""(()=>{
  window.__log=[];
  const st=document.getElementById('stage');
  ['pointerdown','mousedown'].forEach(t=>st.addEventListener(t,e=>{ if(window.__log.length<6) window.__log.push(t+':'+(e.target.tagName||'?')+':'+e.clientX+','+e.clientY); },true));
  const oc=window.__onCreate; return 'ok';})()"""))
ev("document.querySelector('.tool[data-tool=table]').click()"); time.sleep(0.2)
print("editor.tool:", ev("editor.tool"))
st = ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()")
x1,y1 = st['x']+st['w']*0.30, st['y']+st['h']*0.30
print("stage rect:", st, "press at", x1, y1, "| elementFromPoint:", ev(f"document.elementFromPoint({x1},{y1}) && document.elementFromPoint({x1},{y1}).tagName+'.'+(document.elementFromPoint({x1},{y1}).className||'')"))
drag(x1,y1,x1+260,y1+150); time.sleep(1.2)
print("log:", ev("window.__log"))
print("nodes:", ev("document.querySelectorAll('#stage [data-node-id]').length"),
      "| dragState:", ev("editor.drag ? editor.drag.type+'/'+editor.drag.shape+' moved='+editor.drag.moved : 'null'"),
      "| mode:", ev("state.spec.mode || 'n/a'"))
print("spec nodes:", ev("Object.keys(state.spec.nodes).length"), "| locked:", ev("state.spec.locked"), "| viewMode:", ev("document.body.className"))
ws.close(); proc.terminate()
