import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9551
tmp=tempfile.mkdtemp(prefix="rd1")
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
cmd("Page.navigate",url="http://127.0.0.1:8123/read.html?doc=docs/references/drawtest.md"); time.sleep(4.0)
print(ev("""(function(){
 var host=document.querySelector('.alur.draw');
 var pre=document.querySelectorAll('pre').length;
 var body=document.querySelector('article')||document.body;
 return {host:!!host, ready:host?host.getAttribute('data-ready'):null,
   html:host?host.innerHTML.slice(0,160):null,
   preText:pre?[].map.call(document.querySelectorAll('pre'),function(p){return p.textContent.slice(0,40);}):[],
   hasJson:/module/.test(body.textContent), Alur:!!window.Alur, len:body.textContent.length,
   text:body.textContent.slice(0,400)};})()"""))
c.close(); proc.terminate()
