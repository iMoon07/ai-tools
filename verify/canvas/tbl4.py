import json, subprocess, time, urllib.parse, urllib.request, shutil, os
PORT=9589; PROF="/tmp/alur-probes/prof-tbl4"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1400,900","--remote-allow-origins=*","about:blank"],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
import websocket
def http(p,method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=method),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),method="PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=90,suppress_origin=True)
n=[0]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]:
            if r.get("method")=="Runtime.exceptionThrown":
                d=r["params"]["exceptionDetails"]; print("[EXC]",d.get("text"),(d.get("exception") or {}).get("description","")[:140])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")

# render the guide's tables-only example through the real markdown pipeline
md = open('/home/moon/Projects/imoon07.github.io/docs/alur-guide.md').read()
i = md.index('### Tables')
seg = md[i:i+3000]
import re
blocks = re.findall(r'```draw\n(.*?)\n```', seg, re.S)
print("table examples found:", len(blocks))
for b in blocks[:2]:
    spec = json.loads(b)
    print("  spec module:", spec.get('module'), "nodes:", list(spec.get('nodes',{})),
          "shapes:", [v.get('shape') for v in spec.get('nodes',{}).values()])
ws.close(); proc.terminate()
