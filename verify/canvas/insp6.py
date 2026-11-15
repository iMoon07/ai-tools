import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9825; PROF="/tmp/alur-probes/prof-insp6"
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
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.8)
print(json.dumps(ev("""(()=>{const vb=document.getElementById('viewBar');
 const b=document.getElementById('inspectorToggle'); const rb=b.getBoundingClientRect(), rv=vb.getBoundingClientRect();
 const cs=getComputedStyle(vb);
 return {vbRect:[Math.round(rv.x),Math.round(rv.y),Math.round(rv.width),Math.round(rv.height)],
   btn:[Math.round(rb.x),Math.round(rb.y),Math.round(rb.width),Math.round(rb.height)],
   overflow:cs.overflow, ovX:cs.overflowX, sw:vb.scrollWidth, cw:vb.clientWidth,
   inside: rb.x>=rv.x && rb.right<=rv.right+1 && rb.y>=rv.y && rb.bottom<=rv.bottom+1};})()""")))
proc.terminate()
