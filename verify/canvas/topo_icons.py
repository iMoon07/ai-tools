import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9613; PROF="/tmp/alur-probes/prof-icons"
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
        if r.get("id")==n[0]: return r.get("result",{})
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3.5)
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}

print("sprite symbols:", ev("document.querySelectorAll('#topology-sprite symbol').length"))
print("default preset render:", json.dumps(ev("""(()=>{
  const nodes=[...document.querySelectorAll('#preview .topo-node')];
  return nodes.map(nd=>{
    const ic=nd.querySelector('.topo-node-icon');
    const use=ic?ic.querySelector('use'):null;
    return {label:(nd.querySelector('.topo-node-label')||{}).textContent,
            iconName:use?use.getAttribute('href'):null,
            iconExists: use? !!document.querySelector(use.getAttribute('href')) : null,
            iconBox: ic? Math.round(ic.getBoundingClientRect().width):0};
  });
})()""")))

print("\npreset icon audit:")
print(json.dumps(ev("""(()=>{
  const has=n=>!!document.querySelector('#i-'+n);
  const out=[];
  (window.PRESETS||[]).forEach(p=>{
    const bad=[];
    Object.values(p.spec.nodes||{}).forEach(nd=>{
      const icon=Array.isArray(nd)?nd[2]:null;
      if(icon && !has(icon)) bad.push(icon);
    });
    ((p.spec.facilities||[]).filter(Array.isArray)).forEach(f=>{ if(f[0]&&!has(f[0])) bad.push('fac:'+f[0]); });
    out.push({id:p.id||p.label, bad:[...new Set(bad)]});
  });
  return out;
})()"""), indent=1))

print("\nuser spec icons:")
SPEC=json.load(open('/tmp/alur-probes/spec.json'))
icons=sorted({v[2] for v in SPEC['nodes'].values() if isinstance(v,list) and len(v)>2})
print(json.dumps(ev("(()=>{const has=n=>!!document.querySelector('#i-'+n);return %s.map(n=>[n,has(n)])})()" % json.dumps(icons))))
ws.close(); proc.terminate()