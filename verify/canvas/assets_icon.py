import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9671; PROF="/tmp/kilo/prof-ai"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1500,1000","--remote-allow-origins=*","about:blank"],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:300])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.5)
print(ev("""(function(){
  var all=[].slice.call(document.querySelectorAll('#editorBar [data-panel=assets]'));
  return JSON.stringify(all.map(function(b){return {cls:b.className, title:b.title, svg:!!b.querySelector('svg'), text:b.textContent.trim()};}));})()"""))
print("grid icon vs assets icon distinct:", ev("""(function(){
  var g=document.getElementById('gridToggle').textContent.trim();
  var a=[].slice.call(document.querySelectorAll('#editorBar [data-panel=assets]')).filter(function(b){return b.querySelector('svg');})[0];
  return {grid:g, assetsSvg:!!(a&&a.querySelector('svg'))};})()"""))
ws.close(); proc.terminate()
