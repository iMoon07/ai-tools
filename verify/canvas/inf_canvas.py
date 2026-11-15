import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9649; PROF="/tmp/alur-probes/prof-inf"
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
def vb():
    return ev("(()=>{const v=document.querySelector('#stage svg').viewBox.baseVal; return [Math.round(v.x),Math.round(v.y),Math.round(v.width),Math.round(v.height)];})()")
def zoom(): return ev("JSON.parse(document.getElementById('stage').getAttribute('data-spec')).zoom")
def key(k, code, vk, shift=False):
    mods = 8 if shift else 0
    send("Input.dispatchKeyEvent",type="keyDown",code=code,key=k,windowsVirtualKeyCode=vk,nativeVirtualKeyCode=vk,modifiers=mods)
    send("Input.dispatchKeyEvent",type="keyUp",code=code,key=k,windowsVirtualKeyCode=vk,nativeVirtualKeyCode=vk,modifiers=mods)
    time.sleep(0.25)
def drag(x1,y1,x2,y2,steps=8):
    send("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1,buttons=1)
    for i in range(1,steps+1):
        send("Input.dispatchMouseEvent",type="mouseMoved",x=x1+(x2-x1)*i/steps,y=y1+(y2-y1)*i/steps,button="left",buttons=1)
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1,buttons=0)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
spec={"module":"canvas","title":"Zoom test","width":1500,"height":944,"zoom":0.35,"panX":0,"panY":0,"grid":True,
 "nodes":{"a":{"id":"a","shape":"box","x":200,"y":200,"w":180,"h":70,"label":"Alpha","sub":"browser"},
          "b":{"id":"b","shape":"box","x":480,"y":200,"w":180,"h":70,"label":"Beta","sub":"node"}},
 "edges":[{"from":"a","to":"b"}],"drawings":[]}
send("Page.addScriptToEvaluateOnNewDocument",source="localStorage.setItem('ruang.scene.v1', %s);" % json.dumps(json.dumps(spec)))
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.5)
stg = ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()")
print("stage:", [round(stg[k]) for k in ('x','y','w','h')], "| zoom:", round(zoom(),3))
print("viewBox @35%:", vb(), "| expect vw=", round(stg['w']/0.35))
print("node box:", ev("(()=>{const n=document.querySelector('#stage .alur-node');const b=n.getBoundingClientRect();return [Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height)];})()"))

print("\n-- arrow keys pan (no selection) --")
ev("document.querySelectorAll('#stage .is-selected').forEach(e=>e.classList.remove('is-selected'))")
V0=vb()
key("ArrowRight","ArrowRight",39); key("ArrowRight","ArrowRight",39)
V1=vb(); print("right x2:", V0, "->", V1, "| moved:", V0!=V1, "| dx px:", round((V1[0]-V0[0])*0.35))
key("ArrowDown","ArrowDown",40); key("ArrowDown","ArrowDown",40)
V2=vb(); print("down x2:", V1, "->", V2, "| dy px:", round((V2[1]-V1[1])*0.35))
key("ArrowLeft","ArrowLeft",37,shift=True)
V3=vb(); print("shift-left:", V2, "->", V3, "| dx px:", round((V3[0]-V2[0])*0.35))

print("\n-- ctrl+wheel zoom at cursor keeps world point --")
send("Input.dispatchMouseEvent",type="mouseMoved",x=stg['x']+stg['w']*0.25,y=stg['y']+stg['h']*0.75)
before = ev("(()=>{const s=document.querySelector('#stage svg');const v=s.viewBox.baseVal;const r=s.getBoundingClientRect();const px=innerWidth*0+0;return null;})()")
def world_at(px,py):
    return ev("""(()=>{const s=document.querySelector('#stage svg');const v=s.viewBox.baseVal;const r=s.getBoundingClientRect();
      const fx=(%d-r.left)/r.width, fy=(%d-r.top)/r.height; return [Math.round(v.x+fx*v.width), Math.round(v.y+fy*v.height)];})()""" % (px,py))
px, py = stg['x']+stg['w']*0.25, stg['y']+stg['h']*0.75
w0 = world_at(px,py)
send("Input.dispatchMouseEvent",type="mouseWheel",x=px,y=py,deltaX=0,deltaY=-120,modifiers=2)
time.sleep(0.6); w1 = world_at(px,py)
print("world under cursor:", w0, "->", w1, "| anchored:", w0==w1, "| zoom:", round(zoom(),3), "| vb:", vb())

print("\n-- zoom out below 35% --")
zs=[]
for i in range(4):
    send("Input.dispatchMouseEvent",type="mouseWheel",x=px,y=py,deltaX=0,deltaY=200,modifiers=2); time.sleep(0.35)
    zs.append(round(zoom(),3))
print("ctrl+wheel out x4 ->", zs, "| final vb:", vb())

print("\n-- Fit button (Ctrl+0) --")
send("Input.dispatchKeyEvent",type="keyDown",code="Digit0",key="0",windowsVirtualKeyCode=48,nativeVirtualKeyCode=48,modifiers=2)
send("Input.dispatchKeyEvent",type="keyUp",code="Digit0",key="0",windowsVirtualKeyCode=48,nativeVirtualKeyCode=48,modifiers=2)
time.sleep(0.7)
print("after Ctrl+0: zoom", round(zoom(),3), "vb", vb(), "| nodes on screen:", ev("(()=>{const a=[...document.querySelectorAll('#stage .alur-node')].map(n=>{const b=n.getBoundingClientRect();return [b.x,b.y,b.width,b.height];});return JSON.stringify(a);})()"))

print("\n-- space+drag pan at current zoom --")
V4=vb()
send("Input.dispatchKeyEvent",type="keyDown",code="Space",key=" ",windowsVirtualKeyCode=32,nativeVirtualKeyCode=32)
drag(200, 800, 500, 600)
send("Input.dispatchKeyEvent",type="keyUp",code="Space",key=" ",windowsVirtualKeyCode=32,nativeVirtualKeyCode=32)
time.sleep(0.5); V5=vb(); print("space+drag:", V4, "->", V5, "| moved:", V4!=V5)

print("\n-- wheel pan --")
send("Input.dispatchMouseEvent",type="mouseWheel",x=300,y=500,deltaX=0,deltaY=200); time.sleep(0.5)
print("wheel:", V5, "->", vb(), "| moved:", V5!=vb())

print("\n-- arrow keys nudge with selection --")
ev("(()=>{const n=document.querySelector('#stage .alur-node'); n.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,button:0,clientX:0,clientY:0})); return 1;})()")
time.sleep(0.4)
sel = ev("(()=>{const s=JSON.parse(localStorage.getItem('ruang.scene.v1')||'{}');return (s.selected||null);})()")
print("selected:", sel)
if sel:
    p0 = ev("(()=>{const n=JSON.parse(localStorage.getItem('ruang.scene.v1')).nodes[%s];return [n.x,n.y];})()" % json.dumps(sel))
    key("ArrowRight","ArrowRight",39); time.sleep(0.4)
    p1 = ev("(()=>{const n=JSON.parse(localStorage.getItem('ruang.scene.v1')).nodes[%s];return [n.x,n.y];})()" % json.dumps(sel))
    print("nudge:", p0, "->", p1, "| moved +1:", p1[0]==p0[0]+1 and p1[1]==p0[1])

print("\nexceptions:", len(errs))
ws.close(); proc.terminate()
