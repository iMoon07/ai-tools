import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9390
tmp=tempfile.mkdtemp(prefix="ky")
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
    if r.get("subtype")=="error": return {"__err":r.get("description")}
    return r.get("value")
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
print("active:", ev("document.activeElement.tagName+'#'+(document.activeElement.id||'')"))
print("canvas:", ev("document.body.classList.contains('canvas-mode')"))
def key(k, code, keyCode):
    cmd("Input.dispatchKeyEvent", type="keyDown", key=k, code=code, windowsVirtualKeyCode=keyCode, nativeVirtualKeyCode=keyCode)
    cmd("Input.dispatchKeyEvent", type="keyUp", key=k, code=code, windowsVirtualKeyCode=keyCode, nativeVirtualKeyCode=keyCode)
    time.sleep(0.35)
print("tool before:", ev("(document.getElementById('statusTool')||{}).textContent"))
key('r','KeyR',82)
print("tool after R:", ev("(document.getElementById('statusTool')||{}).textContent"))
print("selected tool btn:", ev("""(function(){var b=document.querySelector('[data-tool].is-on');return b?b.getAttribute('data-tool'):null;})()"""))
key('v','KeyV',86)
print("after V:", ev("""(function(){var b=document.querySelector('[data-tool].is-on');return b?b.getAttribute('data-tool'):null;})()"""))
key('?','Slash',191)
print("shortcut card hidden:", ev("(function(){var e=document.getElementById('shortcutCard');return e?e.hidden:'none';})()"))
c.close(); proc.terminate()
