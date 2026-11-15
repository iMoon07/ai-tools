import json, subprocess, time, urllib.parse, urllib.request, shutil, os, re
PORT=9591; PROF="/tmp/alur-probes/prof-tbl5"
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

md = open('/home/moon/Projects/imoon07.github.io/docs/alur-guide.md').read()
i = md.index('### Tables')
blocks = re.findall(r'```draw\n(.*?)\n```', md[i:i+3000], re.S)

page = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="css/shell.css"><link rel="stylesheet" href="css/article.css">
<link rel="stylesheet" href="css/alur.css?v=5">
<style>body{background:#0d1117;color:#e6edf3}main{max-width:760px;margin:0 auto;padding:20px}</style>
</head><body><main class="prose">
%s
</main>
<script src="js/logo-manifest.js"></script><script src="js/alur/kit.js"></script>
<script src="js/alur/cables.js"></script><script src="js/alur/motions.js"></script>
<script src="js/alur/logos.js"></script><script src="js/alur/core.js"></script>
<script src="js/alur/modules/canvas.js"></script><script>Alur.init();</script>
</body></html>""" % ("\n".join('<div class="alur" data-module="canvas" data-spec="%s"></div>' % b.replace('"','&quot;') for b in blocks))
dst='/home/moon/Projects/imoon07.github.io/tmp-tbl5.html'
open(dst,'w').write(page)
try:
    send("Emulation.setDeviceMetricsOverride",width=1400,height=900,deviceScaleFactor=1,mobile=False)
    send("Page.navigate",url="http://127.0.0.1:8123/tmp-tbl5.html"); time.sleep(3)
    print("tables:", ev("document.querySelectorAll('.alur-table').length"),
          "svg:", ev("document.querySelectorAll('.alur svg').length"))
    print("wrap bg:", ev("getComputedStyle(document.querySelector('.alur-table-wrap')).backgroundColor"))
    print("th text:", ev("[...document.querySelectorAll('.alur-table th')].map(t=>t.textContent)"))
    print("first row:", ev("[...document.querySelectorAll('.alur-table tbody tr:first-child td')].map(t=>t.textContent)"))
    ev("document.querySelector('[data-table-action=add-row]').click()"); time.sleep(0.5)
    print("after +Row rows:", ev("document.querySelectorAll('.alur-table tbody tr')[0].closest('table').querySelectorAll('tbody tr').length"))
finally:
    os.remove(dst)
ws.close(); proc.terminate()
