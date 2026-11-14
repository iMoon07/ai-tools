import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9581; PROF="/tmp/kilo/prof-blk"
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
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)

print("block buttons:", ev("[...document.querySelectorAll('[data-scene-module]')].map(b=>b.getAttribute('data-scene-module'))"))
# start from Blank canvas
ev("""(()=>{const b=[...document.querySelectorAll('#templateLibrary [data-tpl-id]')].find(x=>x.getAttribute('data-tpl-id')==='blank'); b.click();})()""")
time.sleep(0.9)
print("blank -> module:", ev("document.getElementById('stage').getAttribute('data-module')"),
      "nodes:", ev("document.querySelectorAll('#stage [data-node-id]').length"))

for blk in ['flow','reverse-proxy','chart','pipeline','graph','table']:
    ev("(()=>{const b=[...document.querySelectorAll('[data-scene-module]')].find(x=>x.getAttribute('data-scene-module')==='%s'); if(b) b.click();})()" % blk)
    time.sleep(1.0)
    r = ev("""(()=>{const st=document.getElementById('stage');
      const modNodes=[...st.querySelectorAll('[data-node-id]')].map(g=>g.getAttribute('data-node-id'));
      return {module:st.getAttribute('data-module'),
              nodes:modNodes.length,
              moduleNodes:st.querySelectorAll('.alur-module-embed').length,
              tables:st.querySelectorAll('.alur-table').length,
              paths:st.querySelectorAll('path').length};})()""")
    print(blk, "->", r)
print("exceptions:", len(errs), errs[:3])
ws.close(); proc.terminate()
