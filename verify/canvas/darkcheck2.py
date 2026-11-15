import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9755
tmp=tempfile.mkdtemp(prefix="tpk")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=390,844","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
for _ in range(80):
    try:
        urllib.request.urlopen("http://127.0.0.1:%d/json/version"%PORT,timeout=1).read(); break
    except Exception: time.sleep(0.25)
tabs=json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json"%PORT).read())
page=[t for t in tabs if t["type"]=="page"][0]
c=websocket.create_connection(page["webSocketDebuggerUrl"],timeout=30); i=[0]
def cmd(m,**p):
    i[0]+=1; c.send(json.dumps({"id":i[0],"method":m,"params":p}))
    while True:
        r=json.loads(c.recv())
        if r.get("id")==i[0]: return r.get("result",{})
def ev(e):
    r=cmd("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=390,height=844,deviceScaleFactor=2,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html?cb="+str(time.time())); time.sleep(3.5)
ev("Array.prototype.forEach.call(document.querySelectorAll('.dock'),function(d){d.hidden=false; d.classList.add('is-open');})")
time.sleep(0.6)
print('body:', ev("document.body.className"))
print('tab bar:', ev("(function(){var e=document.querySelector('.mobile-tabs-bar'); return e?getComputedStyle(e).backgroundColor:null;})()"))
print('field:', ev("(function(){var e=document.querySelector('.dock input, .dock select'); return e?getComputedStyle(e).backgroundColor:null;})()"))
print('head:', ev("(function(){var e=document.querySelector('.shape-head'); return e?getComputedStyle(e).backgroundColor:null;})()"))
print('label color:', ev("(function(){var e=document.querySelector('.alur-canvas-node .alur-node-label'); return e?getComputedStyle(e).fill:null;})()"))
c.close(); proc.terminate()
