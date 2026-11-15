import json, subprocess, time, urllib.parse, urllib.request, shutil, pathlib, re
PORT = 9683; PROF = "/tmp/alur-probes/prof-totoread"
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
ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=90, suppress_origin=True)
n = [0]; exc = []; files = {}

def send(m, **p):
    n[0] += 1; ws.send(json.dumps({"id": n[0], "method": m, "params": p}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == n[0]:
            return r.get("result", {})
        if r.get("method") == "Runtime.exceptionThrown":
            d = r["params"]["exceptionDetails"]
            exc.append(d.get("text", "") + " " + (d.get("exception") or {}).get("description", "")[:200])
        if r.get("method") == "Fetch.requestPaused":
            req = r["params"]["request"]
            body = files.get(req["url"])
            if body is not None:
                send("Fetch.fulfillRequest", requestId=r["params"]["requestId"],
                     responseCode=200,
                     responseHeaders=[{"name": "Content-Type", "value": "text/plain; charset=utf-8"},
                                      {"name": "Access-Control-Allow-Origin", "value": "*"}],
                     body=body)
            else:
                send("Fetch.continueRequest", requestId=r["params"]["requestId"])

def ev(e):
    r = send("Runtime.evaluate", expression=e, returnByValue=True, awaitPromise=True).get("result", {})
    return r.get("value") if r.get("subtype") != "error" else {"__err": r.get("description")}

send("Runtime.enable"); send("Page.enable"); send("Fetch.enable", patterns=[{"urlPattern": "*raw.githubusercontent.com*"}])

LOCAL = pathlib.Path('/home/moon/Projects/Penjelajah-CyberSecurity')
POSTS = [
    ('server-single-tier-stack', 'Experiments/foundations/server-architecture/server-single-tier-stack-en.md'),
    ('template-for-you', 'blog-post-template/template-for-you-en.md'),
]
for pid, rel in POSTS:
    files["https://raw.githubusercontent.com/iMoon07/Penjelajah-CyberSecurity/main/" + rel] = LOCAL.joinpath(rel).read_text()

send("Emulation.setDeviceMetricsOverride", width=1600, height=1000, deviceScaleFactor=1, mobile=False)

for pid, _ in POSTS:
    exc.clear()
    send("Page.navigate", url=f"http://127.0.0.1:8123/read.html?post={pid}&lang=en")
    time.sleep(5.0)
    out = ev("""(()=>{
     const blocks=[...document.querySelectorAll('.topology, .tp')];
     const tps=[...document.querySelectorAll('.tp')];
     const nodes=document.querySelectorAll('.tp-node').length;
     const cols=document.querySelectorAll('.tp-col').length;
     const fails=blocks.filter(b=>/Diagram (gagal|tidak)/.test(b.textContent)).length;
     const notRendered=blocks.filter(b=>!b.querySelector('.tp-board')).length;
     const empty=blocks.filter(b=>b.textContent.trim()==='').length;
     const overflow=[...document.querySelectorAll('.tp')].filter(p=>p.scrollWidth>p.clientWidth+1).length;
     return {blocks:blocks.length, tps:tps.length, nodes, cols, fails, notRendered, empty, overflow,
       titles:[...document.querySelectorAll('.tp-title')].map(e=>e.textContent).slice(0,6)};
    })()""")
    print(pid.ljust(24), json.dumps(out))
    print('   exceptions:', exc if exc else 'none')

proc.terminate()