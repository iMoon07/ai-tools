import json,time,urllib.request,subprocess,tempfile
import websocket
PORT=9801
tmp=tempfile.mkdtemp(prefix="h4")
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
    i[0]+=1;c.send(json.dumps({"id":i[0],"method":m,"params":p}))
    while True:
        r=json.loads(c.recv())
        if r.get("id")==i[0]: return r.get("result",{})
def ev(e):
    r=cmd("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
cmd("Page.enable");cmd("Runtime.enable")
for w in [1400,1180,1000,900,800]:
    cmd("Emulation.setDeviceMetricsOverride",width=w,height=820,deviceScaleFactor=1,mobile=False)
    cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html?cb="+str(time.time()))
    time.sleep(3.0)
    ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
    print(w, json.dumps(ev("""(function(){
      var bar=document.getElementById('editorBar');
      var t=bar.querySelector('.tool-text');
      var kids=[].slice.call(bar.querySelectorAll('.tool')).filter(function(k){return k.getBoundingClientRect().width>0;});
      var over=kids.filter(function(k){var b=k.getBoundingClientRect();return b.right>window.innerWidth+1;}).length;
      return {labelDisplay: t?getComputedStyle(t).display:'none',
              barW: Math.round(bar.getBoundingClientRect().width),
              scrollW: bar.scrollWidth, clientW: bar.clientWidth,
              buttons: kids.length, beyondViewport: over,
              first: kids.length?Math.round(kids[0].getBoundingClientRect().width):0};})()""")))
proc.terminate()
