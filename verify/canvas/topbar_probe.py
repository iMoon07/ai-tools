import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9565; PROF="/tmp/kilo/prof-tb"
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
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=60,suppress_origin=True)
n=[0]; errs=[]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]:
            if r.get("method")=="Runtime.exceptionThrown":
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text")); print("[EXC]",d.get("text"),(d.get("exception") or {}).get("description","")[:200])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")
for W,H,name in [(1500,1000,'desk'),(390,844,'mob')]:
    send("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=W<600)
    send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3)
    print(name,"brand name:",ev("document.querySelector('.brand-name').textContent"))
    print(name,"brand sub:",ev("document.querySelector('.brand-sub').textContent"))
    print(name,"avatar loaded:",ev("(()=>{const i=document.querySelector('.brand-avatar');return i.complete && i.naturalWidth>0})()"))
    print(name,"docTitle value:",ev("document.getElementById('docTitle').value"))
    print(name,"status:",ev("document.getElementById('topStatus').textContent"))
    print(name,"nav:",ev("[...document.querySelectorAll('.top-link')].map(a=>a.textContent.trim())"))
    print(name,"hOverflow:",ev("document.documentElement.scrollWidth > window.innerWidth + 1"))
# title typing syncs spec
ev("window.confirm=function(){return true}")
ev("""(()=>{const t=document.getElementById('docTitle');t.focus();t.value='Pipeline';t.dispatchEvent(new Event('input',{bubbles:true}));})()""")
time.sleep(0.6)
print("after type status:",ev("document.getElementById('topStatus').textContent"))
print("fenced title:",ev("(JSON.parse(document.getElementById('specBox')?1:0)||0)"))
ev("document.querySelector('.dock-tab[data-pane=json]').click()"); time.sleep(0.4)
print("fence has title:",ev("document.getElementById('specBox').value.indexOf('Pipeline')>=0"))
print("exceptions:",errs)
ws.close(); proc.terminate()
