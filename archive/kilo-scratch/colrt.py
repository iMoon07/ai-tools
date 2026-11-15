import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9603; PROF="/tmp/kilo/prof-colrt"
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
send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3.0)
ev("localStorage.clear()")
send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3.0)

def paste(spec):
    ev("(()=>{const t=document.getElementById('specBox');t.value=%s;t.dispatchEvent(new Event('input',{bubbles:true}));return 1})()"
       % json.dumps("```topology\n"+json.dumps(spec)+"\n```"))
    time.sleep(1.2)
    return ev("JSON.parse(document.getElementById('specBox').value.replace(/^\\s*```(?:topology|json)?\\s*\\n/,'').replace(/\\n?```\\s*$/,''))")

SPEC=json.load(open('/tmp/kilo/spec.json'))

print("== 1. paste spec with columns ==")
out=paste(SPEC)
print("  columns:",json.dumps(out['columns']))
print("  cols rendered:",ev("[...document.querySelectorAll('#preview .topo-col')].length"))
print("  _col/_grid leaked:",ev("Object.values(window.__x||{}).length||0"),
      ev("(()=>{const t=document.getElementById('specBox').value;return /_col|_grid/.test(t)})()"))

print("== 2. add node after paste ==")
ev("document.getElementById('addNode').click()")
time.sleep(1.0)
out=ev("JSON.parse(document.getElementById('specBox').value.replace(/^\\s*```(?:topology|json)?\\s*\\n/,'').replace(/\\n?```\\s*$/,''))")
print("  columns:",json.dumps(out['columns'])[:220])
print("  leaked:",ev("(()=>{const t=document.getElementById('specBox').value;return /_col|_grid/.test(t)})()"))

print("== 3. paste spec WITHOUT columns (fallback) ==")
plain={"title":"Plain","nodes":{"A":["A","a","circle-dot","process"],"B":["B","b","circle-dot","process"],"C":["C","c","circle-dot","process"]},
       "edges":[["A","B"],["B","C"]]}
out=paste(plain)
print("  columns:",json.dumps(out['columns']))
print("  cols rendered:",ev("[...document.querySelectorAll('#preview .topo-col')].length"))

print("== 4. default preset untouched ==")
send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(2.6)
ev("localStorage.clear()")
send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(2.6)
print("  columns:",json.dumps(ev("JSON.parse(document.getElementById('specBox').value.replace(/^\\s*```(?:topology|json)?\\s*\\n/,'').replace(/\\n?```\\s*$/,'')).columns"))[:200])
print("  cols rendered:",ev("[...document.querySelectorAll('#preview .topo-col')].length"))
print("  exceptions above: none")
ws.close(); proc.terminate()