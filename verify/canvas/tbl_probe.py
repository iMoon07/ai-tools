import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9559; PROF="/tmp/kilo/prof-tbl"
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
send("Emulation.setDeviceMetricsOverride",width=1400,height=900,deviceScaleFactor=1,mobile=False)

spec = {"module":"canvas","title":"Table demo","grid":True,"width":760,"height":360,
 "nodes":{"t1":{"id":"t1","x":40,"y":40,"w":520,"h":260,"shape":"table","color":"blue",
   "columns":["Name","Role"],
   "rows":[["alpha","one"],["beta","two"]]}},
 "edges":[]}
md = "# Table demo\n\n```draw\n" + json.dumps(spec) + "\n```\n"
open('/tmp/kilo/tbl.md','w').write(md)
# serve via data url? read.html fetches by path. Write into project temp instead.
import shutil as sh
dst='/home/moon/Projects/imoon07.github.io/docs/references/tmp-tbl.md'
open(dst,'w').write(md)

for W,H,name in [(1400,900,'desk'),(390,844,'mob')]:
    send("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=W<600)
    send("Page.navigate",url="http://127.0.0.1:8123/read.html?doc=docs/references/tmp-tbl.md")
    time.sleep(3.5)
    print(name,"blocks:",ev("document.querySelectorAll('.alur').length"),
          "tables:",ev("document.querySelectorAll('.alur-table').length"),
          "tools:",ev("document.querySelectorAll('[data-table-action]').length"))
    print(name,"rows before:",ev("document.querySelectorAll('.alur-table tbody tr').length"),
          "cols:",ev("document.querySelectorAll('.alur-table thead th').length"))
    # click + Row
    ev("document.querySelector('[data-table-action=add-row]').click()")
    time.sleep(0.5)
    print(name,"rows after +Row:",ev("document.querySelectorAll('.alur-table tbody tr').length"))
    ev("document.querySelector('[data-table-action=add-col]').click()")
    time.sleep(0.5)
    print(name,"cols after +Col:",ev("document.querySelectorAll('.alur-table thead th').length"),
          "cells/row:",ev("document.querySelectorAll('.alur-table tbody tr:first-child td').length"))
    ev("document.querySelector('[data-table-action=del-row]').click()")
    time.sleep(0.4)
    print(name,"rows after -Row:",ev("document.querySelectorAll('.alur-table tbody tr').length"))
    # type in a cell
    ev("""(()=>{const c=document.querySelector('.alur-table tbody td');c.focus();c.textContent='hello';c.dispatchEvent(new Event('input',{bubbles:true}));})()""")
    time.sleep(0.4)
    print(name,"cell text:",ev("document.querySelector('.alur-table tbody td').textContent"))
    print(name,"hOverflow:",ev("document.documentElement.scrollWidth > window.innerWidth + 1"))
shutil = None
import os
os.remove('/home/moon/Projects/imoon07.github.io/docs/references/tmp-tbl.md')
ws.close(); proc.terminate()
