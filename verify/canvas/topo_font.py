import json, subprocess, time, urllib.parse, urllib.request, shutil, os
PORT=9587; PROF="/tmp/alur-probes/prof-tf"
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
send("Emulation.setDeviceMetricsOverride",width=1400,height=900,deviceScaleFactor=1,mobile=False)
spec = {"title":"Request / Response","columns":[["C"],["P"],["K"]],
 "nodes":{"C":["Customer","browser","customer","client"],
          "P":["API","node","waiter","process"],
          "K":["Database","postgres","warehouse","database"]},
 "edges":[["C","P","Request"],["P","K","Query"],["K","P","Rows",True],["P","C","Response",True]],
 "badges":True}
page = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="css/shell.css"><link rel="stylesheet" href="css/article.css">
<link rel="stylesheet" href="css/topology.css?v=5">
<style>.prose{max-width:760px;margin:0 auto;padding:20px}</style></head>
<body><div class="prose"><div class="topology" data-spec="%s"></div>
<p style="font-family:ui-sans-serif">plain paragraph</p></div>
<script src="js/logo-manifest.js"></script><script src="js/alur/kit.js"></script>
<script src="js/alur/logos.js"></script><script src="js/topology-icons.js"></script>
<script src="js/topology.js"></script>
<script>Topology.init();</script></body></html>""" % json.dumps(spec).replace('"','&quot;')
dst='/home/moon/Projects/imoon07.github.io/tmp-topofont.html'
open(dst,'w').write(page)
try:
    send("Page.navigate",url="http://127.0.0.1:8123/tmp-topofont.html"); time.sleep(3)
    print("topo font:", ev("getComputedStyle(document.querySelector('.topo')).fontFamily"))
    print("node font:", ev("getComputedStyle(document.querySelector('.topo-node')).fontFamily"))
    print("edge label font:", ev("(()=>{const t=document.querySelector('.topo text, .topo-label, .topo-edge-label'); return t?getComputedStyle(t).fontFamily:'(none)'})()"))
    print("paragraph font:", ev("getComputedStyle(document.querySelector('.prose p')).fontFamily"))
    print("nodes:", ev("document.querySelectorAll('.topo-node').length"), "paths:", ev("document.querySelectorAll('.topo svg path').length"))
    print("font loaded:", ev("document.fonts.check('13px Excalifont')"))
finally:
    os.remove(dst)
ws.close(); proc.terminate()
