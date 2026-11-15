import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9537
tmp=tempfile.mkdtemp(prefix="cht6")
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

print(ev("""(function(){
 var st=document.getElementById('stage');
 var sr=st.getBoundingClientRect();
 var logos=Array.prototype.map.call(document.querySelectorAll('.alur-logo-img'),function(e){
   var b=e.getBoundingClientRect(); return {cls:e.getAttribute('class'),parent:e.parentNode.getAttribute&&e.parentNode.getAttribute('class'),x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height)};});
 var n1=document.querySelector('[data-node-id="n1"]');
 var nb=n1.getBoundingClientRect();
 var cx=Math.round(nb.x+nb.width/2), cy=Math.round(nb.y+nb.height/2);
 var stack=document.elementsFromPoint(cx,cy).map(function(e){return e.tagName+'.'+(e.getAttribute('class')||'');}).slice(0,6);
 return {stage:{x:Math.round(sr.x),y:Math.round(sr.y),w:Math.round(sr.width),h:Math.round(sr.height)},
   n1:{x:Math.round(nb.x),y:Math.round(nb.y),w:Math.round(nb.width),h:Math.round(nb.height)},
   cx:cx,cy:cy,logos:logos.slice(0,6),logoCount:logos.length,stack:stack};
})()"""))
c.close(); proc.terminate()