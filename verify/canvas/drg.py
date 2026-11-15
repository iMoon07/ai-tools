import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9531
W=int(sys.argv[1]) if len(sys.argv)>1 else 1600
H=int(sys.argv[2]) if len(sys.argv)>2 else 1000
tmp=tempfile.mkdtemp(prefix="drg")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=%d,%d"%(W,H),"about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
for _ in range(80):
    try:
        urllib.request.urlopen("http://127.0.0.1:%d/json/version"%PORT,timeout=1).read(); break
    except Exception: time.sleep(0.25)
tabs=json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json"%PORT).read())
page=[t for t in tabs if t["type"]=="page"][0]
c=websocket.create_connection(page["webSocketDebuggerUrl"],timeout=30)
i=[0]
def cmd(m,**p):
    i[0]+=1; c.send(json.dumps({"id":i[0],"method":m,"params":p}))
    while True:
        r=json.loads(c.recv())
        if r.get("id")==i[0]: return r.get("result",{})
def ev(e):
    r=cmd("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)["result"]
    if r.get("subtype")=="error": return {"__err":r.get("description")}
    return r.get("value")
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.2)

def box(sel):
    return ev("""(function(){var d=document.querySelector('%s'); if(!d) return null;
      var b=d.getBoundingClientRect();
      return {id:d.id,x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height),
        ds:d.getAttribute('data-side'),open:d.classList.contains('is-open')};})()""" % sel)

def drag(x1,y1,x2,y2,steps=14):
    cmd("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1)
    for k in range(1,steps+1):
        cmd("Input.dispatchMouseEvent",type="mouseMoved",
            x=int(x1+(x2-x1)*k/steps),y=int(y1+(y2-y1)*k/steps),button="left",buttons=1)
    cmd("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1)
    time.sleep(0.35)

print("== %dx%d ==" % (W,H))

ev("document.querySelector('[data-panel=\"scene\"]').click()"); time.sleep(0.5)
sc = box("#panelScene")
print("scene open:", sc)
if sc:
    hx = sc["x"] + sc["w"] - 5 if sc["ds"] == "left" else sc["x"] + 5
    drag(sc["x"]+40, sc["y"]+18, sc["x"]+140, sc["y"]+120)
    print("  after head drag:", box("#panelScene"))
    drag(hx, sc["y"]+sc["h"]-60, hx+120, sc["y"]+sc["h"]-60)
    print("  after resize drag:", box("#panelScene"))
    print("  handle:", ev("""(function(){var h=document.querySelector('#panelScene .dock-resize'); if(!h) return null;
      var b=h.getBoundingClientRect(); return {x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height)};})()"""))

ev("document.querySelector('[data-panel=\"scene\"]').click()"); time.sleep(0.3)

ev("document.querySelector('[data-panel=\"assets\"]').click()"); time.sleep(0.5)
asx = box("#panelAssets")
print("assets open:", asx)
if asx:
    hx = asx["x"] + 5
    drag(asx["x"]+40, asx["y"]+18, asx["x"]-60, asx["y"]+110)
    print("  after head drag:", box("#panelAssets"))
    drag(hx, asx["y"]+asx["h"]-60, hx-110, asx["y"]+asx["h"]-60)
    print("  after resize drag:", box("#panelAssets"))

ev("document.querySelector('[data-panel=\"assets\"]').click()"); time.sleep(0.3)
ev("document.querySelector('[data-panel=\"layers\"]').click()"); time.sleep(0.5)
ly = box("#panelLayers")
print("layers open:", ly)
if ly:
    hx = ly["x"] + 5
    drag(ly["x"]+40, ly["y"]+18, ly["x"]-50, ly["y"]+100)
    print("  after head drag:", box("#panelLayers"))

print("reload:", ev("location.reload(); 'ok'"))
time.sleep(3.0)
ev("document.querySelector('[data-panel=\"assets\"]').click()"); time.sleep(0.5)
print("assets after reload:", box("#panelAssets"))
c.close(); proc.terminate()