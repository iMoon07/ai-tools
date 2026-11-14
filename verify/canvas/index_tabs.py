import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9676; PROF="/tmp/kilo/prof-idx"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1400,1000","--remote-allow-origins=*","about:blank"],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def http(p,method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=method),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),method="PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=120,suppress_origin=True)
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
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:300])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1400,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/index.html"); time.sleep(4.5)
print("tabs:", ev("[...document.querySelectorAll('.tab')].map(b=>b.textContent.trim())"))
print("tabWork exists:", ev("!!document.getElementById('tabWork')"), "| panelWork hidden:", ev("(()=>{const p=document.getElementById('panelWork');return p?{hidden:p.hidden,display:getComputedStyle(p).display}:null;})()"))
print("active panel:", ev("(()=>{const p=[...document.querySelectorAll('.panel')].filter(x=>!x.hidden).map(x=>x.id);return p;})()"))
for i in range(ev("document.querySelectorAll('.tab').length")):
    ev("document.querySelectorAll('.tab')[%d].click()" % i); time.sleep(0.6)
    print("  tab", ev("document.querySelectorAll('.tab')[%d].textContent.trim()" % i), "->", ev("(()=>{const p=[...document.querySelectorAll('.panel')].filter(x=>!x.hidden).map(x=>x.id);return p;})()"))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
