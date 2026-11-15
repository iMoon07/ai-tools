import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9769
tmp=tempfile.mkdtemp(prefix="pg2")
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

# 1. every referenced asset resolves
assets = set()
import re
for f in ["draw.html", "read.html", "references.html"]:
    html = urllib.request.urlopen("http://127.0.0.1:8123/" + f).read().decode("utf8", "ignore")
    for m in re.findall(r'(?:src|href)="((?!https?:|mailto:|#|data:)[^"]+)"', html):
        assets.add(m.split("?")[0])
missing = []
for a in sorted(assets):
    try:
        code = urllib.request.urlopen("http://127.0.0.1:8123/" + a, timeout=5).getcode()
    except Exception as e:
        code = getattr(e, "code", 0)
    if code != 200:
        missing.append((code, a))
print("assets checked:", len(assets), "missing:", missing)

# 2. page errors
for path in ["index.html", "blog.html", "read.html", "references.html", "draw.html", "topology.html"]:
    cmd("Page.navigate", url="http://127.0.0.1:8123/" + path + "?cb=" + str(time.time()))
    time.sleep(2.6)
    ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
    time.sleep(0.6)
    n = ev("(function(){return (window.__errs||[]).slice(0,3);})()")
    title = ev("document.title")
    print(path, "| title:", (title or "")[:40], "| errors:", n)
c.close(); proc.terminate()