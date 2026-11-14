import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9575; PROF="/tmp/kilo/prof-tpl2"
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
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text")); print("   [EXC]",d.get("text"),(d.get("exception") or {}).get("description","")[:110])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
def click(x,y,button="left"):
    send("Input.dispatchMouseEvent",type="mousePressed",x=x,y=y,button=button,clickCount=1)
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x,y=y,button=button,clickCount=1)
def drag(x1,y1,x2,y2):
    send("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1)
    for i in range(1,6):
        send("Input.dispatchMouseEvent",type="mouseMoved",x=x1+(x2-x1)*i/5,y=y1+(y2-y1)*i/5,button="left")
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)

groups = ev("[...document.querySelectorAll('#templateLibrary .template-group')].map(g=>({name:g.querySelector('summary').textContent, ids:[...g.querySelectorAll('[data-tpl-id]')].map(b=>b.getAttribute('data-tpl-module')+':'+b.getAttribute('data-tpl-id'))}))")
total=ok=bad=0; fails=[]
for g in groups:
    for key in g['ids']:
        mod, tid = key.split(':',1); total+=1
        ev("(()=>{const b=[...document.querySelectorAll('[data-tpl-id]')].find(x=>x.getAttribute('data-tpl-module')==='%s'&&x.getAttribute('data-tpl-id')==='%s'); if(b) b.click();})()" % (mod,tid))
        time.sleep(0.5)
        r = ev("""(()=>{const svg=document.querySelector('#stage svg'); if(!svg) return {err:'no svg'};
          return {mod:document.getElementById('stage').getAttribute('data-module'),
                  nodes:svg.querySelectorAll('[data-node-id]').length,
                  paths:svg.querySelectorAll('path').length,
                  texts:svg.querySelectorAll('text').length,
                  imgs:svg.querySelectorAll('image').length,
                  bad:[...svg.querySelectorAll('.alur-error')].map(e=>e.textContent),
                  empty:svg.children.length};})()""")
        good = r and not r.get('err') and not r.get('bad') and (r.get('nodes',0)+r.get('paths',0)+r.get('texts',0)) > 0
        if good: ok+=1
        else: bad+=1; fails.append((key,r))
print("templates:", total, "ok:", ok, "bad:", bad)
for f in fails[:6]: print("  FAIL", f)
print("exceptions:", len(errs), errs[:3])
ws.close(); proc.terminate()
