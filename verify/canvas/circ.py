import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9932
tmp=tempfile.mkdtemp(prefix="ci")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox",
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
    if r.get("subtype")=="error": print("JS ERROR:",r.get("description"))
    return r.get("value")
def spec():
    return ev("JSON.parse(document.getElementById('stage').getAttribute('data-spec')||'{}')")
def drag(x0,y0,x1,y1):
    cmd("Input.dispatchMouseEvent", type="mousePressed", x=x0, y=y0, button="left", clickCount=1)
    for k in range(1,6):
        cmd("Input.dispatchMouseEvent", type="mouseMoved", x=x0+(x1-x0)*k/5.0, y=y0+(y1-y0)*k/5.0, button="left", buttons=1)
        time.sleep(0.03)
    cmd("Input.dispatchMouseEvent", type="mouseReleased", x=x1, y=y1, button="left", clickCount=1)
    time.sleep(0.4)
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")
print("before:", len(spec().get('nodes') or {}))
ev("document.querySelectorAll('[data-tool=\"circle\"]').length")
print("circle buttons:", ev("document.querySelectorAll('[data-tool=\"circle\"]').length"))
ev("document.querySelectorAll('[data-tool=\"circle\"]')[0].click()")
print("is-on after click:", ev("document.querySelectorAll('[data-tool=\"circle\"].is-on').length"))
print("statusTool:", ev("(document.getElementById('statusTool')||{}).textContent"))
drag(200,600,340,720)
s=spec(); kinds={}
for k,n in (s.get('nodes') or {}).items(): kinds[n.get('shape')]=kinds.get(n.get('shape'),0)+1
print("after drag:", len(s.get('nodes') or {}), kinds)
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
