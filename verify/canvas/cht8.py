import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9539
tmp=tempfile.mkdtemp(prefix="cht8")
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
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.2)
def panel():
    return ev("""(function(){var p=document.getElementById('shapePanel');
      var b=p.getBoundingClientRect();
      return {hidden:p.hidden, disp:getComputedStyle(p).display, x:Math.round(b.x),y:Math.round(b.y),
        w:Math.round(b.width),h:Math.round(b.height), mode:(document.getElementById('editorMode')||{}).textContent,
        body:p.querySelector('#shapePanelBody')?p.querySelector('#shapePanelBody').children.length:-1};})()""")
print("load  :", panel())
ev("document.querySelector('[data-scene-module=\"chart\"]').click()"); time.sleep(1.0)
print("chart :", panel())
print("logoPE:", ev("(function(){var e=document.querySelector('.alur-logo-img');return e?getComputedStyle(e).pointerEvents:'none-found';})()"))
c.close(); proc.terminate()
