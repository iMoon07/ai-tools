import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9672; PROF="/tmp/alur-probes/prof-topom"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=390,844","--remote-allow-origins=*","about:blank"],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def http(p,method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=method),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),method="PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=120,suppress_origin=True)
n=[0]; errs=[]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]:
            if r.get("method")=="Runtime.exceptionThrown":
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text")); print("   [EXC]", d.get("text"), (d.get("exception") or {}).get("description","")[:200])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:300])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=390,height=844,deviceScaleFactor=2,mobile=True)
send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(4.5)
print("doc size:", ev("({sw:document.documentElement.scrollWidth, cw:document.documentElement.clientWidth, sh:document.documentElement.scrollHeight})"))
print("overflowX:", ev("document.documentElement.scrollWidth > document.documentElement.clientWidth + 1"))
print("header:", ev("(()=>{const h=document.querySelector('.topbar');const r=h.getBoundingClientRect();return {box:[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)],scrollW:h.scrollWidth,clientW:h.clientWidth};})()"))
print("stage:", ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return [Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)];})()"))
print("dock:", ev("(()=>{const d=document.getElementById('dock');const r=d.getBoundingClientRect();const c=getComputedStyle(d);return {box:[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)],transform:c.transform,vis:c.visibility};})()"))
print("dockToggle:", ev("(()=>{const b=document.getElementById('dockToggle');const r=b.getBoundingClientRect();const c=getComputedStyle(b);return {display:c.display,box:[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)]};})()"))
print("nodes:", ev("document.querySelectorAll('#preview .topo-node').length"), "| empty:", ev("document.getElementById('board').classList.contains('is-empty')"))
print("preview scroll:", ev("(()=>{const p=document.getElementById('preview');return {sw:p.scrollWidth,cw:p.clientWidth};})()"))
print("small tap targets:", ev("""(function(){
  var bad=[];
  document.querySelectorAll('button, a, input, select').forEach(function(el){
    var r=el.getBoundingClientRect(); var c=getComputedStyle(el);
    if(c.display==='none'||c.visibility==='hidden'||!r.width) return;
    if(r.height<28||r.width<28) bad.push((el.id||el.className||el.tagName)+' '+Math.round(r.width)+'x'+Math.round(r.height));
  });
  return bad.slice(0,12);})()"""))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
