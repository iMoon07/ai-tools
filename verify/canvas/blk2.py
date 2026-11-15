import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9583; PROF="/tmp/alur-probes/prof-blk2"
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
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text")); print("   [EXC]",d.get("text"),(d.get("exception") or {}).get("description","")[:140])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
print("excalifont loaded:", ev("document.fonts.check('13px Excalifont')"))
print("body font:", ev("getComputedStyle(document.body).fontFamily"))

# from BLANK CANVAS
ev("""(()=>{const b=[...document.querySelectorAll('#templateLibrary [data-tpl-id]')].find(x=>x.getAttribute('data-tpl-id')==='blank'); b.click();})()""")
time.sleep(0.9)
print("blank ->", ev("document.getElementById('stage').getAttribute('data-module')"), "nodes:", ev("document.querySelectorAll('#stage [data-node-id]').length"))
for blk in ['flow','reverse-proxy','chart','pipeline','graph','table']:
    ev("(()=>{const b=[...document.querySelectorAll('[data-scene-module]')].find(x=>x.getAttribute('data-scene-module')==='%s'); if(b) b.click();})()" % blk)
    time.sleep(1.0)
    print(" ", blk, "->", ev("""(()=>{const st=document.getElementById('stage');
      return {module:st.getAttribute('data-module'),
              nodes:st.querySelectorAll('[data-node-id]').length,
              liveBlocks:st.querySelectorAll('.alur-module-embed').length,
              tables:st.querySelectorAll('.alur-table').length};})()"""))

# from a FLOW scene
ev("(()=>{const b=[...document.querySelectorAll('#templateLibrary [data-tpl-module=flow]')].find(x=>/Stack 4/.test(x.textContent)); b.click();})()")
time.sleep(1.0)
print("flow scene ->", ev("document.getElementById('stage').getAttribute('data-module')"),
      "nodes:", ev("document.querySelectorAll('#stage [data-node-id]').length"))
ev("(()=>{const b=[...document.querySelectorAll('[data-scene-module]')].find(x=>x.getAttribute('data-scene-module')==='chart'); b.click();})()")
time.sleep(1.2)
print("after +Chart ->", ev("""(()=>{const st=document.getElementById('stage');
      return {module:st.getAttribute('data-module'),
              nodes:st.querySelectorAll('[data-node-id]').length,
              liveBlocks:st.querySelectorAll('.alur-module-embed').length};})()"""))
print("exceptions:", len(errs), errs[:3])
ws.close(); proc.terminate()
