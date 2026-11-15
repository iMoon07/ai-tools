import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9535
tmp=tempfile.mkdtemp(prefix="cht4")
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

ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
ev("var b=document.getElementById('shapePanelClose'); if(b) b.click();")
time.sleep(0.3)
ev("document.querySelector('[data-scene-module=\"chart\"]').click()")
time.sleep(1.0)

POS = """(function(){var id=arguments; return null;})"""
def node_xy(nid):
    return ev("(function(){var n=JSON.parse(document.getElementById('stage').getAttribute('data-spec')).nodes['%s'];"
              "var el=document.querySelector('[data-node-id=\"%s\"]');var b=el.getBoundingClientRect();"
              "return {sx:Math.round(b.x+b.width*0.8),sy:Math.round(b.y+b.height*0.6),x:n.x,y:n.y};})()" % (nid,nid))

def drag(x1,y1,x2,y2):
    cmd("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1)
    for k in range(1,12):
        cmd("Input.dispatchMouseEvent",type="mouseMoved",x=int(x1+(x2-x1)*k/11),y=int(y1+(y2-y1)*k/11),button="left",buttons=1)
    cmd("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1)
    time.sleep(0.35)

b = node_xy('n1'); print("n1 before:", b)
drag(b['sx'], b['sy'], b['sx']-60, b['sy']+40)
print("n1 after :", node_xy('n1'))

ch = node_xy('n4'); print("n4 before:", ch)
drag(ch['sx'], ch['sy'], ch['sx']-60, ch['sy']+40)
print("n4 after :", node_xy('n4'))
c.close(); proc.terminate()