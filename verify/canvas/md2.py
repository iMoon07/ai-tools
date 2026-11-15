import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9554
tmp=tempfile.mkdtemp(prefix="md2")
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
cmd("Page.navigate",url="http://127.0.0.1:8123/read.html"); time.sleep(3.0)
print(ev("""(async function(){
  var urls=['/Experiments/foundations/server-architecture/server-single-tier-stack-en.md',
            'https://raw.githubusercontent.com/iMoon07/Penjelajah-CyberSecurity/main/Experiments/foundations/server-architecture/server-single-tier-stack-en.md'];
  var out={};
  for (var i=0;i<urls.length;i++){
    try{
      var r=await fetch(urls[i]);
      var t=await r.text();
      var html=window.marked.parse(t);
      var fences=(t.match(/^```([a-zA-Z-]*)/gm)||[]);
      var counts={}; fences.forEach(function(f){counts[f]=(counts[f]||0)+1;});
      out[urls[i].slice(0,40)]={status:r.status,len:t.length,counts:counts,
        drawIdx:t.indexOf('```draw'), ctx:t.slice(Math.max(0,t.indexOf('```draw')-80), t.indexOf('```draw')+60)};
    }catch(e){ out[urls[i].slice(0,40)]='ERR '+e.message; }
  }
  return out;
})()"""))
c.close(); proc.terminate()
