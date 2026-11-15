import json, time, urllib.request, subprocess, tempfile
import websocket

PORT = 9822
tmp = tempfile.mkdtemp(prefix="sfilr")
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

cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride", width=1400, height=900, deviceScaleFactor=1, mobile=False)
cmd("Page.navigate", url="http://127.0.0.1:8123/read.html?cb=" + str(time.time()))
time.sleep(4.0)
print('sticky count:', ev("document.querySelectorAll('.alur-sticky').length"))
print('computed    :', ev("(function(){var p=document.querySelector('.alur-sticky');"
      "if(!p)return 'none';var s=getComputedStyle(p);"
      "return 'fill='+s.fill+' stroke='+s.stroke+' inProse='+!!p.closest('.prose');})()"))
print('box computed:', ev("(function(){var p=document.querySelector('.alur-node-box');"
      "if(!p)return 'none';return getComputedStyle(p).fill;})()"))
print('label ink   :', ev("(function(){var t=document.querySelector('.alur-sticky-label');"
      "return t?getComputedStyle(t).fill:'none';})()"))
c.close(); proc.terminate()