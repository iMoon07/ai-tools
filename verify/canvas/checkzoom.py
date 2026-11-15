import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9655
tmp=tempfile.mkdtemp(prefix="cz")
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
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("document.getElementById('themeToggle').click();")
time.sleep(0.4)
# open assets panel
ev("""(function(){var b=document.querySelector('[data-panel="assets"]'); if(b) b.click();})()""")
time.sleep(0.4)
out=ev(r"""(function(){
  var chip=document.querySelector('#logoCats .chip');
  var zc=document.querySelector('.zoom-cluster');
  var zb=document.querySelector('.zoom-bar');
  var fit=document.getElementById('zoomFit');
  var zv=document.getElementById('zoomVal');
  function st(el){ if(!el) return null; var c=getComputedStyle(el); return {bg:c.backgroundColor,color:c.color,border:c.borderColor};}
  var chips=Array.from(document.querySelectorAll('#logoCats .chip')).slice(0,3).map(function(x){return {t:x.textContent.trim().slice(0,20),s:st(x)};});
  return {chip:chip?{t:chip.textContent.trim().slice(0,20),s:st(chip)}:null, chips:chips, zoomBar:st(zb), zoomCluster:st(zc), fit:st(fit), zoomVal:st(zv), logoCats:st(document.getElementById('logoCats'))};
})()""")
print(json.dumps(out, indent=1))
c.close(); proc.terminate()
