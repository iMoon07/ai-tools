import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9830; PROF="/tmp/alur-probes/prof-scene"
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
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.0)

print("scene dock present:", ev("!!document.getElementById('panelScene')"))
print("sections:", json.dumps(ev("""(()=>{
  const sp=document.getElementById('panelScene');
  return {connected: sp.isConnected,
    steps:[].map.call(sp.querySelectorAll('.scene-step'),s=>({
      head:s.querySelector('.scene-step-head b')?s.querySelector('.scene-step-head b').textContent:null,
      hidden:!!s.hidden})),
    hasLibrary: !!document.getElementById('templateLibrary'),
    hasSurprise: !!document.getElementById('surprise'),
    presetOpts: document.getElementById('preset').options.length};})()""")))

# open the scene dock
ev("document.querySelector('[data-panel=scene]') ? document.querySelector('[data-panel=scene]').click() : null")
time.sleep(0.6)
print("dock open:", json.dumps(ev("""(()=>{const d=document.getElementById('panelScene');
 const r=d.getBoundingClientRect();
 return {open:d.classList.contains('is-open'), w:Math.round(r.width), h:Math.round(r.height),
   stageLeft:getComputedStyle(document.getElementById('stage')).left};})()""")))

# add a block
before = ev("JSON.parse(document.getElementById('stage').getAttribute('data-spec')).nodes")
ev("document.querySelector('[data-scene-module=chart]').click()"); time.sleep(0.9)
print("add block:", json.dumps(ev("""(()=>{const s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));
 return {module:s.module, title:s.title};})()""")))
print("exc:", exc if exc else "none")
proc.terminate()
