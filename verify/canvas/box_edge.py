import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9660; PROF="/tmp/kilo/prof-boxedge"
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
n=[0]; logs=[]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]: return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:300])
    return res.get("value")
def drag(x1,y1,x2,y2,steps=10):
    send("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1,buttons=1)
    for i in range(1,steps+1):
        send("Input.dispatchMouseEvent",type="mouseMoved",x=x1+(x2-x1)*i/steps,y=y1+(y2-y1)*i/steps,button="left",buttons=1)
        time.sleep(0.02)
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1,buttons=0)
    time.sleep(0.8)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.5)
def counts():
    return ev("({n:document.querySelectorAll('#stage .alur-node').length,e:document.querySelectorAll('#stage .alur-edge-head').length,tool:document.querySelector('[data-tool].is-on').getAttribute('data-tool')})")
print("start:", counts())
for label,(x1,y1,x2,y2) in {'TL':(30,128,90,172),'ML':(30,506,90,550),'C':(720,506,780,550),'BL':(30,884,90,928)}.items():
    print(label, "set box ->", ev("""(function(){var b=[].slice.call(document.querySelectorAll('[data-tool]')).filter(function(x){return x.getAttribute('data-tool')==='box';})[0]; b.click(); return document.querySelector('[data-tool].is-on').getAttribute('data-tool');})()"""))
    print("    hit@start:", ev("""(function(x,y){var e=document.elementFromPoint(x,y); if(!e) return 'none'; var c=[],p=e; while(p&&c.length<5){c.push(p.tagName.toLowerCase()+(p.id?'#'+p.id:'')+(p.getAttribute&&p.getAttribute('class')?'.'+String(p.getAttribute('class')).trim().split(/\\s+/)[0]:'')); p=p.parentElement;} return c.join(' < ');})(%d,%d)""" % (x1,y1)))
    b = counts(); drag(x1,y1,x2,y2); a = counts()
    print("   ", label, "before", b, "after", a, "| nodes now:", ev("Object.keys(JSON.parse(localStorage.getItem('ruang.scene.v1')).nodes||{}).length"))
ws.close(); proc.terminate()
