import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9815; PROF="/tmp/alur-probes/prof-code5"
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
PROBE = """(()=>{const b=document.getElementById('drawCode');
 const d=document.getElementById('exportBox');
 const head=document.querySelector('.code-head');
 const btns=[].map.call(document.querySelectorAll('.code-head .mini'),x=>{const r=x.getBoundingClientRect();return [Math.round(r.width),Math.round(r.height)];});
 const br=b.getBoundingClientRect(), dr=d.getBoundingClientRect();
 return {vw:innerWidth, boxW:Math.round(br.width), boxH:Math.round(br.height),
   headW:Math.round(head.getBoundingClientRect().width), btns:btns,
   detailsW:Math.round(dr.width), detailsH:Math.round(dr.height),
   ovfX: document.documentElement.scrollWidth>innerWidth,
   ovfBox: b.scrollWidth>b.clientWidth+1,
   dockScroll: (()=>{const s=document.querySelector('.dock-body'); return s? s.scrollHeight>s.clientHeight : null;})()};})()"""
for w,h,mob,tag in ((1600,1000,False,"desktop"),(1100,900,False,"laptop"),(390,844,True,"mobile")):
    send("Emulation.setDeviceMetricsOverride",width=w,height=h,deviceScaleFactor=1,mobile=mob)
    send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.6)
    ev("document.getElementById('exportBox').open = true"); time.sleep(0.4)
    print(tag, json.dumps(ev(PROBE)))

# Ctrl+Enter applies
send("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.6)
ev("document.getElementById('exportBox').open = true")
print("ctrl+enter:", json.dumps(ev("""(async()=>{
  const b=document.getElementById('drawCode');
  const spec=JSON.parse(b.value); spec.title='Ctrl Enter';
  b.value=JSON.stringify(spec,null,2);
  b.dispatchEvent(new Event('input',{bubbles:true}));
  b.focus();
  b.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',ctrlKey:true,bubbles:true,cancelable:true}));
  await new Promise(r=>setTimeout(r,700));
  return {title:JSON.parse(document.getElementById('stage').getAttribute('data-spec')).title,
          status:document.getElementById('codeStatus').textContent};
})()""")))
print("exc:", exc if exc else "none")
proc.terminate()
