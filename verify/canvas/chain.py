import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9980
tmp=tempfile.mkdtemp(prefix="ch")
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
def edges():
    return ev("""(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec')||'{}');
      return (s.edges||[]).map(function(e){return e.points;});})()""")
def click(x,y):
    cmd("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", clickCount=1)
    cmd("Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y, button="left", clickCount=1)
    time.sleep(0.3)
def move(x,y):
    cmd("Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y, button="none")
    time.sleep(0.15)
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")
print("edges start:", edges())
ev("document.querySelector('[data-tool=\"line\"]').click()")
print("tool:", ev("(document.getElementById('statusTool')||{}).textContent"))
click(700,600); move(760,640); click(820,600); move(880,660); click(900,700)
print("after 3 clicks (no close):", edges())
ev("document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))")
time.sleep(0.5)
print("after Esc:", edges())
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
