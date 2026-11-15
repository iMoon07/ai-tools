import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9675; PROF="/tmp/alur-probes/prof-toposz"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1500,1000","--remote-allow-origins=*","about:blank"],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def http(p,method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=method),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),method="PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=120,suppress_origin=True)
n=[0]; errs=[]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]:
            if r.get("method")=="Runtime.exceptionThrown":
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text")); print("   [EXC]", d.get("text"), (d.get("exception") or {}).get("description","")[:200])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:300])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")
for w,h,mob in ((1500,1000,False),(1180,820,False),(1024,768,True),(768,1024,True),(390,844,True),(360,740,True)):
    send("Emulation.setDeviceMetricsOverride",width=w,height=h,deviceScaleFactor=1,mobile=mob)
    send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3.5)
    r = ev("""(function(){
      var de=document.documentElement;
      var st=document.getElementById('stage').getBoundingClientRect();
      var dk=document.getElementById('dock'); var dr=dk.getBoundingClientRect();
      var hd=document.querySelector('.topbar');
      return {vw:de.clientWidth, sw:de.scrollWidth, overflowX:de.scrollWidth>de.clientWidth+1,
              head:[Math.round(hd.getBoundingClientRect().width), hd.scrollWidth],
              stage:[Math.round(st.width),Math.round(st.height)],
              dock:[Math.round(dr.width),Math.round(dr.height)],
              toggle:getComputedStyle(document.getElementById('dockToggle')).display,
              nodes:document.querySelectorAll('#preview .topo-node').length};})()""")
    print("%dx%d" % (w,h), r)
print("exceptions:", len(errs))
ws.close(); proc.terminate()
