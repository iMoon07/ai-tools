import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9824; PROF="/tmp/alur-probes/prof-insp5"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",f"--user-data-dir={PROF}",
 "--no-first-run","--no-default-browser-check","--disable-gpu","--window-size=390,844",
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
for w,h,mob,tag in ((390,844,True,"mobile"),(1600,1000,False,"desktop")):
    send("Emulation.setDeviceMetricsOverride",width=w,height=h,deviceScaleFactor=1,mobile=mob)
    exc.clear()
    send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.8)
    print(tag, json.dumps(ev("""(()=>{const vb=document.getElementById('viewBar');
      const b=document.getElementById('inspectorToggle'); const r=b.getBoundingClientRect();
      return {ovfX:document.documentElement.scrollWidth>innerWidth,
        btn:[Math.round(r.width),Math.round(r.height)], btnVisible:r.width>0,
        vbRight:Math.round(vb.getBoundingClientRect().right), iw:innerWidth,
        vbScroll: vb.scrollWidth>vb.clientWidth};})()""")), "| exc:", (exc[0] if exc else "none"))

# mobile menu has a properties entry?
print("mobile menu props:", ev("!!document.querySelector('[data-mobile-panel=properties]')"))
proc.terminate()
