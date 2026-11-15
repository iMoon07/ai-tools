import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9611; PROF="/tmp/alur-probes/prof-table2"
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
ev("(()=>{const s=document.getElementById('preset'); s.value='canvas:blank'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(1.2)
def tinfo(tag):
    print(tag, ev("""(()=>{const g=document.querySelector('#stage .alur-table-node'); if(!g) return 'none';
      const fo=g.querySelector('.alur-table-fo'), w=g.querySelector('.alur-table-wrap');
      return JSON.stringify({foW:fo.getAttribute('width'), foH:fo.getAttribute('height'),
        cols:g.querySelectorAll('thead th').length, rows:g.querySelectorAll('tbody tr').length,
        ch:w.clientHeight, sh:w.scrollHeight, cw:w.clientWidth, sw:w.scrollWidth,
        title:document.getElementById('inspectorTitle') ? document.getElementById('inspectorTitle').textContent : null,
        cardText:!!document.body.textContent.match(/drag to move, resize with the handles, double-click to expand/)});})()"""))
ev("document.querySelector('[data-scene-module=table]').click()"); time.sleep(1.2)
tinfo("table:")
ev("document.querySelector('[data-table-action=add-row]').click()"); time.sleep(0.9)
tinfo("after +row:")
h = ev("(()=>{const el=document.querySelector('.alur-handle[data-handle=se]'); if(!el) return null; const r=el.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};})()")
if h:
    drag(h['x'],h['y'],h['x']+80,h['y']+50); time.sleep(1.0); tinfo("after resize:")
# chart node check
ev("(()=>{const b=[...document.querySelectorAll('#templateLibrary [data-tpl-module=chart]')].pop(); b.click();})()"); time.sleep(1.5)
print("chart node:", ev("""(()=>{const g=document.querySelector('#stage .alur-chart-node'); if(!g) return 'none';
   return JSON.stringify({svg:!!g.querySelector('.alur-module-embed svg'), fo:g.querySelector('.alur-chart-fo').getAttribute('width'),
     h:g.querySelector('.alur-chart-fo').getAttribute('height')});})()"""))
# select chart -> inspector should not be "Card"
ev("(()=>{const g=document.querySelector('#stage .alur-chart-node'); const r=g.getBoundingClientRect(); window.__c={x:r.x+r.width/2,y:r.y+r.height/2};})()")
c = ev("window.__c")
send("Input.dispatchMouseEvent",type="mousePressed",x=c['x'],y=c['y'],button="left",clickCount=1)
send("Input.dispatchMouseEvent",type="mouseReleased",x=c['x'],y=c['y'],button="left",clickCount=1)
time.sleep(0.8)
print("chart selected inspector:", ev("document.querySelector('.inspector-title, #inspectorTitle') ? document.querySelector('.inspector-title, #inspectorTitle').textContent : 'n/a'"),
      "| cardCtl:", ev("!!document.body.textContent.match(/Front\\s*Back|Expand/)"))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
