import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9560
W=int(sys.argv[1]); H=int(sys.argv[2])
tmp=tempfile.mkdtemp(prefix="sz")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=%d,%d"%(W,H),"about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=(W<600))
cmd("Page.navigate",url="http://127.0.0.1:8124/imoon07.github.io/read.html?url=/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture/server-single-tier-stack-en.md")
time.sleep(5.0)
print(W, ev("""(function(){
 var a=document.querySelector('.alur.draw')||document.querySelector('.topology');
 var svg=a?a.querySelector('svg'):null;
 var host=a?a.querySelector('.alur-host'):null;
 var art=document.querySelector('.article-body, article, #content');
 var r=function(e){if(!e)return null;var b=e.getBoundingClientRect();return {x:Math.round(b.x),w:Math.round(b.width),h:Math.round(b.height)};};
 return {alur:r(a), host:r(host), svg:r(svg), vb:svg?svg.getAttribute('viewBox'):null,
   par:r(a?a.parentNode:null), docW:document.documentElement.clientWidth,
   overflowX:document.documentElement.scrollWidth>document.documentElement.clientWidth,
   scrollW:document.documentElement.scrollWidth};})()"""))
c.close(); proc.terminate()
