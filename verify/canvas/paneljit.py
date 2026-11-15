import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9873
W,H=(1600,1000)
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

probe = """(function(){
 var st=document.getElementById('stage');
 var p=document.getElementById('panelAssets');
 var svg=document.querySelector('#stage svg');
 var grid=svg?svg.querySelector('.alur-canvas-grid'):null;
 var stR=st.getBoundingClientRect(), pR=p.getBoundingClientRect();
 return {stageL:Math.round(stR.left),stageR:Math.round(innerWidth-stR.right),
         stageW:Math.round(stR.width),stageH:Math.round(stR.height),
         panW:Math.round(pR.width),panL:Math.round(pR.left),panOpen:p.classList.contains('is-open'),
         vb:svg?svg.getAttribute('viewBox'):null,
         gridW:grid?grid.getAttribute('width'):null,
         gridX:grid?grid.getAttribute('x'):null};
})()"""

print("closed:", ev(probe))
# sample frames during open
ev("""(function(){
  window.__s=[];
  var st=document.getElementById('stage'), p=document.getElementById('panelAssets');
  var btn=document.querySelector('[data-panel="assets"]');
  window.__btn=btn;
  var n=0;
  var t=setInterval(function(){
    var stR=st.getBoundingClientRect(), pR=p.getBoundingClientRect();
    window.__s.push({t:n, stW:Math.round(stR.width), stL:Math.round(stR.left),
      pW:Math.round(pR.width), pL:Math.round(pR.left),
      vb:(document.querySelector('#stage svg')||{getAttribute:function(){return null}}).getAttribute('viewBox')});
    if(++n>40) clearInterval(t);
  },25);
  btn.click();
  return 'clicked';
})()""")
time.sleep(1.4)
s = ev("window.__s")
print("frames:", len(s) if s else s)
if s:
    for f in s[::3]:
        print(f)
print("after:", ev(probe))
c.close(); proc.terminate()
