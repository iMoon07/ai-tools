import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9573; PROF="/tmp/kilo/prof-tpl"
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
                d=r["params"]["exceptionDetails"]
                msg=d.get("text"); errs.append(msg); print("   [EXC]",msg,(d.get("exception") or {}).get("description","")[:110])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)

groups = ev("[...document.querySelectorAll('#templateLibrary .template-group')].map(g=>({name:g.querySelector('summary').textContent, ids:[...g.querySelectorAll('[data-tpl-id]')].map(b=>b.getAttribute('data-tpl-module')+':'+b.getAttribute('data-tpl-id'))}))")
print("groups:", [(g['name'], len(g['ids'])) for g in groups])
total=ok=bad=0
for g in groups:
    for key in g['ids']:
        mod, tid = key.split(':',1)
        total+=1
        ev("(()=>{const b=[...document.querySelectorAll('[data-tpl-id]')].find(x=>x.getAttribute('data-tpl-module')==='%s'&&x.getAttribute('data-tpl-id')==='%s'); if(b) b.click();})()" % (mod,tid))
        time.sleep(0.55)
        r = ev("""(()=>{const svg=document.querySelector('#stage svg'); if(!svg) return {err:'no svg'};
          const mod=document.getElementById('stage').getAttribute('data-module');
          const nodes=svg.querySelectorAll('[data-node-id]').length;
          const paths=svg.querySelectorAll('path').length;
          const texts=svg.querySelectorAll('text').length;
          const bad=[...svg.querySelectorAll('.alur-error')].map(e=>e.textContent);
          return {mod,nodes,paths,texts,bad};})()""")
        good = r and not r.get('err') and not r.get('bad') and r.get('nodes',0) > 0
        if good: ok+=1
        else:
            bad+=1
            print("  FAIL", key, "->", r)
print("templates:", total, "ok:", ok, "bad:", bad)
print("exceptions:", len(errs))
ws.close(); proc.terminate()
