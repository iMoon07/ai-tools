import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9602; PROF="/tmp/alur-probes/prof-tbltool"
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
n=[0]; errs=[]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]:
            if r.get("method")=="Runtime.exceptionThrown":
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text")); print("   [EXC]",d.get("text"),(d.get("exception") or {}).get("description","")[:160])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:220])
    return res.get("value")
def drag(x1,y1,x2,y2):
    send("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1)
    for i in range(1,7):
        send("Input.dispatchMouseEvent",type="mouseMoved",x=x1+(x2-x1)*i/6,y=y1+(y2-y1)*i/6,button="left")
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)

# blank the canvas first so nothing is under the pointer
print("blank canvas:", ev("""(()=>{const s=document.getElementById('preset'); s.value='canvas:blank'; s.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})()"""))
time.sleep(1.2)
print("nodes after blank:", ev("document.querySelectorAll('#stage [data-node-id]').length"))
print("hint text:", ev("document.getElementById('editorHint').textContent"))

ev("document.querySelector('.tool[data-tool=table]').click()"); time.sleep(0.3)
print("tool:", ev("editor.tool") if ev("typeof editor!=='undefined'") else "?", "| hint:", ev("document.getElementById('editorHint').textContent"))
st = ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()")
x1, y1 = st['x']+st['w']*0.30, st['y']+st['h']*0.30
drag(x1, y1, x1+260, y1+150)
time.sleep(1.4)
print("nodes after drag:", ev("document.querySelectorAll('#stage [data-node-id]').length"))
print("table node:", ev("""(()=>{const g=document.querySelector('.alur-table-node'); if(!g) return 'none';
  const fo=g.querySelector('.alur-table-fo');
  return {id:g.getAttribute('data-node-id'), foW:fo.getAttribute('width'), foH:fo.getAttribute('height'),
          rows:g.querySelectorAll('tbody tr').length, cols:g.querySelectorAll('thead th').length};})()"""))
h = ev("(()=>{const el=document.querySelector('.alur-handle[data-handle=se]'); if(!el) return null; const r=el.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};})()")
if h:
    drag(h['x'], h['y'], h['x']+100, h['y']+70)
    time.sleep(1.0)
    print("after resize:", ev("(()=>{const fo=document.querySelector('.alur-table-fo'); return {foW:fo.getAttribute('width'), foH:fo.getAttribute('height')};})()"))
    ev("document.querySelector('[data-table-action=add-row]').click()"); time.sleep(0.9)
    print("after +row:", ev("""(()=>{const w=document.querySelector('.alur-table-wrap');
      return {rows:document.querySelectorAll('.alur-table tbody tr').length,
              ch:w.clientHeight, sh:w.scrollHeight, foH:document.querySelector('.alur-table-fo').getAttribute('height')};})()"""))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
