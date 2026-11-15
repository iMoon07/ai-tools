import json, subprocess, time, urllib.parse, urllib.request, shutil, pathlib
PORT=9601; PROF="/tmp/alur-probes/prof-colcmp"
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

# --- A: editor ---
send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3.2)
print("editor loaded:", ev("typeof window.Topology"))
ev("localStorage.clear()")
send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3.2)
js = "(()=>{const t=document.getElementById('specBox');t.value=%s;t.dispatchEvent(new Event('input',{bubbles:true}));t.dispatchEvent(new Event('blur',{bubbles:true}));return 1})()" % json.dumps("```topology\n"+json.dumps(SPEC,indent=2)+"\n```")
ev(js); time.sleep(1.4)
print("\n-- editor columns --")
print(json.dumps(ev("JSON.parse(document.getElementById('specBox').value).columns"),indent=0)[:400])
print("-- editor preview --")
print(json.dumps(ev("(()=>{const p=document.getElementById('preview');const ns=[...p.querySelectorAll('.topo-node')];const b=p.querySelector('.topo-canvas');return {cols:[...p.querySelectorAll('.topo-col')].length,nodes:ns.length,canvas:b?b.getBoundingClientRect().width:0,first:ns.slice(0,4).map(x=>{const r=x.getBoundingClientRect();return [Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)]})}})()")))

# --- B: article (read.html pipeline) ---
page = pathlib.Path('/tmp/alur-probes/colcmp.html')
page.write_text("""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="http://127.0.0.1:8123/css/topology.css?v=6">
<style>body{margin:0;background:#0d1117;color:#c9d1d9;font:14px system-ui}#wrap{width:1100px;margin:0 auto;padding:24px}</style>
</head><body><div id="wrap"><div class="topology" data-spec="%s"></div></div>
<script src="http://127.0.0.1:8123/js/topology-icons.js?v=4"></script>
<script src="http://127.0.0.1:8123/js/topology.js?v=4"></script></body></html>""" % json.dumps(json.dumps(SPEC)).replace('"','&quot;'))
send("Page.navigate",url="file:///tmp/alur-probes/colcmp.html"); time.sleep(2.6)
print("\n-- article columns --")
print(json.dumps(ev("(()=>{const p=document.querySelector('.topology');const ns=[...p.querySelectorAll('.topo-node')];const b=p.querySelector('.topo-canvas');return {cols:[...p.querySelectorAll('.topo-col')].length,nodes:ns.length,canvas:b?Math.round(b.getBoundingClientRect().width):0,first:ns.slice(0,4).map(x=>{const r=x.getBoundingClientRect();return [Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)]})}})()")))
ws.close(); proc.terminate()