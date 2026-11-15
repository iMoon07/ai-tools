import json, subprocess, time, urllib.parse, urllib.request, shutil, pathlib, re
PORT=9636; PROF="/tmp/alur-probes/prof-parity6"
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

MD = pathlib.Path('/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture/server-single-tier-stack-en.md').read_text()
SPECS = [json.loads(b) for b in re.findall(r'```topology[ \t]*\n([\s\S]*?)\n```', MD)]

# article harness
pathlib.Path('/tmp/alur-probes/parity_art.html').write_text(
"<!doctype html><html><head><meta charset='utf-8'>"
"<link rel='stylesheet' href='http://127.0.0.1:8123/css/topology.css?v=6'>"
"<style>body{margin:0;background:#0d1117;color:#c9d1d9;font:13px/1.55 system-ui}"
"#wrap{width:670px;margin:0 auto;padding:24px}</style></head><body>"
"<div id='wrap'><div id='host'></div></div>"
"<script src='http://127.0.0.1:8123/js/topology-icons.js?v=4'></script>"
"<script src='http://127.0.0.1:8123/js/topology.js?v=4'></script></body></html>")

SHAPE = """(()=>{
 const p=document.querySelector('#preview')||document.querySelector('.topology');
 const cv=p.querySelector('.topo-canvas'); const cb=cv.getBoundingClientRect();
 const nodes=[...p.querySelectorAll('.topo-node')].map(nd=>{const b=nd.getBoundingClientRect();
   return [nd.dataset.node||'', +((b.left-cb.left)/cb.width).toFixed(3), +((b.top-cb.top)/cb.width).toFixed(3),
           +(b.width/cb.width).toFixed(3), +(b.height/cb.width).toFixed(3)];});
 const cols=[...p.querySelectorAll('.topo-col')].length;
 const st=p.querySelector('.topo-node'); const cs=st?getComputedStyle(st):null;
 const lab=p.querySelector('.topo-node-label'); const lcs=lab?getComputedStyle(lab):null;
 const edges=[...p.querySelectorAll('path.topo-edge--flow, path.topo-edge--back')].length;
 const root=p;
 const colsEl=p.querySelector('.topo-columns');
 const csg=colsEl?getComputedStyle(colsEl):null;
 return {cols, nodes, edges, canvas:[Math.round(cb.width),Math.round(cb.height)],
   rootW: root.clientWidth, zoom: cv.style.zoom, gtc: csg?csg.gridTemplateColumns:null,
   rootCS: (()=>{const c=getComputedStyle(root);return [c.padding, c.fontSize, c.width];})(),
   colsBox: (()=>{const e=p.querySelector('.topo-columns'); if(!e) return null; const b=e.getBoundingClientRect(); const c=getComputedStyle(e); return [Math.round(b.width), c.display, c.gap, c.flexWrap, c.gridTemplateColumns];})(),
   colBoxes: [...p.querySelectorAll('.topo-col')].map(e=>Math.round(e.getBoundingClientRect().width)),
   font: [document.fonts.check('13px Excalifont'), document.fonts.status],
   svgW: (()=>{const s=p.querySelector('svg'); return s?[Math.round(s.getBoundingClientRect().width), s.getAttribute('width'), s.getAttribute('viewBox')]:null;})(),
   cvW: (()=>{const c=p.querySelector('.topo-canvas'); return c?[c.offsetWidth, c.scrollWidth]:null;})(),
   style: cs? [cs.fontSize, cs.borderRadius, cs.border, cs.background.slice(0,28)]:null,
   label: lcs? [lcs.fontSize, lcs.color]:null,
   vert: p.classList.contains('topo--vertical')};
})()"""

def article(spec):
    ev("(()=>{const h=document.getElementById('host');h.innerHTML='';"
       "const d=document.createElement('div');d.className='topology';h.appendChild(d);"
       "window.Topology.render(d,%s);return 1})()" % json.dumps(spec))
    time.sleep(0.7)
    return ev(SHAPE)

def editor(spec):
    ev("(()=>{const t=document.getElementById('specBox');"
       "t.value=%s;t.dispatchEvent(new Event('input',{bubbles:true}));return 1})()"
       % json.dumps("```topology\n"+json.dumps(spec)+"\n```"))
    time.sleep(3.2)
    return ev(SHAPE)

send("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="file:///tmp/alur-probes/parity_art.html"); time.sleep(2.2)
A = [article(s) for s in SPECS]

send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3.2)
ev("localStorage.clear()")
send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3.2)
# widen the editor stage so the canvas is comparable
ev("document.getElementById('dockClose').click()")
E = []
for s in SPECS:
    E.append(editor(s))

for i,(a,e) in enumerate(zip(A,E)):
    if i!=2: continue
    same_cols = a['cols']==e['cols']
    same_n = a['nodes']==e['nodes']
    same_e = a['edges']==e['edges']
    same_v = a['vert']==e['vert']
    same_s = a['style']==e['style']
    same_l = a['label']==e['label']
    print(f"block {i}: cols {a['cols']}/{e['cols']} {'OK' if same_cols else 'DIFF'} | nodes {'OK' if same_n else 'DIFF'} | edges {a['edges']}/{e['edges']} {'OK' if same_e else 'DIFF'} | vert {a['vert']}/{e['vert']} | style {'OK' if same_s else 'DIFF'} | label {'OK' if same_l else 'DIFF'}")
    if not same_n:
        print("   ART:", json.dumps(a['nodes'])[:260])
        print("   EDT:", json.dumps(e['nodes'])[:260])
    if not same_s:
        print("   ART style:", a['style'], " EDT style:", e['style'])
        print("   ART rootW:",a['rootW'],"zoom:",a['zoom'],"gtc:",(a['gtc'] or '')[:60],"cs:",a['rootCS'])
        print("   EDT rootW:",e['rootW'],"zoom:",e['zoom'],"gtc:",(e['gtc'] or '')[:60],"cs:",e['rootCS'])
        print("   cols ART:", a['colsBox'], " EDT:", e['colsBox'])
        print("   colw ART:", a['colBoxes'], " EDT:", e['colBoxes'])
        print("   font ART:", a['font'], " EDT:", e['font'])
        print("   svg ART:", a['svgW'], " EDT:", e['svgW'])
        print("   cvW ART:", a['cvW'], " EDT:", e['cvW'])
    if not same_l:
        print("   ART label:", a['label'], " EDT label:", e['label'])
print("exceptions:", exc)
ws.close(); proc.terminate()