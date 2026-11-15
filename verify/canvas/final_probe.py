import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9601; PROF="/tmp/alur-probes/prof-final"
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
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text")); print("   [EXC]",d.get("text"),(d.get("exception") or {}).get("description","")[:150])
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
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y2=y2,button="left",clickCount=1)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)

print("tools:", ev("[...document.querySelectorAll('.tool[data-tool]')].map(b=>b.dataset.tool)"))

# 1) template click inserts, does not replace
before = ev("document.getElementById('stage').getAttribute('data-module')")
ev("(()=>{const b=[...document.querySelectorAll('#templateLibrary [data-tpl-module=graph]')][0]; b.click();})()")
time.sleep(1.2)
print("template click -> module:", ev("document.getElementById('stage').getAttribute('data-module')"),
      "liveBlocks:", ev("document.querySelectorAll('.alur-module-embed').length"),
      "nodes:", ev("document.querySelectorAll('#stage [data-node-id]').length"))
ev("(()=>{const b=[...document.querySelectorAll('#templateLibrary [data-tpl-module=chart]')].pop(); b.click();})()")
time.sleep(1.2)
print("second template -> liveBlocks:", ev("document.querySelectorAll('.alur-module-embed').length"))

# 2) table tool drag-to-size
ev("document.querySelector('.tool[data-tool=table]').click()"); time.sleep(0.3)
st = ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()")
drag(st['x']+st['w']*0.15, st['y']+st['h']*0.25, st['x']+st['w']*0.15+260, st['y']+st['h']*0.25+150)
time.sleep(1.2)
print("drag table ->", ev("""(()=>{const g=document.querySelector('.alur-table-node'); if(!g) return 'none';
  const fo=g.querySelector('.alur-table-fo');
  return {foW:fo.getAttribute('width'), foH:fo.getAttribute('height'),
          rows:g.querySelectorAll('tbody tr').length, cols:g.querySelectorAll('thead th').length};})()"""))
# resize it
h = ev("(()=>{const r=document.querySelector('.alur-handle[data-handle=se]').getBoundingClientRect();return {x:r.x+4,y:r.y+4};})()")
drag(h['x'], h['y'], h['x']+90, h['y']+60)
time.sleep(1.0)
print("after resize ->", ev("(()=>{const fo=document.querySelector('.alur-table-fo'); return {foW:fo.getAttribute('width'), foH:fo.getAttribute('height')};})()"))
# add rows, check no scroll
ev("document.querySelector('[data-table-action=add-row]').click()"); time.sleep(0.8)
print("rows now:", ev("document.querySelectorAll('.alur-table tbody tr').length"),
      "scroll:", ev("(()=>{const w=document.querySelector('.alur-table-wrap'); return {ch:w.clientHeight, sh:w.scrollHeight};})()"))

# 3) cable controls on reverse proxy
ev("""(()=>{const s=document.getElementById('preset'); s.value='reverse-proxy:simple'; s.dispatchEvent(new Event('change',{bubbles:true}));})()""")
time.sleep(1.2)
print("reverse-proxy linkControls visible:", ev("getComputedStyle(document.getElementById('linkControls')).display"),
      "hint:", ev("document.querySelector('#linkControls .hint').textContent"))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
