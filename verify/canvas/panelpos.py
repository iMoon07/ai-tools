import json, sys, time, urllib.request, subprocess, tempfile
import websocket
PORT=int(sys.argv[1]); W=int(sys.argv[2]); H=int(sys.argv[3])
tmp=tempfile.mkdtemp(prefix="pp")
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
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=W<600)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")

def box(sel):
    return ev("""(function(){var e=document.querySelector(%s); if(!e) return null;
      var r=e.getBoundingClientRect();
      return {l:Math.round(r.left),t:Math.round(r.top),w:Math.round(r.width),h:Math.round(r.height),open:e.classList.contains('is-open')};})()""" % json.dumps(sel))

def click(sel):
    ev("""(function(){var b=document.querySelector(%s); if(b) b.click(); return !!b;})()""" % json.dumps(sel))
    time.sleep(0.6)

print("=== %dx%d ===" % (W,H))
click('[data-panel="assets"]'); print("assets:", box('#panelAssets'))
click('[data-panel="layers"]'); print("layers:", box('#panelLayers'))
click('[data-panel="layers"]')
click('[data-panel="assets"]')
print("both same box:", box('#panelAssets')==box('#panelLayers'))

# jitter sample while opening
ev("""(function(){
  window.__s=[]; var p=document.getElementById('panelAssets');
  var n=0; var t=setInterval(function(){
    var r=p.getBoundingClientRect();
    window.__s.push([Math.round(r.left),Math.round(r.top),Math.round(r.width)]);
    if(++n>24) clearInterval(t);
  },30);
  document.querySelector('[data-panel="layers"]').click();
  document.querySelector('[data-panel="assets"]').click();
  return 1;})()""")
time.sleep(1.2)
s=ev("window.__s")
uniq=[]
if s:
    for f in s:
        if f not in uniq: uniq.append(f)
print("distinct frames during open:", uniq)

print("doc:", ev("({sw:document.documentElement.scrollWidth, iw:innerWidth})"))
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
