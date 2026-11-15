import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9555
tmp=tempfile.mkdtemp(prefix="md3")
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
cmd("Page.navigate",url="http://127.0.0.1:8124/imoon07.github.io/read.html?url=/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture/server-single-tier-stack-en.md"); time.sleep(3.0)
print(ev("""(async function(){
  var t=document.body.textContent;
  var html=window.marked.parse(t);
  var d=document.createElement('div'); d.innerHTML=html;
  var drawDivs=d.querySelectorAll('.alur.draw').length;
  var pres=d.querySelectorAll('pre').length;
  var out={drawDivs:drawDivs, pres:pres, topologyDivs:d.querySelectorAll('.topology').length};
  document.getElementById('content').appendChild(d);
  window.Alur.init(d);
  out.afterMount={draw:document.querySelectorAll('.alur.draw[data-ready]').length,
                  topo:document.querySelectorAll('.topology').length,
                  err:Array.prototype.map.call(document.querySelectorAll('.alur-error'),function(e){return e.textContent;}).slice(0,3)};
  return out;
})()"""))
c.close(); proc.terminate()
