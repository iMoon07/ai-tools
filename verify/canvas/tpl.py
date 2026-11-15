import json, sys, time, urllib.request, subprocess, tempfile
import websocket
PORT=int(sys.argv[1]); W=int(sys.argv[2]); H=int(sys.argv[3])
tmp=tempfile.mkdtemp(prefix="tp")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=%d,%d"%(W,H),"about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=W<600)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")
print("== %dx%d ==" % (W,H))
print("templates:", ev("document.querySelectorAll('#templateList .block-item').length"))
print("sections:", ev("""(function(){var o=[];document.querySelectorAll('#panelScene .scene-step-head b').forEach(function(b){o.push(b.textContent)});return o;})()"""))
# klik template chart terakhir
n = ev("document.querySelectorAll('#templateList .block-item').length")
ev("document.querySelector('#templateList [data-template-module=\"chart\"]').click()"); time.sleep(1.0)
s = spec(); sel = s.get('selected'); nd = (s.get('nodes') or {}).get(sel, {})
print("clicked template #%d -> module=%s chartType=%s dataSource=%s labels=%s data=%s" % (
    n, nd.get('module'), nd.get('chartType'), nd.get('dataSource'),
    (nd.get('moduleSpec') or {}).get('labels'), (nd.get('moduleSpec') or {}).get('data')))
print("quick hidden:", ev("(function(){var e=document.getElementById('chartQuickAdd');return e?!e.hidden:null;})()"))
print("doc:", ev("({sw:document.documentElement.scrollWidth, iw:innerWidth})"))
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
