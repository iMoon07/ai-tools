import json, subprocess, time, urllib.parse, urllib.request, shutil, pathlib
PORT=9602; PROF="/tmp/alur-probes/prof-colcmp2"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1600,1000","--remote-allow-origins=*","about:blank"],
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
                print("  [EXC]", r["params"]["exceptionDetails"].get("text"))
            return r.get("result",{})
def ev(expr):
    r=send("Runtime.evaluate",expression=expr,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": return {"__err":res.get("description")}
    return res.get("value")
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)

SPEC=json.load(open('/tmp/alur-probes/spec.json'))
SHAPE = ("(()=>{const p=document.querySelector('.topology')||document.getElementById('preview');"
 "const ns=[...p.querySelectorAll('.topo-node')];const b=p.querySelector('.topo-canvas');"
 "return {cols:[...p.querySelectorAll('.topo-col')].length,nodes:ns.length,"
 "canvas:b?Math.round(b.getBoundingClientRect().width):0,"
 "pos:ns.map(x=>{const r=x.getBoundingClientRect();return [Math.round(r.x),Math.round(r.y)]})}})()")

# ---- A: editor (topology.html) ----
send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3.0)
ev("localStorage.clear()")
send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3.0)
ev("(()=>{const t=document.getElementById('specBox');t.value=%s;t.dispatchEvent(new Event('input',{bubbles:true}));return 1})()"
   % json.dumps("```topology\n"+json.dumps(SPEC)+"\n```"))
time.sleep(1.5)
ed_cols = ev("JSON.parse(document.getElementById('specBox').value.replace(/^\\s*```(?:topology|json)?\\s*\\n/,'').replace(/\\n?```\\s*$/,'')).columns")
print("EDITOR columns:")
print(" ", json.dumps(ed_cols))
print("EDITOR shape:", json.dumps(ev(SHAPE)))

# ---- B: article (read.html pipeline) ----
pathlib.Path('/tmp/alur-probes/colcmp2.html').write_text(
"<!doctype html><html><head><meta charset='utf-8'>"
"<link rel='stylesheet' href='http://127.0.0.1:8123/css/topology.css?v=6'>"
"<style>body{margin:0;background:#0d1117}#wrap{width:1100px;margin:0 auto;padding:24px}</style>"
"</head><body><div id='wrap'><div class='topology'></div></div>"
"<script src='http://127.0.0.1:8123/js/topology-icons.js?v=4'></script>"
"<script src='http://127.0.0.1:8123/js/topology.js?v=4'></script></body></html>")
send("Page.navigate",url="file:///tmp/alur-probes/colcmp2.html"); time.sleep(2.2)
ev("(()=>{const el=document.querySelector('.topology');window.Topology.render(el,%s);return 1})()" % json.dumps(SPEC))
time.sleep(0.8)
print("\nARTICLE shape:", json.dumps(ev(SHAPE)))
ws.close(); proc.terminate()