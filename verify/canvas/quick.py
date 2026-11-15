import json, sys, time, urllib.request, subprocess, tempfile
import websocket
PORT=int(sys.argv[1]); W=int(sys.argv[2]); H=int(sys.argv[3])
tmp=tempfile.mkdtemp(prefix="q")
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
print("== %dx%d ==" % (W,H), "errors:", ev("window.__errs||[]"))
print("quick list items:", ev("(function(){var h=document.getElementById('chartQuickList');return h?h.querySelectorAll('.block-item').length:'MISSING';})()"))
print("quick visible:", ev("(function(){var e=document.getElementById('chartQuickAdd');return e?!e.hidden:null;})()"))
n0=len(spec().get('nodes') or {})
ev("document.querySelector('#chartQuickList .block-item:nth-child(3)').click()"); time.sleep(0.9)
s=spec(); n1=len(s.get('nodes') or {})
print("nodes %d -> %d" % (n0,n1))
print("selected:", s.get('selected'), "type:", (s.get('nodes') or {}).get(s.get('selected'),{}).get('chartType'))
print("quick visible after:", ev("(function(){var e=document.getElementById('chartQuickAdd');return e?!e.hidden:null;})()"))
print("doc:", ev("({sw:document.documentElement.scrollWidth, iw:innerWidth})"))
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
