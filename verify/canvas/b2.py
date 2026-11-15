import json, subprocess, time, urllib.parse, urllib.request, shutil, re, pathlib
PORT=9641; PROF="/tmp/alur-probes/prof-b2"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1600,1000","--remote-allow-origins=*","about:blank"],
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
        if r.get("id")==n[0]: return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)

MD = pathlib.Path('/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture/server-single-tier-stack-en.md').read_text()
SPECS = [json.loads(b) for b in re.findall(r'```topology[ \t]*\n([\s\S]*?)\n```', MD)]
B2 = SPECS[2]

send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3.4)

def state(tag):
    print(tag, json.dumps(ev("""(()=>{const p=document.querySelector('#preview');const c=p.querySelector('.topo-canvas');
      return {prev:[p.clientWidth, p.getBoundingClientRect().width], cv:c?[c.offsetWidth, c.getAttribute('style'), c.querySelector('svg').getAttribute('width')]:null,
              vert:p.classList.contains('topo--vertical'), dock:document.getElementById('dock').className};})()""")))

state("before paste:")
ev("(()=>{const t=document.getElementById('specBox');t.value=%s;t.dispatchEvent(new Event('input',{bubbles:true}));return 1})()"
   % json.dumps("```topology\n"+json.dumps(B2)+"\n```"))
time.sleep(2.0)
state("after paste :")
ev("window.Topology.relayout(document.querySelector('#preview'))")
time.sleep(1.2)
state("after relayout:")
# now force a re-render from scratch
ev("window.Topology.render(document.querySelector('#preview'), %s)" % json.dumps(B2))
time.sleep(1.6)
state("after re-render:")
ws.close(); proc.terminate()