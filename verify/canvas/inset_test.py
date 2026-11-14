import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9663; PROF="/tmp/kilo/prof-inset"
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
def drag(x1,y1,x2,y2,steps=8):
    send("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1,buttons=1)
    for i in range(1,steps+1):
        send("Input.dispatchMouseEvent",type="mouseMoved",x=x1+(x2-x1)*i/steps,y=y1+(y2-y1)*i/steps,button="left",buttons=1); time.sleep(0.02)
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1,buttons=0); time.sleep(0.8)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.5)
def stage_rect():
    return ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return [Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)];})()")
def panel_state():
    return ev("(()=>{const p=document.getElementById('shapePanel');const r=p.getBoundingClientRect();return {hidden:p.hidden,box:[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)]};})()")
def counts():
    return ev("({n:document.querySelectorAll('#stage .alur-node').length,heads:document.querySelectorAll('#stage .alur-edge-head').length})")
print("initial stage:", stage_rect(), "| panel:", panel_state())
ev("(function(){var b=[].slice.call(document.querySelectorAll('[data-tool]')).filter(function(x){return x.getAttribute('data-tool')==='box';})[0]; b.click(); return 1;})()"); time.sleep(0.4)
drag(700,500,760,540)
print("after 1st box -> stage:", stage_rect(), "| panel:", panel_state(), "| counts:", counts())
print("vb:", ev("(()=>{const v=document.querySelector('#stage svg').viewBox.baseVal;return [Math.round(v.x),Math.round(v.y),Math.round(v.width),Math.round(v.height)];})()"))
ev("(function(){var b=[].slice.call(document.querySelectorAll('[data-tool]')).filter(function(x){return x.getAttribute('data-tool')==='box';})[0]; b.click(); return 1;})()"); time.sleep(0.3)
r = stage_rect()
for label,(fx,fy) in {'TL':(0.03,0.08),'TR':(0.97,0.08),'BL':(0.03,0.92),'BR':(0.96,0.92)}.items():
    ev("(function(){var b=[].slice.call(document.querySelectorAll('[data-tool]')).filter(function(x){return x.getAttribute('data-tool')==='box';})[0]; b.click(); return 1;})()"); time.sleep(0.25)
    x, y = r[0]+r[2]*fx, r[1]+r[3]*fy
    b = counts(); drag(round(x)-25, round(y)-18, round(x)+25, round(y)+18); a = counts()
    print("  ", label, "at", (round(x),round(y)), "-> nodes", b['n'], "->", a['n'], "| hit:", ev("(function(x,y){var e=document.elementFromPoint(x,y); return e?e.tagName.toLowerCase()+(e.id?'#'+e.id:''):'none';})(%d,%d)" % (round(x),round(y))))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
