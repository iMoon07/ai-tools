import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9891
tmp=tempfile.mkdtemp(prefix="dr")
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
def key(k, code=None, vk=None):
    code = code or k
    cmd("Input.dispatchKeyEvent", type="keyDown", key=k, code=code,
        windowsVirtualKeyCode=vk or (46 if k=='Delete' else 0), nativeVirtualKeyCode=vk or (46 if k=='Delete' else 0))
    cmd("Input.dispatchKeyEvent", type="keyUp", key=k, code=code,
        windowsVirtualKeyCode=vk or (46 if k=='Delete' else 0), nativeVirtualKeyCode=vk or (46 if k=='Delete' else 0))
def click(x,y):
    cmd("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", clickCount=1)
    cmd("Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y, button="left", clickCount=1)

cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")

def count():
    return ev("({nodes:document.querySelectorAll('#stage .alur-canvas-node').length, sel:document.querySelectorAll('#stage .alur-canvas-node.is-selected').length, active:(document.activeElement||{}).tagName+'.'+((document.activeElement||{}).id||'')})")

print("start:", count())
r = ev("""(function(){var n=document.querySelector('#stage .alur-canvas-node');var b=n.getBoundingClientRect();return {x:b.left+b.width/2,y:b.top+b.height/2};})()""")
print("node center:", r)
click(r["x"], r["y"]); time.sleep(0.35)
print("after real click:", count())
key('Delete'); time.sleep(0.45)
print("after Delete x1:", count())
key('Delete'); time.sleep(0.45)
print("after Delete x2:", count())
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
