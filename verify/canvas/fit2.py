import json, subprocess, time, urllib.parse, urllib.request, shutil, os
PORT=9569; PROF="/tmp/alur-probes/prof-fit2"
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
                d=r["params"]["exceptionDetails"]; print("[EXC]",d.get("text"))
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    return r.get("result",{}).get("value")
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1400,height=900,deviceScaleFactor=1,mobile=False)
spec = {"module":"canvas","title":"T","grid":True,"width":900,"height":520,
 "nodes":{"t1":{"id":"t1","x":40,"y":40,"w":420,"h":240,"shape":"table","color":"blue",
   "columns":["Name","Role"],"rows":[["alpha","one"],["beta","two"]]}},"edges":[]}
page = """<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="css/alur.css">
<style>main{max-width:760px;margin:0 auto;padding:24px}</style></head><body><main>
<div class="alur" data-module="canvas" data-spec="%s"></div></main>
<script src="js/logo-manifest.js"></script><script src="js/alur/kit.js"></script>
<script src="js/alur/cables.js"></script><script src="js/alur/motions.js"></script>
<script src="js/alur/logos.js"></script><script src="js/alur/core.js"></script>
<script src="js/alur/modules/canvas.js"></script><script>Alur.init();</script></body></html>""" % json.dumps(spec).replace('"','&quot;')
dst='/home/moon/Projects/imoon07.github.io/tmp-fit2.html'
open(dst,'w').write(page)
try:
    send("Page.navigate",url="http://127.0.0.1:8123/tmp-fit2.html"); time.sleep(2.5)
    print(json.dumps(ev("""(()=>{const g=document.querySelector('.alur-table-node');
      const fo=g.querySelector('.alur-table-fo'), box=g.querySelector('.alur-table-box');
      const wrap=g.querySelector('.alur-table-wrap');
      const tools=wrap.querySelector('.alur-table-tools'), t=wrap.querySelector('.alur-table');
      return {foH:fo.getAttribute('height'), boxH:box.getAttribute('height'),
              toolsH:tools.offsetHeight, tableH:t.offsetHeight,
              wrapClientH:wrap.clientHeight, wrapScrollH:wrap.scrollHeight};})()"""), indent=1))
finally:
    os.remove(dst)
ws.close(); proc.terminate()
