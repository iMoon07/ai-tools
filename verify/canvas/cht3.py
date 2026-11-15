import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9534
tmp=tempfile.mkdtemp(prefix="cht3")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=1600,1000","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
cmd("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.2)

PROBE = open('/tmp/alur-probes/cht_probe2.js').read()

def sel():
    return ev(PROBE)

print("insert:", (ev("document.querySelector('[data-scene-module=\"chart\"]').click()"), time.sleep(1.0), sel())[2])
ev("var b=document.getElementById('shapePanelClose'); if(b) b.click();")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.4)
print("hit:", ev(open('/tmp/alur-probes/cht_probe3.js').read()))
box = ev("(function(){var n=document.querySelector('.alur-chart-node'); var b=n.getBoundingClientRect(); return {x:Math.round(b.x+b.width/2),y:Math.round(b.y+b.height/2)};})()")
print("center:", box)
cmd("Input.dispatchMouseEvent",type="mousePressed",x=box["x"],y=box["y"],button="left",clickCount=1)
for k in range(1,11):
    cmd("Input.dispatchMouseEvent",type="mouseMoved",x=box["x"]-k*8,y=box["y"]+k*6,button="left",buttons=1)
cmd("Input.dispatchMouseEvent",type="mouseReleased",x=box["x"]-80,y=box["y"]+60,button="left",clickCount=1)
time.sleep(0.4)
print("after drag:", ev(PROBE))
print("moved node:", ev("(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec')||'{}');var n=s.nodes[s.selected];return {id:s.selected,x:Math.round(n.x),y:Math.round(n.y),w:n.w,h:n.h};})()"))
ev("document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'Delete',code:'Delete',bubbles:true}))")
time.sleep(0.5)
print("after Del:", ev(PROBE))
c.close(); proc.terminate()