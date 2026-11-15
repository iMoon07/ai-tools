import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9500
tmp=tempfile.mkdtemp(prefix="gr")
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
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
def st():
    return ev("""(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec')||'{}');
      var g=document.querySelector('.alur-canvas-grid');
      return {grid:s.grid, nodes:Object.keys(s.nodes||{}).length, gridEl:!!g,
        gridOpacity:g?getComputedStyle(g).opacity:null, vb:(document.querySelector('#stage svg')||{}).getAttribute?document.querySelector('#stage svg').getAttribute('viewBox'):null};})()""")
print("before:", st())
ev("document.querySelector('[data-scene-module=\"chart\"]').click()")
time.sleep(0.9)
print("after Add block > Chart:", st())
ev("document.querySelector('#chartQuickList .block-item').click()")
time.sleep(0.9)
print("after quick list item:", st())
print("gridToggle pressed:", ev("(function(){var b=document.getElementById('gridToggle');return b?b.getAttribute('aria-pressed'):'none';})()"))
c.close(); proc.terminate()
