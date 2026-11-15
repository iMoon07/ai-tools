import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9854; PROF="/tmp/alur-probes/prof-noframe"
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
            d=r["params"]["exceptionDetails"]; exc.append(d.get("text","")+" "+(d.get("exception") or {}).get("description","")[:200])
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
send("Runtime.enable"); send("Page.enable")

for w,h,mob,tag in ((1600,1000,False,"desktop"),(390,844,True,"mobile")):
    send("Emulation.setDeviceMetricsOverride",width=w,height=h,deviceScaleFactor=1,mobile=mob)
    exc.clear()
    send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.8)
    print(tag, json.dumps(ev("""(()=>{const svg=document.querySelector('#stage svg');
      const grid=svg.querySelector('.alur-canvas-grid');
      const vb=svg.viewBox.baseVal;
      return {pageLayer:!!svg.querySelector('.alur-layer-page'),
        pageRect:!!svg.querySelector('.alur-page-rect'),
        pageBtn:!!document.getElementById('pageToggle'),
        gridFillsViewport: grid ? (grid.getAttribute('width')==Math.round(vb.width) && grid.getAttribute('x')==Math.round(vb.x)) : null,
        ovfX:document.documentElement.scrollWidth>innerWidth,
        bodyBg:getComputedStyle(document.body).backgroundColor};})()""")))

# auto-pan masih jalan?
send("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.8)
print("auto-pan:", json.dumps(ev("""(async()=>{
  const stage=document.getElementById('stage'); const r=stage.getBoundingClientRect();
  const mk=(t,x,y)=>new PointerEvent(t,{bubbles:true,cancelable:true,pointerId:5,pointerType:'mouse',isPrimary:true,button:0,buttons:1,clientX:x,clientY:y});
  document.querySelector('[data-tool=arrow]').click();
  stage.dispatchEvent(mk('pointerdown', r.left+300, r.top+300));
  for (let i=0;i<14;i++) { window.dispatchEvent(mk('pointermove', r.right-25, r.top+320)); await new Promise(x=>setTimeout(x,45)); }
  const vb=document.querySelector('#stage svg').viewBox.baseVal;
  window.dispatchEvent(mk('pointerup', r.right-25, r.top+320));
  await new Promise(x=>setTimeout(x,300));
  return {panX:Math.round(vb.x), endX:(()=>{const s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));
    const e=(s.edges||[]).slice(-1)[0]||{}; return e.points?Math.round(e.points[e.points.length-1][0]):null;})()};})()""")))

# snap guide: geser node dekat node lain, cek .alur-guide muncul
print("guides:", json.dumps(ev("""(async()=>{
  document.querySelector('[data-tool=select]').click(); await new Promise(r=>setTimeout(r,300));
  const nd=document.querySelector('#stage svg .alur-canvas-node');
  const b=nd.getBoundingClientRect();
  const mk=(t,x,y)=>new PointerEvent(t,{bubbles:true,cancelable:true,pointerId:6,pointerType:'mouse',isPrimary:true,button:0,buttons:1,clientX:x,clientY:y});
  nd.dispatchEvent(mk('pointerdown', b.x+b.width/2, b.y+b.height/2));
  await new Promise(r=>setTimeout(r,60));
  for (let i=0;i<14;i++){ window.dispatchEvent(mk('pointermove', b.x+b.width/2+i*6, b.y+b.height/2+i*1)); await new Promise(r=>setTimeout(r,20)); }
  const guides=document.querySelectorAll('#stage svg .alur-guide').length;
  window.dispatchEvent(mk('pointerup', b.x+b.width/2+84, b.y+b.height/2+14));
  await new Promise(r=>setTimeout(r,200));
  return {guidesDuring:guides, guidesAfter:document.querySelectorAll('#stage svg .alur-guide').length};})()""")))
print("exc:", exc if exc else "none")
proc.terminate()
