import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9480
widths=[1920,1600,1440,1280,1100,1024,900,820,768,761,760,700,600,480,390]
tmp=tempfile.mkdtemp(prefix="wd")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=1600,1000","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
cmd("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.0)
print("%5s %6s %6s %6s %6s %6s" % ("w","stage","rail","tabs","tgl","view"))
for w in widths:
    cmd("Emulation.setDeviceMetricsOverride",width=w,height=900,deviceScaleFactor=1,mobile=False)
    time.sleep(0.55)
    r = ev("""(function(){function g(s){var e=document.querySelector(s); if(!e) return -1;
      var b=e.getBoundingClientRect(); if(b.width===0&&b.height===0) return 0; return Math.round(b.width);}
      return {stage:g('#stage'), rail:g('#editorBar'), tabs:g('#mobileTabs'), tgl:g('#panelToggle'), view:g('#viewBar')};})()""")
    print("%5d %6s %6s %6s %6s %6s" % (w, r.get('stage'), r.get('rail'), r.get('tabs'), r.get('tgl'), r.get('view')))
c.close(); proc.terminate()
