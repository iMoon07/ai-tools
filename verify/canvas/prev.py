import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9556
tmp=tempfile.mkdtemp(prefix="prev")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=1400,900","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
for _ in range(80):
    try:
        urllib.request.urlopen("http://127.0.0.1:%d/json/version"%PORT,timeout=1).read(); break
    except Exception: time.sleep(0.25)
tabs=json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json"%PORT).read())
page=[t for t in tabs if t["type"]=="page"][0]
c=websocket.create_connection(page["webSocketDebuggerUrl"],timeout=30)
i=[0]
def cmd(m,**p):
    i[0]+=1; c.send(json.dumps({"id":i[0],"method":m,"params":p}))
    while True:
        r=json.loads(c.recv())
        if r.get("id")==i[0]: return r.get("result",{})
def ev(e):
    r=cmd("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)["result"]
    if r.get("subtype")=="error": return {"__err":r.get("description")}
    return r.get("value")
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1400,height=900,deviceScaleFactor=1,mobile=False)
url="http://127.0.0.1:8124/imoon07.github.io/read.html?url=/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture/server-single-tier-stack-en.md"
cmd("Page.navigate",url=url); time.sleep(5.0)
print(ev("""(function(){
 var d=document.querySelectorAll('.alur.draw');
 var t=document.querySelectorAll('.topology');
 return {title:(document.getElementById('article-title')||{}).textContent,
  draw:d.length, drawReady:document.querySelectorAll('.alur.draw[data-ready]').length,
  drawSvg:d.length?!!d[0].querySelector('svg'):null,
  drawTable:d.length?!!d[0].querySelector('table'):null,
  topo:t.length, pres:document.querySelectorAll('pre').length,
  errs:Array.prototype.map.call(document.querySelectorAll('.alur-error'),function(e){return e.textContent;}).slice(0,3),
  rawJson:/\"module\":\\s*\"canvas\"/.test(document.body.textContent)};})()"""))
c.close(); proc.terminate()
