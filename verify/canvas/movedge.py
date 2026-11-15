import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9960
tmp=tempfile.mkdtemp(prefix="me")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox",
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
    if r.get("subtype")=="error": print("JS ERROR:",r.get("description"))
    return r.get("value")
def edges():
    return ev("""(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec')||'{}');
      return (s.edges||[]).map(function(e){return e.points;});})()""")
def drag(x0,y0,x1,y1):
    cmd("Input.dispatchMouseEvent", type="mousePressed", x=x0, y=y0, button="left", clickCount=1)
    for k in range(1,7):
        cmd("Input.dispatchMouseEvent", type="mouseMoved", x=x0+(x1-x0)*k/6.0, y=y0+(y1-y0)*k/6.0, button="left", buttons=1)
        time.sleep(0.03)
    cmd("Input.dispatchMouseEvent", type="mouseReleased", x=x1, y=y1, button="left", clickCount=1)
    time.sleep(0.4)
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")
print("fold closed -> template visible:", ev("(function(){var d=document.getElementById('templateFold');return d?d.open:null;})()"))
print("template items:", ev("document.querySelectorAll('#templateList .block-item').length"))
print("fold list scrollable:", ev("(function(){var h=document.getElementById('templateList');return h?getComputedStyle(h).maxHeight:'x';})()"))
e0 = edges(); print("edges before:", e0)
# find a point on an edge: use midpoint of the first edge
if e0:
    p0 = e0[0][0]; p1 = e0[0][-1]
    mx = (p0[0]+p1[0])/2.0; my = (p0[1]+p1[1])/2.0
    # convert scene -> client via svg CTM
    pt = ev("""(function(){var svg=document.querySelector('#stage svg');var p=svg.createSVGPoint();
      p.x=%f;p.y=%f;var m=svg.getScreenCTM();var q=p.matrixTransform(m);return {x:q.x,y:q.y};})()""" % (mx,my))
    print("click at edge midpoint client:", pt)
    drag(pt["x"], pt["y"], pt["x"]+80, pt["y"]+50)
    e1 = edges(); print("edges after drag:", e1)
    print("moved:", json.dumps(e0) != json.dumps(e1))
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
