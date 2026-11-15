import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9410
tmp=tempfile.mkdtemp(prefix="m2")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=390,844","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
cmd("Emulation.setDeviceMetricsOverride",width=390,height=844,deviceScaleFactor=1,mobile=True)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")
def rect(sel):
    return ev("""(function(){var e=document.querySelector(%s); if(!e) return 'missing';
      var b=e.getBoundingClientRect(); var cs=getComputedStyle(e);
      return {y:Math.round(b.y),h:Math.round(b.height),w:Math.round(b.width),disp:cs.display,vis:cs.visibility};})()""" % json.dumps(sel))
print("topbar:", rect('.topbar'))
print("rail:", rect('#editorBar'))
print("viewbar:", rect('#viewBar'))
print("stage:", rect('#stage'))
print("nav links visible:", ev("""(function(){var a=document.querySelectorAll('.top-link');var n=0;
  for(var k=0;k<a.length;k++){if(a[k].getBoundingClientRect().width>0)n++;}return n+'/'+a.length;})()"""))
ev("document.querySelector('[data-panel=\"scene\"]').click()")
time.sleep(0.6)
print("scene dock:", ev("""(function(){var d=document.getElementById('panelScene');var b=d.getBoundingClientRect();
  var cs=getComputedStyle(d);return {y:Math.round(b.y),h:Math.round(b.height),vis:cs.visibility,tr:cs.transform,radius:cs.borderRadius};})()"""))
print("overflow:", ev("({sw:document.documentElement.scrollWidth, iw:document.documentElement.clientWidth})"))
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
