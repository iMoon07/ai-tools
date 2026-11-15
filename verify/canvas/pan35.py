import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9648; PROF="/tmp/alur-probes/prof-pan35"
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
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=90,suppress_origin=True)
n=[0]; errs=[]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]:
            if r.get("method")=="Runtime.exceptionThrown":
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text")); print("   [EXC]", d.get("text"), (d.get("exception") or {}).get("description","")[:180])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
def vb():
    return ev("(()=>{const v=document.querySelector('#stage svg').viewBox.baseVal; return [Math.round(v.x),Math.round(v.y),Math.round(v.width),Math.round(v.height)];})()")
def drag(x1,y1,x2,y2,steps=8,button="left"):
    send("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button=button,clickCount=1,buttons=1)
    for i in range(1,steps+1):
        send("Input.dispatchMouseEvent",type="mouseMoved",x=x1+(x2-x1)*i/steps,y=y1+(y2-y1)*i/steps,button=button,buttons=1)
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button=button,clickCount=1,buttons=0)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
spec={"module":"canvas","title":"Zoom test","width":1500,"height":944,"zoom":0.35,"panX":0,"panY":0,"grid":True,
 "nodes":{"a":{"id":"a","shape":"box","x":200,"y":200,"w":180,"h":70,"label":"Alpha","sub":"browser"},
          "b":{"id":"b","shape":"box","x":480,"y":200,"w":180,"h":70,"label":"Beta","sub":"node"},
          "c":{"id":"c","shape":"box","x":200,"y":360,"w":180,"h":70,"label":"Gamma","sub":"postgres"}},
 "edges":[{"from":"a","to":"b"}],"drawings":[]}
send("Page.addScriptToEvaluateOnNewDocument",source="localStorage.setItem('ruang.scene.v1', %s);" % json.dumps(json.dumps(spec)))
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.5)
print("zoom:", ev("JSON.parse(document.getElementById('stage').getAttribute('data-spec')).zoom"), "| viewBox:", vb())
print("node screen box:", ev("(()=>{const n=document.querySelector('#stage .alur-node'); if(!n) return null; const b=n.getBoundingClientRect(); return [b.x,b.y,b.width,b.height].map(Math.round);})()"))
V0 = vb()
# empty spot: bottom-left of the stage
stg = ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()")
bx, by = stg['x']+80, stg['y']+stg['h']-80
print("\n-- space+drag --")
send("Input.dispatchKeyEvent",type="keyDown",code="Space",key=" ",windowsVirtualKeyCode=32,nativeVirtualKeyCode=32)
send("Input.dispatchKeyEvent",type="char",text=" ")
drag(bx,by,bx+200,by-150)
send("Input.dispatchKeyEvent",type="keyUp",code="Space",key=" ",windowsVirtualKeyCode=32,nativeVirtualKeyCode=32)
time.sleep(0.6); V1=vb(); print("viewBox:", V1, "| moved:", V0!=V1)
print("\n-- middle drag --")
drag(bx,by,bx+200,by-150,button="middle"); time.sleep(0.6); V2=vb(); print("viewBox:", V2, "| moved:", V1!=V2)
print("\n-- pan tool drag --")
ev("document.querySelector('.tool[data-tool=pan]').click()"); time.sleep(0.3)
drag(bx,by,bx+200,by-150); time.sleep(0.6); V3=vb(); print("viewBox:", V3, "| moved:", V2!=V3)
ev("document.querySelector('.tool[data-tool=select]').click()"); time.sleep(0.3)
print("\n-- wheel pan (deltaY 300) --")
send("Input.dispatchMouseEvent",type="mouseWheel",x=bx,y=by,deltaX=0,deltaY=300); time.sleep(0.6); V4=vb(); print("viewBox:", V4, "| moved:", V3!=V4)
print("\n-- ctrl+wheel zoom out --")
send("Input.dispatchMouseEvent",type="mouseWheel",x=bx,y=by,deltaX=0,deltaY=300,modifiers=2); time.sleep(0.6)
print("viewBox:", vb(), "| zoom:", ev("JSON.parse(document.getElementById('stage').getAttribute('data-spec')).zoom"))
print("\n-- arrow keys (nothing selected) --")
ev("document.querySelectorAll('#stage .alur-node').forEach(n=>n.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,button:0})))"); time.sleep(0.3)
V5=vb()
for k,code,vk in (("ArrowRight","ArrowRight",39),("ArrowDown","ArrowDown",40)):
    send("Input.dispatchKeyEvent",type="keyDown",code=code,key=k,windowsVirtualKeyCode=vk,nativeVirtualKeyCode=vk)
    send("Input.dispatchKeyEvent",type="keyUp",code=code,key=k,windowsVirtualKeyCode=vk,nativeVirtualKeyCode=vk)
    time.sleep(0.3)
print("viewBox:", vb(), "| moved:", V5!=vb())
print("exceptions:", len(errs))
ws.close(); proc.terminate()
