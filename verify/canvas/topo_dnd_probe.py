import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9531; PROF="/tmp/kilo/prof-dnd"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1500,1000","--remote-allow-origins=*","about:blank"],
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
            if r.get("method")=="Runtime.exceptionThrown": print("[exception]",r["params"]["exceptionDetails"].get("text"))
            if r.get("error"): raise RuntimeError(r["error"])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": return "ERR "+str(res.get("description"))[:200]
    return res.get("value")

send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://localhost:8123/topology.html" if False else "http://127.0.0.1:8123/topology.html")
time.sleep(4)

print("tabs:", ev("""(()=>{const out=[];
  ['nodes','edges','look','logos','json'].forEach(t=>{
    document.querySelector(`.dock-tab[data-pane=${t}]`).click();
    out.push(t+':'+(document.querySelector('.pane.is-on')||{}).dataset);
  });
  document.querySelector('.dock-tab[data-pane=nodes]').click();
  return out.join(' ');})()"""))

print("before dnd:", ev("""[...document.querySelectorAll('#preview .topo-node')].map(n=>n.dataset.node+':'+(n.querySelector('.topo-icon use')||{}).getAttribute?n.querySelector('.topo-icon use').getAttribute('href'):'').join(' | ')"""))

print("dnd:", ev("""(()=>{
  const tile = document.querySelector('#logoGrid .tile[title*="docker"]') || document.querySelector('#logoGrid .tile');
  const target = document.querySelectorAll('#preview .topo-node')[1];
  if(!tile || !target) return 'missing tile/target';
  const dt = new DataTransfer();
  tile.dispatchEvent(new DragEvent('dragstart',{bubbles:true,dataTransfer:dt}));
  const logo = dt.getData('text/x-logo');
  target.dispatchEvent(new DragEvent('dragover',{bubbles:true,dataTransfer:dt}));
  target.dispatchEvent(new DragEvent('drop',{bubbles:true,dataTransfer:dt}));
  return JSON.stringify({logo: logo, node: target.dataset.node,
    highlighted: target.className});
})()"""))
time.sleep(1.5)
print("after dnd:", ev("""JSON.stringify({
  node: document.querySelectorAll('#preview .topo-node')[1].dataset.node,
  iconHref: (document.querySelectorAll('#preview .topo-node')[1].querySelector('.topo-icon use')||{}).getAttribute
     ? document.querySelectorAll('#preview .topo-node')[1].querySelector('.topo-icon use').getAttribute('href') : null,
  img: document.querySelectorAll('#preview .topo-node')[1].querySelectorAll('.topo-icon--file').length,
  specIcon: JSON.parse(document.getElementById('specBox').value).nodes[document.querySelectorAll('#preview .topo-node')[1].dataset.node][2]
})"""))
ws.close(); proc.terminate()
