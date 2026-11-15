import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9650; PROF="/tmp/alur-probes/prof-inf2"
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
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
def spec_zoom():
    return ev("(()=>{try{return JSON.parse(localStorage.getItem('ruang.scene.v1')).zoom;}catch(e){return 'err';}})()")
def vb():
    return ev("(()=>{const v=document.querySelector('#stage svg').viewBox.baseVal; return [Math.round(v.x),Math.round(v.y),Math.round(v.width),Math.round(v.height)];})()")
def ctrlwheel(px,py,dy,times=1):
    for _ in range(times):
        send("Input.dispatchMouseEvent",type="mouseWheel",x=px,y=py,deltaX=0,deltaY=dy,modifiers=2); time.sleep(0.35)
def key(k, code, vk, mods=0):
    send("Input.dispatchKeyEvent",type="keyDown",code=code,key=k,windowsVirtualKeyCode=vk,nativeVirtualKeyCode=vk,modifiers=mods)
    send("Input.dispatchKeyEvent",type="keyUp",code=code,key=k,windowsVirtualKeyCode=vk,nativeVirtualKeyCode=vk,modifiers=mods)
    time.sleep(0.35)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)

print("== fresh blank canvas default view ==")
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
print("zoom:", spec_zoom(), "| vb:", vb(), "| grid:", ev("(()=>{const g=document.querySelector('.alur-canvas-grid');return g?[g.getAttribute('x'),g.getAttribute('y'),g.getAttribute('width'),g.getAttribute('height')].map(Math.round):null;})()"))

stg = ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()")
px, py = stg['x']+stg['w']*0.5, stg['y']+stg['h']*0.5

print("\n== zoom range ==")
seq=[]
ctrlwheel(px,py,200,times=14); seq.append(('out x14', round(spec_zoom(),4)))
ctrlwheel(px,py,-120,times=40); seq.append(('in x40', round(spec_zoom(),4)))
for a,b in seq: print(a, '->', b, '| vb w:', vb()[2])

print("\n== pan at extreme zooms ==")
for label, z in (('0.10',0.10), ('0.05',0.05), ('3.00',3.0)):
    ev("(()=>{const s=JSON.parse(localStorage.getItem('ruang.scene.v1'));s.zoom=%s;s.panX=0;s.panY=0;localStorage.setItem('ruang.scene.v1',JSON.stringify(s));})()" % z)
    send("Page.reload"); time.sleep(4)
    v0 = vb()
    key("ArrowRight","ArrowRight",39)
    v1 = vb()
    print(label, "vb:", v0, "-> after ArrowRight:", v1, "| moved:", v0!=v1, "| panX:", ev("JSON.parse(localStorage.getItem('ruang.scene.v1')).panX"))

print("\n== zoom in/out buttons keep the centre ==")
ev("(()=>{const s=JSON.parse(localStorage.getItem('ruang.scene.v1'));s.zoom=1;s.panX=200;s.panY=150;localStorage.setItem('ruang.scene.v1',JSON.stringify(s));})()")
send("Page.reload"); time.sleep(4)
c0 = ev("(()=>{const v=document.querySelector('#stage svg').viewBox.baseVal;return [Math.round(v.x+v.width/2),Math.round(v.y+v.height/2)];})()")
ev("document.getElementById('zoomIn').click()"); time.sleep(0.5)
c1 = ev("(()=>{const v=document.querySelector('#stage svg').viewBox.baseVal;return [Math.round(v.x+v.width/2),Math.round(v.y+v.height/2)];})()")
print("centre before/after zoomIn:", c0, c1, "| stable:", c0==c1, "| zoom:", round(spec_zoom(),3))

print("\n== Fit / zoom-to-selection on blank and on content ==")
ev("document.getElementById('zoomFit').click()"); time.sleep(0.5)
print("blank fit -> vb:", vb(), "zoom:", spec_zoom())
key("!","!",49,8); time.sleep(0.5); print("shift+! -> vb:", vb())
ev("document.querySelector('[data-scene-module=flow]').click()"); time.sleep(1.6)
ev("document.getElementById('zoomFit').click()"); time.sleep(0.6)
print("content fit -> vb:", vb(), "zoom:", round(spec_zoom(),3))
boxes = ev("[...document.querySelectorAll('#stage .alur-node')].map(n=>{const b=n.getBoundingClientRect();return [Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height)];})")
print("nodes:", json.dumps(boxes))
inside = ev("(()=>{const r=document.querySelector('#stage').getBoundingClientRect();return [...document.querySelectorAll('#stage .alur-node')].every(n=>{const b=n.getBoundingClientRect();return b.x>=r.x-1&&b.y>=r.y-1&&b.right<=r.right+1&&b.bottom<=r.bottom+1;});})()")
print("all nodes inside viewport after fit:", inside)
print("\nexceptions:", len(errs))
ws.close(); proc.terminate()
