import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9653; PROF="/tmp/kilo/prof-fullarea"
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
def drag(x1,y1,x2,y2,steps=10):
    send("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1,buttons=1)
    for i in range(1,steps+1):
        send("Input.dispatchMouseEvent",type="mouseMoved",x=x1+(x2-x1)*i/steps,y=y1+(y2-y1)*i/steps,button="left",buttons=1)
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1,buttons=0)
    time.sleep(0.25)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
stg = ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()")
print("stage:", {k: round(stg[k]) for k in ('x','y','w','h')})
print("svg rect:", ev("(()=>{const s=document.querySelector('#stage svg');const r=s.getBoundingClientRect();return {x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height),cw:s.clientWidth,ch:s.clientHeight,attr:[s.getAttribute('width'),s.getAttribute('height')]};})()"))
print("\n-- what is on top at each point --")
pts = {'TL':(0.01,0.03),'TC':(0.5,0.03),'TR':(0.99,0.03),'ML':(0.01,0.5),'C':(0.5,0.5),'MR':(0.99,0.5),'BL':(0.01,0.97),'BC':(0.5,0.97),'BR':(0.99,0.97)}
for name,(fx,fy) in pts.items():
    x, y = stg['x']+stg['w']*fx, stg['y']+stg['h']*fy
    info = ev("""(()=>{const e=document.elementFromPoint(%d,%d); if(!e) return 'none';
      const chain=[];let c=e;while(c&&chain.length<5){chain.push(c.tagName.toLowerCase()+(c.id?'#'+c.id:'')+(c.getAttribute&&c.getAttribute('class')?'.'+String(c.getAttribute('class')).split(' ')[0]:''));c=c.parentElement;}
      return chain.join(' < ');})()""" % (round(x),round(y)))
    print(f"  {name} ({round(x)},{round(y)}): {info}")
print("\n-- draw arrows in 9 zones --")
ev("document.querySelector('.tool[data-tool=arrow]').click()"); time.sleep(0.3)
before = ev("""(()=>{try{return (JSON.parse(localStorage.getItem('ruang.scene.v1')).drawings||[]).length;}catch(e){return -1;}})()""")
ok = {}
for name,(fx,fy) in pts.items():
    x, y = stg['x']+stg['w']*fx, stg['y']+stg['h']*fy
    drag(round(x)-30, round(y)-20, round(x)+30, round(y)+20)
    after = ev("""(()=>{try{return (JSON.parse(localStorage.getItem('ruang.scene.v1')).drawings||[]).length;}catch(e){return -1;}})()""")
    ok[name] = after - before
    before = after
print("drawings added per zone:", ok)
print("\n-- draw boxes/circles/lines in corners --")
ev("document.querySelector('.tool[data-tool=box]').click()"); time.sleep(0.3)
def nodes(): return ev("(()=>{try{return Object.keys(JSON.parse(localStorage.getItem('ruang.scene.v1')).nodes||{}).length;}catch(e){return -1;}})()")
res={}
for name in ('TL','BR','TR','BL'):
    fx,fy = pts[name]
    x, y = stg['x']+stg['w']*fx, stg['y']+stg['h']*fy
    b = nodes(); drag(round(x)-40, round(y)-30, round(x)+40, round(y)+30); res[name]=nodes()-b
print("boxes added per corner:", res)
print("exceptions:", len(errs))
ws.close(); proc.terminate()
