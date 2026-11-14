import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9661; PROF="/tmp/kilo/prof-panel"
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
n=[0]
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
def drag(x1,y1,x2,y2,steps=8):
    send("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1,buttons=1)
    for i in range(1,steps+1):
        send("Input.dispatchMouseEvent",type="mouseMoved",x=x1+(x2-x1)*i/steps,y=y1+(y2-y1)*i/steps,button="left",buttons=1); time.sleep(0.02)
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1,buttons=0); time.sleep(0.8)
RECTS = """(function(){var g=function(sel){var e=document.querySelector(sel); if(!e) return null; var r=e.getBoundingClientRect(); var c=getComputedStyle(e);
 return [sel, Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height), c.pointerEvents, c.zIndex, c.display];};
 return JSON.stringify(['#shapePanel','#shapePanelBody','.panelAssets','#panelAssets','#minimap','#editorBar','#viewBar','#stage','#leftDock','#rightDock'].map(g).filter(Boolean));})()"""
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.5)
print("on load:", ev(RECTS))
ev("(function(){var b=[].slice.call(document.querySelectorAll('[data-tool]')).filter(function(x){return x.getAttribute('data-tool')==='box';})[0]; b.click(); return 1;})()"); time.sleep(0.4)
drag(700,500,760,540)
print("after drawing a box:", ev(RECTS))
print("selected:", ev("JSON.stringify(JSON.parse(localStorage.getItem('ruang.scene.v1')).selected||null)"))
print("hit at (200,500):", ev("(function(){var e=document.elementFromPoint(200,500); var c=[],p=e; while(p&&c.length<4){c.push(p.tagName.toLowerCase()+(p.id?'#'+p.id:'')); p=p.parentElement;} return c.join(' < ');})()"))
ws.close(); proc.terminate()
