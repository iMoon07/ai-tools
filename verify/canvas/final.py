import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9340
URL=sys.argv[1]; W=int(sys.argv[2]); H=int(sys.argv[3])
tmp=tempfile.mkdtemp(prefix="fn")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
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
    if r.get("subtype")=="error": return {"__err":r.get("description")}
    return r.get("value")
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=W<700)
cmd("Page.navigate",url=URL); time.sleep(2.8)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")
time.sleep(0.4)
d=ev("({sw:document.documentElement.scrollWidth, iw:document.documentElement.clientWidth})")
e=ev("window.__errs||[]")
nav=ev("""(function(){var n=document.querySelector('.navigation'); if(!n) return 'none';
  var b=n.getBoundingClientRect(); return {y:Math.round(b.y),h:Math.round(b.height)};})()""")
print("%-28s %4s ovf=%-5s nav=%s err=%s" % (URL.split('/')[-1].ljust(28), ("%dx%d"%(W,H)), d['sw']>d['iw'], nav, e))
c.close(); proc.terminate()
