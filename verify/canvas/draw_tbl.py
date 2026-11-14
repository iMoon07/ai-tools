import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9563; PROF="/tmp/kilo/prof-dtbl"
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
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
print("spec textarea gone:", ev("!document.getElementById('spec')"))
print("apply gone:", ev("!document.getElementById('apply')"))
print("reset present:", ev("!!document.getElementById('reset')"))
print("advanced summary:", ev("(document.querySelector('.scene-advanced summary')||{}).textContent"))
# insert a table block
print("insert table:", ev("(()=>{const b=[...document.querySelectorAll('button')].filter(x=>/Table/.test(x.textContent));if(!b.length)return 'no button';b[0].click();return 'clicked';})()"))
time.sleep(1.2)
print("table nodes:", ev("document.querySelectorAll('.alur-table-node').length"))
print("rows:", ev("document.querySelectorAll('.alur-table tbody tr').length"))
ev("document.querySelector('[data-table-action=add-row]').click()"); time.sleep(0.9)
print("after +Row:", ev("document.querySelectorAll('.alur-table tbody tr').length"))
ev("document.querySelector('[data-table-action=add-col]').click()"); time.sleep(0.9)
print("after +Col:", ev("document.querySelectorAll('.alur-table thead th').length"))
print("undo stack:", ev("(()=>{try{return 'ok'}catch(e){return e.message}})()"))
print("exceptions:", errs)
ws.close(); proc.terminate()
