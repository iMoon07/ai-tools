import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9595; PROF="/tmp/alur-probes/prof-tr"
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
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text")); print("[EXC]",d.get("text"),(d.get("exception") or {}).get("description","")[:140])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
def drag(x1,y1,x2,y2):
    send("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1)
    for i in range(1,6):
        send("Input.dispatchMouseEvent",type="mouseMoved",x=x1+(x2-x1)*i/5,y=y1+(y2-y1)*i/5,button="left")
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
ev("(()=>{const b=[...document.querySelectorAll('[data-scene-module]')].find(x=>x.getAttribute('data-scene-module')==='table'); b.click();})()")
time.sleep(1.2)
m = ev("""(()=>{const g=document.querySelector('.alur-table-node'); const fo=g.querySelector('.alur-table-fo');
  const box=g.querySelector('.alur-table-box'); const wrap=g.querySelector('.alur-table-wrap');
  return {foH:fo.getAttribute('height'), boxH:box.getAttribute('height'),
          wrapH:wrap.clientHeight, scrollH:wrap.scrollHeight};})()""")
print("after insert:", m)
# resize with the se handle
h = ev("""(()=>{const r=document.querySelector('.alur-handle[data-handle=se]').getBoundingClientRect();
  return {x:r.x+r.width/2, y:r.y+r.height/2};})()""")
print("se handle at:", h)
drag(h['x'], h['y'], h['x']+120, h['y']+90)
time.sleep(1.0)
print("after resize:", ev("""(()=>{const g=document.querySelector('.alur-table-node'); const fo=g.querySelector('.alur-table-fo');
  const box=g.querySelector('.alur-table-box');
  const svg=document.querySelector('#stage svg');
  return {foW:fo.getAttribute('width'), foH:fo.getAttribute('height'),
          boxW:box.getAttribute('width'), boxH:box.getAttribute('height'),
          vb:svg.getAttribute('viewBox').slice(0,24)};})()"""))
print("table render:", ev("""(()=>{const t=document.querySelector('.alur-table'); const r=t.getBoundingClientRect();
  return {w:Math.round(r.width), h:Math.round(r.height)};})()"""))
# shrink back
h2 = ev("""(()=>{const r=document.querySelector('.alur-handle[data-handle=nw]').getBoundingClientRect();
  return {x:r.x+r.width/2, y:r.y+r.height/2};})()""")
drag(h2['x'], h2['y'], h2['x']-100, h2['y']-60)
time.sleep(1.0)
print("after nw drag:", ev("""(()=>{const g=document.querySelector('.alur-table-node'); const fo=g.querySelector('.alur-table-fo');
  return {foW:fo.getAttribute('width'), foH:fo.getAttribute('height'), x:g.getAttribute('transform')};})()"""))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
