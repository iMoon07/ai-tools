import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT = 9711; PROF = "/tmp/alur-probes/prof-totofinal"
shutil.rmtree(PROF, ignore_errors=True)
proc = subprocess.Popen(["chromium", "--headless=new", f"--remote-debugging-port={PORT}",
    f"--user-data-dir={PROF}", "--no-first-run", "--no-default-browser-check", "--disable-gpu",
    "--window-size=1600,1000", "--remote-allow-origins=*", "--hide-scrollbars", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
import websocket

def http(p, method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}", method=method), timeout=10).read())

for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)

t = http("/json/new?" + urllib.parse.quote("about:blank", safe=""), method="PUT")
ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
n = [0]; exc = []

def send(m, **p):
    n[0] += 1; ws.send(json.dumps({"id": n[0], "method": m, "params": p}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == n[0]: return r.get("result", {})
        if r.get("method") == "Runtime.exceptionThrown":
            d = r["params"]["exceptionDetails"]
            exc.append(d.get("text", "") + " " + (d.get("exception") or {}).get("description", "")[:200])

def ev(e):
    r = send("Runtime.evaluate", expression=e, returnByValue=True, awaitPromise=True).get("result", {})
    return r.get("value") if r.get("subtype") != "error" else {"__err": r.get("description")}

send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride", width=1600, height=1000, deviceScaleFactor=1, mobile=False)

PAGES = ['index.html', 'read.html', 'references.html', 'blog.html', 'about.html',
         'topology.html', 'draw.html']

for page in PAGES:
    exc.clear()
    send("Page.navigate", url="http://127.0.0.1:8123/" + page)
    time.sleep(2.6)
    out = ev("""(()=>{
      const tp=document.querySelectorAll('.tp');
      const bad=[...tp].filter(p=>/Diagram (gagal|tidak)/.test(p.textContent)).length;
      const unrendered=[...document.querySelectorAll('.topology')].filter(d=>!d.querySelector('.tp-board')).length;
      return {title:document.title.slice(0,34), tp:tp.length, bad, unrendered,
        overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+1};
    })()""")
    print(page.ljust(18), json.dumps(out), '| exc:', exc if exc else 'none')

proc.terminate()