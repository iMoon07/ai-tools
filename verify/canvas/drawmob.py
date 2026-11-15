import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9303
W,H=390,844
tmp=tempfile.mkdtemp(prefix="dm")
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
    if r.get("subtype")=="error": print("JS ERROR:",r.get("description"))
    return r.get("value")
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=True)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")
print("topbar:", ev("""(function(){var e=document.querySelector('.topbar');var b=e.getBoundingClientRect();
  return {y:Math.round(b.y),h:Math.round(b.height),w:Math.round(b.width)};})()"""))
print("rail:", ev("""(function(){var e=document.getElementById('editorBar');var b=e.getBoundingClientRect();
  var cs=getComputedStyle(e);
  return {disp:cs.display,y:Math.round(b.y),h:Math.round(b.height),w:Math.round(b.width),
    sw:e.scrollWidth,cw:e.clientWidth,tools:e.querySelectorAll('.tool').length};})()"""))
print("viewbar:", ev("""(function(){var e=document.getElementById('viewBar');var b=e.getBoundingClientRect();
  return {y:Math.round(b.y),h:Math.round(b.height)};})()"""))
print("stage:", ev("""(function(){var e=document.getElementById('stage');var b=e.getBoundingClientRect();
  return {y:Math.round(b.y),h:Math.round(b.height)};})()"""))
print("fab gone:", ev("!document.getElementById('mobileFab') && !document.getElementById('mobileMenu')"))
print("small taps:", ev("""(function(){var r=document.getElementById('editorBar');var out=[];
  Array.prototype.forEach.call(r.querySelectorAll('.tool'),function(e){var b=e.getBoundingClientRect();
   if(b.width>0&&(b.width<36||b.height<36)) out.push({t:(e.getAttribute('aria-label')||'').slice(0,12),w:Math.round(b.width),h:Math.round(b.height)});});
  return out.slice(0,8);})()"""))
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
