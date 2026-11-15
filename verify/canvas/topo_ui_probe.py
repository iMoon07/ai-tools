import json, subprocess, time, urllib.parse, urllib.request, shutil

PORT=9521; PROF="/tmp/alur-probes/prof-ui"
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

def newtab():
    t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),method="PUT")
    ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=60,suppress_origin=True)
    n=[0]
    def send(m,**p):
        n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
        while True:
            r=json.loads(ws.recv())
            if r.get("id")==n[0]:
                if r.get("method")=="Runtime.exceptionThrown": print("  [exception]",r["params"]["exceptionDetails"].get("text"))
                if r.get("method")=="Runtime.consoleAPICalled":
                    a=r["params"]["args"]; print("  [console]"," ".join(str(x.get("value",x.get("description"))) for x in a))
                if r.get("error"): raise RuntimeError(r["error"])
                return r.get("result",{})
    return ws,send

def run(width,height,label):
    ws,send=newtab()
    send("Runtime.enable"); send("Page.enable")
    send("Emulation.setDeviceMetricsOverride",width=width,height=height,deviceScaleFactor=1,mobile=width<700)
    send("Page.navigate",url="http://127.0.0.1:8123/topology.html")
    time.sleep(4)
    def ev(e):
        r=send("Runtime.evaluate",expression=e,returnByValue=True)
        res=r.get("result",{})
        if res.get("subtype")=="error": return "ERR "+str(res.get("description"))[:200]
        return res.get("value")
    print(f"== {label} ({width}x{height}) ==")
    print("  render:", ev("""JSON.stringify({
      nodes: document.querySelectorAll('#preview .topo-node').length,
      edges: document.querySelectorAll('#preview path.topo-edge--flow, #preview path.topo-edge--back').length,
      badges: [...document.querySelectorAll('#preview text')].map(t=>t.textContent),
      edgeColors: [...document.querySelectorAll('#preview path.topo-edge--flow, #preview path.topo-edge--back')].map(p=>p.getAttribute('stroke')),
      nodeCards: document.querySelectorAll('#nodeList .card').length,
      edgeCards: document.querySelectorAll('#edgeList .card').length,
      title: document.getElementById('docTitle').textContent,
      legend: [document.getElementById('lgFlow').textContent, document.getElementById('lgBack').textContent]
    })"""))
    # switch tabs
    for tab in ['edges','look','logos','json','nodes']:
        ev(f"document.querySelector('.dock-tab[data-pane={tab}]').click()")
    print("  tabs ok:", ev("[...document.querySelectorAll('.dock-pane')].filter(p=>p.classList.contains('is-on')).length"))
    # add an edge and style it
    ev("document.querySelector('.dock-tab[data-pane=edges]').click()")
    print("  add edge:", ev("""(()=>{const n=document.querySelectorAll('#edgeList .card').length;
      document.getElementById('addEdge').click();
      return n+' -> '+document.querySelectorAll('#edgeList .card').length;})()"""))
    time.sleep(1)
    print("  after add:", ev("""JSON.stringify({
      edges: document.querySelectorAll('#preview path.topo-edge--flow, #preview path.topo-edge--back').length,
      cards: document.querySelectorAll('#edgeList .card').length
    })"""))
    # apply context to all edges
    ev("document.querySelector('.dock-tab[data-pane=look]').click()")
    ev("""(()=>{const f=document.getElementById('fFlow'); f.value='Request';
      f.dispatchEvent(new Event('input',{bubbles:true}));
      const b=document.getElementById('fBack'); b.value='Response';
      b.dispatchEvent(new Event('input',{bubbles:true}));
      document.getElementById('applyCtx').click(); return 1;})()""")
    time.sleep(1)
    print("  context badges:", ev("[...document.querySelectorAll('#preview text')].map(t=>t.textContent).join(' | ')"))
    # drag a logo onto a node
    print("  logo tiles:", ev("document.querySelectorAll('#logoGrid .tile').length"))
    print("  drag data set:", ev("""(()=>{const t=document.querySelector('#logoGrid .tile');
      if(!t) return 'no tile'; return t.title;})()"""))
    print("  legend bar:", ev("document.getElementById('lgFlow').textContent+' / '+document.getElementById('lgBack').textContent"))
    ws.close()

run(1500,1000,"desktop")
run(390,844,"mobile")
proc.terminate()
