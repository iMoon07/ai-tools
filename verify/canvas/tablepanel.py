import json, time, urllib.request, subprocess, tempfile
import websocket

PORT = 9825
tmp = tempfile.mkdtemp(prefix="tbl")
proc = subprocess.Popen(["chromium", "--headless=new", "--disable-gpu", "--no-sandbox",
    "--hide-scrollbars", "--remote-debugging-port=%d" % PORT, "--remote-allow-origins=*",
    "--user-data-dir=" + tmp, "--window-size=1400,900", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(80):
    try:
        urllib.request.urlopen("http://127.0.0.1:%d/json/version" % PORT, timeout=1).read(); break
    except Exception:
        time.sleep(0.25)
tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT).read())
page = [t for t in tabs if t["type"] == "page"][0]
c = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=30)
i = [0]
def cmd(m, **p):
    i[0] += 1; c.send(json.dumps({"id": i[0], "method": m, "params": p}))
    while True:
        r = json.loads(c.recv())
        if r.get("id") == i[0]: return r.get("result", {})
def ev(e):
    r = cmd("Runtime.evaluate", expression=e, returnByValue=True, awaitPromise=True).get("result", {})
    return r.get("value") if r.get("subtype") != "error" else {"__err": r.get("description")}

def key(k):
    ev("document.body.dispatchEvent(new KeyboardEvent('keydown',{key:%s,bubbles:true,cancelable:true}));" % json.dumps(k))
    time.sleep(0.35)

def click(x, y):
    for t in ("mousePressed", "mouseReleased"):
        cmd("Input.dispatchMouseEvent", type=t, x=x, y=y, button="left", clickCount=1)
        time.sleep(0.06)
    time.sleep(0.5)

cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride", width=1400, height=900, deviceScaleFactor=1, mobile=False)
cmd("Page.navigate", url="http://127.0.0.1:8123/draw.html?cb=" + str(time.time()))
time.sleep(3.6)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.3)

PANEL = ("(function(){var p=document.getElementById('shapePanel');"
         "var b=document.getElementById('shapePanelBody');"
         "var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));"
         "var shapes=Object.keys(s.nodes).map(function(k){return s.nodes[k].shape;});"
         "var t=(document.getElementById('shapePanelTitle')||{}).textContent||'';"
         "return 'hidden='+p.hidden+' | title='+t+' | bodyLen='+b.innerHTML.length"
         " + ' | shapes=['+shapes.join(',')+']';})()")

print('start            :', ev(PANEL))
key('9')
print('after key 9      :', ev(PANEL))
click(700, 450)
print('after place click:', ev(PANEL))
key('v')
click(700, 450)
print('after select tbl :', ev(PANEL))
key('r')
click(400, 250)
print('after box select :', ev(PANEL))
print('box sections     :', ev("(function(){var b=document.getElementById('shapePanelBody');"
      "return b?b.innerText.replace(/\\s+/g,' ').slice(0,120):'none';})()"))
key('Delete')
print('after delete tbl :', ev(PANEL))
print('errs:', ev("window.__errs"))
c.close(); proc.terminate()