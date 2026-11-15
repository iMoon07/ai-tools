import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9874
W,H=1600,1000
tmp=tempfile.mkdtemp(prefix="pj")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox",
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
    if r.get("subtype")=="error": print("JS ERROR:",r.get("description"))
    return r.get("value")
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)

m = """(function(){
 var st=document.getElementById('stage');
 var svg=st.querySelector('svg');
 var stR=st.getBoundingClientRect(), svR=svg.getBoundingClientRect();
 var grid=svg.querySelector('.alur-canvas-grid');
 return {stage:[Math.round(stR.width),Math.round(stR.height)],
   svg:[Math.round(svR.width),Math.round(svR.height)],
   svgAttr:[svg.getAttribute('width'),svg.getAttribute('height')],
   svgStyle:[svg.style.width,svg.style.height],
   vb:svg.getAttribute('viewBox'),
   gridW:grid.getAttribute('width'), gridH:grid.getAttribute('height'),
   stageStyle:[st.style.left,st.style.right,st.style.top,st.style.bottom]};
})()"""
print("closed:", ev(m))
ev("""(function(){var b=document.querySelector('[data-panel="assets"]'); b.click(); return 1;})()""")
time.sleep(1.2)
print("opened:", ev(m))
# force a resize event
cmd("Emulation.setDeviceMetricsOverride",width=W-2,height=H,deviceScaleFactor=1,mobile=False)
time.sleep(0.6)
print("after 1px resize:", ev(m))
c.close(); proc.terminate()
