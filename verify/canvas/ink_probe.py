import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9577; PROF="/tmp/alur-probes/prof-ink"
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
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text")); print("   [EXC]",d.get("text"),(d.get("exception") or {}).get("description","")[:120])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
def drag(x1,y1,x2,y2):
    send("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1)
    for i in range(1,8):
        send("Input.dispatchMouseEvent",type="mouseMoved",x=x1+(x2-x1)*i/7,y=y1+(y2-y1)*i/7,button="left")
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)

print("tool buttons:", ev("[...document.querySelectorAll('.tool[data-tool]')].map(b=>b.dataset.tool)"))
# canvas template
ev("(()=>{const b=[...document.querySelectorAll('[data-tpl-id]')].find(x=>x.getAttribute('data-tpl-module')==='canvas'); if(b) b.click();})()")
time.sleep(1.0)
print("canvas nodes:", ev("document.querySelectorAll('#stage [data-node-id]').length"))

for tool in ['arrow','line','draw']:
    ev("(()=>{const b=document.querySelector('.tool[data-tool=%s]'); if(b) b.click();})()" % ("'"+tool+"'"))
    time.sleep(0.3)
    drag(300,300,520,420)
    time.sleep(0.7)
    r = ev("""(()=>{const ds=[...document.querySelectorAll('#stage [data-drawing]')];
      return {count:ds.length, last: ds.length? {d:ds[ds.length-1].getAttribute('d').slice(0,40), cls:ds[ds.length-1].getAttribute('class')} : null};})()""")
    print(tool, "->", r)

before = ev("document.querySelectorAll('#stage [data-drawing]').length")
ev("(()=>{const b=[...document.querySelectorAll('[data-tpl-id]')].find(x=>x.getAttribute('data-tpl-module')==='flow'&&x.getAttribute('data-tpl-id')==='stack4'); if(b) b.click();})()")
time.sleep(1.0)
after = ev("document.querySelectorAll('#stage [data-drawing]').length")
print("ink before/after template:", before, after)
print("module after:", ev("document.getElementById('stage').getAttribute('data-module')"))

# undo back to canvas
send("Input.dispatchMouseEvent",type="keyDown",key="z",code="KeyZ",modifiers=2,windowsVirtualKeyCode=90)
send("Input.dispatchMouseEvent",type="keyUp",key="z",code="KeyZ",modifiers=2,windowsVirtualKeyCode=90)
time.sleep(0.9)
print("after undo module:", ev("document.getElementById('stage').getAttribute('data-module')"),
      "ink:", ev("document.querySelectorAll('#stage [data-drawing]').length"))
print("exceptions:", len(errs), errs[:3])
ws.close(); proc.terminate()
