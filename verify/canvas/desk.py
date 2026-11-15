import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9834; PROF="/tmp/alur-probes/prof-desk"
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

print("docks:", json.dumps(ev("""(()=>{const ids=['panelScene','panelAssets','panelLayers','panelProperties'];
 return ids.map(id=>{const d=document.getElementById(id); return [id, !!d, d?d.classList.contains('is-open'):null];});})()""")))

# open Scene
ev("document.querySelector('[data-panel=scene]').click()"); time.sleep(0.8)
print("scene:", json.dumps(ev("""(()=>{const d=document.getElementById('panelScene'); const r=d.getBoundingClientRect();
 const b=document.getElementById('preset'); const rb=b.getBoundingClientRect();
 return {open:d.classList.contains('is-open'), w:Math.round(r.width), h:Math.round(r.height),
   top:Math.round(r.top), preset:[Math.round(rb.width),Math.round(rb.height)],
   steps:[].map.call(d.querySelectorAll('.scene-step'),s=>({
     t:s.querySelector('.scene-step-head b').textContent, hidden:!!s.hidden}))};})()""")))

# template add vs replace
before = ev("JSON.parse(document.getElementById('stage').getAttribute('data-spec')).nodes")
ev("document.getElementById('addTemplate').click()"); time.sleep(1.0)
after = ev("JSON.parse(document.getElementById('stage').getAttribute('data-spec')).nodes")
print("add template: nodes %d -> %d" % (len(before or {}), len(after or {})))
ev("document.getElementById('loadTemplate').click()"); time.sleep(1.2)
after2 = ev("JSON.parse(document.getElementById('stage').getAttribute('data-spec')).nodes")
print("replace template: nodes -> %d" % (len(after2 or {}),))

# assets
ev("document.querySelector('[data-panel=assets]').click()"); time.sleep(0.9)
print("assets:", json.dumps(ev("""(()=>{const d=document.getElementById('panelAssets'); const r=d.getBoundingClientRect();
 return {open:d.classList.contains('is-open'), w:Math.round(r.width), h:Math.round(r.height),
   sections:[].map.call(d.querySelectorAll('.asset-section-head b'),x=>x.textContent),
   tiles:document.querySelectorAll('#logoGrid .logo-tile').length,
   sceneInside: !!d.querySelector('#sceneSection')};})()""")))

# chart section only for chart module
ev("document.querySelector('[data-scene-module=chart]').click()"); time.sleep(1.0)
ev("document.querySelector('[data-panel=scene]').click()"); time.sleep(0.6)
print("chart sec:", ev("[document.getElementById('chartSection').hidden, document.getElementById('linkSection').hidden]"))
print("exc:", exc if exc else "none")
proc.terminate()
