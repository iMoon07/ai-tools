import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9811; PROF="/tmp/alur-probes/prof-code2"
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

# 1. live sync: a real user action must rewrite the block
before = ev("document.getElementById('drawCode').value")
ev("document.getElementById('surprise').click()"); time.sleep(0.6)
after = ev("document.getElementById('drawCode').value")
print("live sync:", json.dumps({"changed": before != after, "sameLen": len(before)==len(after)}))

# 2. edit code -> apply
print("apply:", json.dumps(ev("""(async()=>{
  const b=document.getElementById('drawCode');
  const spec=JSON.parse(b.value);
  spec.nodes = spec.nodes || [];
  spec.nodes.push({id:'probe-1', label:'Probe', x:200, y:200, w:140, h:60, kind:'process'});
  spec.title = 'Edited from code';
  b.value=JSON.stringify(spec,null,2);
  b.dispatchEvent(new Event('input',{bubbles:true}));
  await new Promise(r=>setTimeout(r,200));
  const st=document.getElementById('codeStatus').textContent;
  document.getElementById('applyCode').click();
  await new Promise(r=>setTimeout(r,700));
  return {status:st, after:document.getElementById('codeStatus').textContent,
    nodesOnCanvas:(window.state&&state.spec.nodes||[]).length,
    svgNodes:document.querySelectorAll('#stage svg .alur-node').length,
    hasProbe:JSON.stringify(state.spec).indexOf('probe-1')>-1};
})()""")))

# 3. invalid json
print("invalid:", json.dumps(ev("""(async()=>{
  const b=document.getElementById('drawCode');
  const keep=b.value;
  b.value='{ "nodes": [ }';
  b.dispatchEvent(new Event('input',{bubbles:true}));
  await new Promise(r=>setTimeout(r,150));
  const typed=document.getElementById('codeStatus').textContent;
  const badCls=b.className;
  document.getElementById('applyCode').click();
  await new Promise(r=>setTimeout(r,400));
  const applied=document.getElementById('codeStatus').textContent;
  const stillThere=(window.state&&state.spec.nodes||[]).length;
  b.value=keep; b.dispatchEvent(new Event('input',{bubbles:true}));
  return {typed, badCls, applied, nodesStill:stillThere};
})()""")))

# 4. fenced block
print("fenced:", json.dumps(ev("""(async()=>{
  const b=document.getElementById('drawCode');
  const spec=JSON.parse(b.value);
  spec.title='Fenced apply';
  b.value='```draw\\n'+JSON.stringify(spec,null,2)+'\\n```';
  b.dispatchEvent(new Event('input',{bubbles:true}));
  await new Promise(r=>setTimeout(r,150));
  document.getElementById('applyCode').click();
  await new Promise(r=>setTimeout(r,600));
  return {status:document.getElementById('codeStatus').textContent, title:state.spec.title};
})()""")))

# 5. revert
print("revert:", json.dumps(ev("""(async()=>{
  document.getElementById('revertCode').click();
  await new Promise(r=>setTimeout(r,200));
  return {status:document.getElementById('codeStatus').textContent,
    matches: document.getElementById('drawCode').value === JSON.stringify(state.spec,null,2)};
})()""")))
print("exc:", exc if exc else "none")
proc.terminate()
