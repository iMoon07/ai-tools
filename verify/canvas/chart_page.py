import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9625; PROF="/tmp/alur-probes/prof-chartpage"
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
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text")); print("   [EXC]", d.get("text"), (d.get("exception") or {}).get("description","")[:200])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
def snap(tag):
    print(tag, ev("""JSON.stringify({href:location.href, mod:document.getElementById('stage').getAttribute('data-module'),
      bodyKids:document.body.children.length, stageKids:document.getElementById('stage').children.length,
      stageCls:document.getElementById('stage').className, svg:!!document.querySelector('#stage svg'),
      vb:(document.querySelector('#stage svg')||{getAttribute:()=>null}).getAttribute('viewBox'),
      fixed:[...document.querySelectorAll('body > *')].filter(e=>getComputedStyle(e).position==='fixed').length})"""))
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
snap("load:")
ev("(()=>{const s=document.getElementById('preset'); s.value='canvas:blank'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(1.2)
snap("blank:")
print("chart templates:", ev("document.querySelectorAll('#templateLibrary [data-tpl-module=chart]').length"))
ev("(()=>{const b=document.querySelector('#templateLibrary [data-tpl-module=chart]'); b.click();})()"); time.sleep(1.6)
snap("after chart tpl:")
ev("document.querySelector('[data-scene-module=chart]').click()"); time.sleep(1.6)
snap("after chart block:")
print("chart nodes:", ev("document.querySelectorAll('#stage .alur-chart-node').length"),
      "| heads:", ev("document.querySelectorAll('#stage .alur-edge-head').length"))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
