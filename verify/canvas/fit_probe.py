import json, subprocess, time, urllib.parse, urllib.request, shutil, os
PORT=9567; PROF="/tmp/alur-probes/prof-fit"
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

spec = {"module":"canvas","title":"Table demo","grid":True,"width":900,"height":520,
 "nodes":{"t1":{"id":"t1","x":40,"y":40,"w":420,"h":240,"shape":"table","color":"blue",
   "columns":["Name","Role"],
   "rows":[["alpha","one"],["beta","two"]]}},
 "edges":[]}

page = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="css/alur.css">
<style>body{background:#0b0f14;color:#e6edf3;font:15px/1.6 ui-sans-serif;padding:0}
main{max-width:760px;margin:0 auto;padding:24px 20px}</style>
</head><body><main>
<h1>Article</h1>
<div class="alur" data-module="canvas" data-spec="%s"></div>
<div class="alur" data-module="canvas" data-editor="1" data-spec="%s"></div>
</main>
<script src="js/logo-manifest.js"></script>
<script src="js/alur/kit.js"></script><script src="js/alur/cables.js"></script>
<script src="js/alur/motions.js"></script><script src="js/alur/logos.js"></script>
<script src="js/alur/core.js"></script><script src="js/alur/modules/canvas.js"></script>
<script>Alur.init();</script>
</body></html>""" % (json.dumps(spec).replace('"','&quot;'), json.dumps(spec).replace('"','&quot;'))
dst='/home/moon/Projects/imoon07.github.io/tmp-fit.html'
open(dst,'w').write(page)
try:
    for W,H,name in [(1400,900,'desk'),(390,844,'mob')]:
        send("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=W<600)
        send("Page.navigate",url="http://127.0.0.1:8123/tmp-fit.html"); time.sleep(2.5)
        r = ev("""(()=>{const hosts=[...document.querySelectorAll('.alur')];
          return hosts.map(h=>{const svg=h.querySelector('svg');const t=h.querySelector('.alur-table');
          const hr=h.getBoundingClientRect(), tr=t?t.getBoundingClientRect():null;
          return {vb:svg.getAttribute('viewBox'), hostW:Math.round(hr.width),
                  tableW: tr?Math.round(tr.width):null,
                  tableH: tr?Math.round(tr.height):null};});})()""")
        print(name, json.dumps(r))
        print(name,"hOverflow:",ev("document.documentElement.scrollWidth > window.innerWidth + 1"))
finally:
    os.remove(dst)
ws.close(); proc.terminate()
