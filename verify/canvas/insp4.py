import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9823; PROF="/tmp/alur-probes/prof-insp4"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",f"--user-data-dir={PROF}",
 "--no-first-run","--no-default-browser-check","--disable-gpu","--window-size=1600,1000",
 "--remote-allow-origins=*","--hide-scrollbars","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
import websocket
def http(p,m="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=m),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),"PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=60,suppress_origin=True)
n=[0]; exc=[]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]: return r.get("result",{})
        if r.get("method")=="Runtime.exceptionThrown":
            d=r["params"]["exceptionDetails"]; exc.append(d.get("text","")+" "+(d.get("exception") or {}).get("description","")[:180])
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.0)

def state():
    return ev("""(()=>{const sp=document.getElementById('shapePanel');
     return {hidden:sp.hidden, title:document.getElementById('shapePanelTitle').textContent,
       labels:[].map.call(document.querySelectorAll('#shapePanelBody .shape-label'),x=>x.textContent),
       buttons:[].map.call(document.querySelectorAll('#shapePanelBody button'),x=>x.textContent.trim()).filter(Boolean).slice(0,8),
       selects:document.querySelectorAll('#shapePanelBody select').length,
       ranges:document.querySelectorAll('#shapePanelBody input[type=range]').length};})()""")

for tool in ('text','draw','diamond','circle','table','box','arrow','line'):
    ev("document.querySelector('[data-tool=%s]').click()"%tool); time.sleep(0.6)
    print(tool, json.dumps(state()))

# select a node again, then an edge
ev("document.querySelector('[data-tool=select]').click()"); time.sleep(0.4)
print("select node:", json.dumps(ev("""(()=>{const nd=document.querySelector('#stage svg .alur-node');
 if(!nd) return 'none'; const r=nd.getBoundingClientRect();
 nd.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,clientX:r.x+r.width/2,clientY:r.y+r.height/2}));
 return 'ok';})()"""))[:60])
time.sleep(0.6); print("node panel:", json.dumps(state()))
print("edge hit:", json.dumps(ev("""(()=>{const p=document.querySelector('#stage svg .alur-edge, #stage svg path.alur-wire, #stage svg g[data-edge]');
 if(!p) return 'no edge el'; const r=p.getBoundingClientRect();
 p.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,clientX:r.x+r.width/2,clientY:r.y+r.height/2}));
 return 'ok';})()"""))[:60])
time.sleep(0.7); print("edge panel:", json.dumps(state()))
print("exc:", exc if exc else "none")
proc.terminate()
