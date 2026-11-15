import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9814; PROF="/tmp/alur-probes/prof-code4"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",f"--user-data-dir={PROF}",
 "--no-first-run","--no-default-browser-check","--disable-gpu","--window-size=1600,1000",
 "--remote-allow-origins=*","--hide-scrollbars","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
import websocket
def http(p,m="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=m),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),"PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=60,suppress_origin=True)
n=[0]; exc=[]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]: return r.get("result",{})
        if r.get("method")=="Runtime.exceptionThrown":
            d=r["params"]["exceptionDetails"]; exc.append(d.get("text","")+" "+(d.get("exception") or {}).get("description","")[:180])
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.2)
ev("document.getElementById('exportBox').open = true")

def snap():
    return ev("""(()=>{const s=JSON.parse(document.getElementById('stage').getAttribute('data-spec')||'{}');
      const k=o=>Array.isArray(o)?o.length:Object.keys(o||{}).length;
      return {nodes:k(s.nodes), edges:k(s.edges), title:s.title,
              status:document.getElementById('codeStatus').textContent};})()""")
print("start:", json.dumps(snap()))

print("apply add node:", json.dumps(ev("""(async()=>{
  const b=document.getElementById('drawCode');
  const spec=JSON.parse(b.value);
  spec.nodes['probe-1']={id:'probe-1',x:200,y:300,w:140,h:60,shape:'box',label:'Probe',sub:'from code',color:'blue'};
  spec.title='Edited from code';
  b.value=JSON.stringify(spec,null,2);
  b.dispatchEvent(new Event('input',{bubbles:true}));
  await new Promise(r=>setTimeout(r,200));
  const typed=document.getElementById('codeStatus').textContent;
  document.getElementById('applyCode').click();
  await new Promise(r=>setTimeout(r,900));
  return {typed, status:document.getElementById('codeStatus').textContent};
})()""")))
print("after apply:", json.dumps(snap()))
print("canvas has probe:", ev("document.getElementById('stage').innerHTML.indexOf('Probe')>-1"))

print("array nodes accepted:", json.dumps(ev("""(async()=>{
  const b=document.getElementById('drawCode');
  const spec=JSON.parse(b.value);
  spec.nodes=Object.keys(spec.nodes).map(k=>spec.nodes[k]);
  spec.nodes.push({id:'probe-2',x:200,y:420,w:140,h:60,label:'Array form'});
  b.value=JSON.stringify(spec,null,2);
  b.dispatchEvent(new Event('input',{bubbles:true}));
  await new Promise(r=>setTimeout(r,200));
  const typed=document.getElementById('codeStatus').textContent;
  document.getElementById('applyCode').click();
  await new Promise(r=>setTimeout(r,800));
  return {typed, status:document.getElementById('codeStatus').textContent};
})()""")))
print("after array:", json.dumps(snap()))

print("fenced:", json.dumps(ev("""(async()=>{
  const b=document.getElementById('drawCode');
  const spec=JSON.parse(b.value);
  spec.title='Fenced apply';
  b.value='```draw\\n'+JSON.stringify(spec,null,2)+'\\n```';
  b.dispatchEvent(new Event('input',{bubbles:true}));
  await new Promise(r=>setTimeout(r,200));
  const typed=document.getElementById('codeStatus').textContent;
  document.getElementById('applyCode').click();
  await new Promise(r=>setTimeout(r,800));
  return {typed, status:document.getElementById('codeStatus').textContent};
})()""")))
print("after fenced:", json.dumps(snap()))

print("revert:", json.dumps(ev("""(async()=>{
  document.getElementById('revertCode').click();
  await new Promise(r=>setTimeout(r,250));
  return {status:document.getElementById('codeStatus').textContent,
    sync: document.getElementById('drawCode').value === JSON.stringify(JSON.parse(document.getElementById('stage').getAttribute('data-spec')),null,2)};
})()""")))

print("live after surprise:", json.dumps(ev("""(async()=>{
  const before=document.getElementById('drawCode').value;
  document.getElementById('surprise').click();
  await new Promise(r=>setTimeout(r,600));
  return {changed: before !== document.getElementById('drawCode').value};
})()""")))
print("exc:", exc if exc else "none")
proc.terminate()
