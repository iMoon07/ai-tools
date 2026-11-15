import json, subprocess, time, urllib.parse, urllib.request, shutil, base64
PORT=9612; PROF="/tmp/alur-probes/prof-topo3"
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
print(json.dumps(ev("""(()=>{
 const cs=e=>{const s=getComputedStyle(e);return {fs:s.fontSize,lh:s.lineHeight,c:s.color,bg:s.backgroundColor,pad:s.padding,br:s.borderRadius}};
 const r=e=>{const b=e.getBoundingClientRect();return [Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height)]};
 const q=s=>document.querySelector(s);
 const node=q('#preview .topo-node');
 const out={};
 out.page={top:r(q('header')||document.body), h1:cs(q('h1')||document.body)};
 out.board=r(q('#board'));
 out.canvas=r(q('#preview .topo-canvas'));
 out.svg=r(q('#preview svg'));
 out.node={box:r(node), style:cs(node)};
 out.nodeParts=[...node.children].map(c=>[c.className,r(c),cs(c).fs]);
 const lbl=node.querySelector('.topo-node-label')||node.querySelector('strong');
 if(lbl) out.label={text:lbl.textContent, box:r(lbl), style:cs(lbl)};
 const sub=node.querySelector('.topo-node-sub');
 if(sub) out.sub={text:sub.textContent, box:r(sub), style:cs(sub)};
 out.paths=[...document.querySelectorAll('#preview .topo-svg path')].map(p=>({cls:p.getAttribute('class'),d:(p.getAttribute('d')||'').slice(0,60),stroke:p.getAttribute('stroke'),dash:p.getAttribute('stroke-dasharray'),mk:p.getAttribute('marker-end')}));
 out.texts=[...document.querySelectorAll('#preview .topo-svg text')].map(t=>({txt:t.textContent,x:t.getAttribute('x'),y:t.getAttribute('y'),cls:t.getAttribute('class'),bg:t.getAttribute('fill')}));
 out.labels=[...document.querySelectorAll('#preview .topo-svg .topo-badge, #preview .topo-svg g')].map(g=>g.getAttribute('class')).slice(0,10);
 out.footer=r(q('#preview .topo-footer'));
 return {paths:out.paths,texts:out.texts,groups:out.labels}})()"""),indent=1))
ws.close(); proc.terminate()