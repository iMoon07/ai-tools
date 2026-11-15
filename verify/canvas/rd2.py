import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9552
tmp=tempfile.mkdtemp(prefix="rd2")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=1400,900","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
cmd("Emulation.setDeviceMetricsOverride",width=1400,height=900,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/read.html"); time.sleep(3.0)
SPEC = r'''{"module":"canvas","title":"My canvas","grid":true,"width":900,"height":520,"cable":"solid","motion":"flow","speed":1,"nodes":{"n27":{"id":"n27","x":638,"y":726,"w":418,"h":242,"shape":"table","label":"","sub":"","color":"blue","columns":["Column 1","Column 2","Column 3"],"rows":[["","",""],["","",""],["","",""]]}},"edges":[],"selected":"n27","selectedEdge":null,"selectedEdges":[],"selectedDrawing":null,"zoom":0.6,"panX":-434,"panY":333,"edgeStyle":{},"drawings":[]}'''
js = "(function(){var d=document.createElement('div');d.className='alur draw';d.setAttribute('data-spec', %s);var host=document.getElementById('content')||document.body;host.appendChild(d);window.Alur.init(host);var svg=d.querySelector('svg');var tb=d.querySelector('table');return {svg:!!svg, table:!!tb, ready:d.getAttribute('data-ready'), html:d.innerHTML.slice(0,120), vb:svg?svg.getAttribute('viewBox'):null};})()" % json.dumps(SPEC)
print(ev(js))
c.close(); proc.terminate()
