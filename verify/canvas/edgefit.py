import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9622; PROF="/tmp/alur-probes/prof-edgefit"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1600,1000","--remote-allow-origins=*","--hide-scrollbars","about:blank"],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
import websocket
def http(p,method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=method),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),method="PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=90,suppress_origin=True)
n=[0]; exc=[]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]: return r.get("result",{})
        if r.get("method")=="Runtime.exceptionThrown":
            d=r["params"]["exceptionDetails"]; exc.append(d.get("text",""))
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
send("Runtime.enable"); send("Page.enable")

MEASURE = """(()=>{
  const p=document.querySelector('#preview');
  const nodes=[...p.querySelectorAll('.topo-node')].map(nd=>{
    const b=nd.getBoundingClientRect();
    return {id:nd.dataset.node||'', l:b.left, r:b.right, t:b.top, b:b.bottom};
  });
  const paths=[...p.querySelectorAll('path.topo-edge--flow, path.topo-edge--back')];
  const out=paths.map(pa=>{
    const L=pa.getTotalLength(); const m=pa.getScreenCTM();
    const a=pa.getPointAtLength(0).matrixTransform(m);
    const b=pa.getPointAtLength(L).matrixTransform(m);
    const near=(pt)=>{
      let best=1e9,who='';
      nodes.forEach(nd=>{
        const dx=Math.max(nd.l-pt.x, 0, pt.x-nd.r), dy=Math.max(nd.t-pt.y, 0, pt.y-nd.b);
        const d=Math.hypot(dx,dy); if(d<best){best=d;who=nd.id;}
      });
      return [Math.round(best),who];
    };
    return {cls:pa.getAttribute('class'), from:near(a), to:near(b)};
  });
  return {nodes:nodes.map(nd=>[nd.id, Math.round(nd.r-nd.l), Math.round(nd.b-nd.t)]), edges:out};
})()"""

def run(w, h, vertical):
    send("Emulation.setDeviceMetricsOverride",width=w,height=h,deviceScaleFactor=1,mobile=w<600)
    send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3.0)
    ev("(()=>{const t=document.getElementById('specBox');t.value=%s;return 1})()" % json.dumps("```topology\n"+json.dumps(json.load(open('/tmp/alur-probes/spec.json')))+"\n```"))
    # switch to the compact default preset instead: use the built-in starter
    ev("localStorage.clear()")
    send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3.0)
    # set layout via Look panel
    ev("document.querySelector('.dock-tab[data-pane=look]').click()"); time.sleep(0.5)
    ev("(()=>{const b=document.querySelector('#fVertical button[data-v=%d]'); if(b) b.click(); return 1})()" % (1 if vertical else 0))
    time.sleep(1.6)
    ev("document.getElementById('dockClose').click()"); time.sleep(0.9)
    return ev(MEASURE)

for vertical in (True, False):
    for (w, h) in ((1600, 1000), (390, 844)):
        r = run(w, h, vertical)
        worst = max([e['from'][0] for e in r['edges']] + [e['to'][0] for e in r['edges']] or [0])
        print(("vertical  " if vertical else "horizontal"), f"{w}x{h}", "nodes:", r['nodes'],
              "| worst gap:", worst, "px")
        if worst > 6:
            print("   edges:", json.dumps(r['edges'])[:400])
print("exceptions:", exc)
ws.close(); proc.terminate()