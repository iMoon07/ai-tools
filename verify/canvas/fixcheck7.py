import json, time, urllib.request, subprocess, tempfile
import websocket

PORT = 9787
tmp = tempfile.mkdtemp(prefix="fx")
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
cmd("Page.navigate", url="http://127.0.0.1:8123/draw.html?cb=" + str(time.time()))
time.sleep(3.6)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.3)

# seed a link straight into the spec and re-render
print('seed:', ev("(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));"
                  "var k=Object.keys(s.nodes)[0];s.nodes[k].link='https://example.com';"
                  "document.getElementById('stage').setAttribute('data-spec',JSON.stringify(s));"
                  "if(window.Alur&&Alur.destroy&&document.getElementById('stage').__alur){Alur.destroy(document.getElementById('stage').__alur);}"
                  "Alur.mount(document.getElementById('stage'));return k;})()"))
time.sleep(0.8)
print('links in svg:', ev("document.querySelectorAll('.alur-node-link').length"))
print('first node html:', ev("(function(){var g=document.querySelector('.alur-canvas-node');"
                             "return g?g.outerHTML.slice(0,700):'none';})()"))
print('errs:', ev("window.__errs"))
c.close(); proc.terminate()