import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9767
tmp=tempfile.mkdtemp(prefix="pg")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=1280,900","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
    r=cmd("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Network.enable")
bad=[]
def on_msg(m):
    if m.get("method") == "Network.responseReceived":
        u = m["params"]["response"]["url"]
        st = m["params"]["response"]["status"]
        if st >= 400 and "favicon" not in u:
            bad.append((st, u))

import threading
stop=False
def reader():
    while not stop:
        try:
            m=json.loads(c.recv())
        except Exception:
            return
        if m.get("id") is None:
            on_msg(m)
threading.Thread(target=reader, daemon=True).start()

for path in ["index.html", "blog.html", "read.html", "references.html", "draw.html", "topology.html"]:
    bad.clear()
    cmd("Page.navigate", url="http://127.0.0.1:8123/" + path + "?cb=" + str(time.time()))
    time.sleep(2.8)
    errs = ev("(function(){return (window.__errs||[]).length;})()")
    print(path, "errors:", errs, "bad requests:", bad[:3])
stop=True
c.close(); proc.terminate()