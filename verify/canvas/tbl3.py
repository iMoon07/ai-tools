import json, subprocess, time, urllib.parse, urllib.request, shutil, os
PORT=9585; PROF="/tmp/alur-probes/prof-tbl3"
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
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=90,suppress_origin=True)
n=[0]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]:
            if r.get("method")=="Runtime.exceptionThrown":
                d=r["params"]["exceptionDetails"]; print("[EXC]",d.get("text"),(d.get("exception") or {}).get("description","")[:140])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")
spec = {"module":"canvas","title":"Table demo","grid":True,"width":900,"height":520,
 "nodes":{"t1":{"id":"t1","x":40,"y":40,"w":420,"h":240,"shape":"table","color":"blue",
   "columns":["Name","Role"],
   "rows":[["alpha","one"],["beta","two"]]}},
 "edges":[]}
page = """<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="css/alur.css">
<style>body{background:#ffffff;color:#111;font:16px/1.6 ui-sans-serif}
main{max-width:760px;margin:0 auto;padding:24px}</style></head><body><main>
<h1>Article</h1><p>Before</p>
<div class="alur" data-module="canvas" data-spec="%s"></div>
<p>After</p></main>
<script src="js/logo-manifest.js"></script><script src="js/alur/kit.js"></script>
<script src="js/alur/cables.js"></script><script src="js/alur/motions.js"></script>
<script src="js/alur/logos.js"></script><script src="js/alur/core.js"></script>
<script src="js/alur/modules/canvas.js"></script><script>Alur.init();</script>
</body></html>""" % json.dumps(spec).replace('"','&quot;')
dst='/home/moon/Projects/imoon07.github.io/tmp-tbl3.html'
open(dst,'w').write(page)
try:
    for W,H,name in [(1400,900,'desk'),(390,844,'mob')]:
        send("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=W<600)
        send("Page.navigate",url="http://127.0.0.1:8123/tmp-tbl3.html"); time.sleep(2.5)
        r = ev("""(()=>{const t=document.querySelector('.alur-table');
          if(!t) return {err:'no table'};
          const box=getComputedStyle(t.closest('.alur-table-wrap'));
          const th=getComputedStyle(t.querySelector('th'));
          const td=getComputedStyle(t.querySelector('td'));
          const sc=t.closest('.alur-table-scroll');
          return {svg:!!document.querySelector('.alur svg'),
                  tables:document.querySelectorAll('.alur-table').length,
                  wrapBg:box.backgroundColor, wrapH:Math.round(t.closest('.alur-table-wrap').getBoundingClientRect().height),
                  thBg:th.backgroundColor, thBorder:th.borderBottomColor,
                  tdBorder:td.borderBottomColor,
                  scrollOverflow:getComputedStyle(sc).overflow,
                  tableH:Math.round(t.getBoundingClientRect().height),
                  pageScroll:document.documentElement.scrollHeight};})()""")
        print(name, json.dumps(r))
        ev("document.querySelector('[data-table-action=add-row]').click()"); time.sleep(0.4)
        ev("document.querySelector('[data-table-action=add-row]').click()"); time.sleep(0.5)
        print(name, "after +2 rows ->", ev("({rows:document.querySelectorAll('.alur-table tbody tr').length, tableH:Math.round(document.querySelector('.alur-table').getBoundingClientRect().height), scrollH:document.documentElement.scrollHeight, overflowX:document.documentElement.scrollWidth>window.innerWidth+1})"))
finally:
    os.remove(dst)
ws.close(); proc.terminate()
