import json, subprocess, time, urllib.parse, urllib.request, shutil, os
PORT=9561; PROF="/tmp/alur-probes/prof-tbl2"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1400,900","--remote-allow-origins=*","about:blank"],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
import websocket
def http(p,method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=method),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),method="PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=60,suppress_origin=True)
n=[0]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]:
            if r.get("method")=="Runtime.exceptionThrown":
                d=r["params"]["exceptionDetails"]; print("[EXC]",d.get("text"),(d.get("exception") or {}).get("description","")[:160])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")

spec = {"module":"canvas","title":"Table demo","grid":True,"width":760,"height":360,
 "nodes":{"t1":{"id":"t1","x":40,"y":40,"w":520,"h":260,"shape":"table","color":"blue",
   "columns":["Name","Role"],
   "rows":[["alpha","one"],["beta","two"]]}},
 "edges":[]}

page = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="css/alur.css">
<link rel="stylesheet" href="css/topology.css">
<style>body{background:#0b0f14;color:#e6edf3;font:14px ui-sans-serif;padding:20px}</style>
</head><body>
<div class="alur" data-module="canvas" data-spec="%s"></div>
<script src="js/logo-manifest.js"></script>
<script src="js/alur/kit.js"></script>
<script src="js/alur/cables.js"></script>
<script src="js/alur/motions.js"></script>
<script src="js/alur/logos.js"></script>
<script src="js/alur/core.js"></script>
<script src="js/alur/modules/canvas.js"></script>
<script>Alur.init();</script>
</body></html>""" % json.dumps(spec).replace('"','&quot;')

dst='/home/moon/Projects/imoon07.github.io/tmp-tbl.html'
open(dst,'w').write(page)
try:
    for W,H,name in [(1400,900,'desk'),(390,844,'mob')]:
        send("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=W<600)
        send("Page.navigate",url="http://127.0.0.1:8123/tmp-tbl.html"); time.sleep(2.5)
        print(name,"tables:",ev("document.querySelectorAll('.alur-table').length"),
              "tools:",ev("document.querySelectorAll('[data-table-action]').length"))
        print(name,"rows:",ev("document.querySelectorAll('.alur-table tbody tr').length"),
              "cols:",ev("document.querySelectorAll('.alur-table thead th').length"))
        ev("document.querySelector('[data-table-action=add-row]').click()"); time.sleep(0.4)
        print(name,"+Row ->",ev("document.querySelectorAll('.alur-table tbody tr').length"))
        ev("document.querySelector('[data-table-action=add-col]').click()"); time.sleep(0.4)
        print(name,"+Col ->",ev("document.querySelectorAll('.alur-table thead th').length"),
              "cells:",ev("document.querySelectorAll('.alur-table tbody tr:first-child td').length"))
        ev("document.querySelector('[data-table-action=del-row]').click()"); time.sleep(0.4)
        print(name,"-Row ->",ev("document.querySelectorAll('.alur-table tbody tr').length"))
        ev("document.querySelector('[data-table-action=del-col]').click()"); time.sleep(0.4)
        print(name,"-Col ->",ev("document.querySelectorAll('.alur-table thead th').length"))
        ev("""(()=>{const c=document.querySelector('.alur-table tbody td');c.focus();c.textContent='hello';c.dispatchEvent(new Event('input',{bubbles:true}));})()""")
        time.sleep(0.4)
        print(name,"typed:",ev("document.querySelector('.alur-table tbody td').textContent"))
        print(name,"hOverflow:",ev("document.documentElement.scrollWidth > window.innerWidth + 1"))
        print(name,"tool font:",ev("getComputedStyle(document.querySelector('.alur-table-tool')).fontSize"))
finally:
    os.remove(dst)
ws.close(); proc.terminate()
