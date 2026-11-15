import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9440
W,H=390,844
tmp=tempfile.mkdtemp(prefix="pm")
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
    if r.get("subtype")=="error": return {"__err":r.get("description")}
    return r.get("value")
def tap(sel):
    r=ev("""(function(){var e=document.querySelector(%s); if(!e) return null;
      var b=e.getBoundingClientRect(); return [Math.round(b.x+b.width/2), Math.round(b.y+b.height/2)];})()""" % json.dumps(sel))
    if not r: return None
    cmd("Input.dispatchMouseEvent", type="mousePressed", x=r[0], y=r[1], button="left", clickCount=1)
    cmd("Input.dispatchMouseEvent", type="mouseReleased", x=r[0], y=r[1], button="left", clickCount=1)
    time.sleep(0.45)
    return r
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=True)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")
print("toggle:", ev("""(function(){var e=document.getElementById('panelToggle');if(!e)return 'missing';
  var b=e.getBoundingClientRect();return {disp:getComputedStyle(e).display,y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height)};})()"""))
print("tabs:", ev("""(function(){var e=document.getElementById('mobileTabs');var b=e.getBoundingClientRect();
  return {disp:getComputedStyle(e).display,y:Math.round(b.y),h:Math.round(b.height),n:e.querySelectorAll('.mtab').length};})()"""))
print("rail hidden:", ev("getComputedStyle(document.getElementById('editorBar')).display"))
print("viewbar hidden:", ev("getComputedStyle(document.getElementById('viewBar')).display"))
print("toolGrid n:", ev("document.querySelectorAll('#toolGrid .tool').length"))
print("grid cols:", ev("getComputedStyle(document.getElementById('toolGrid')).gridTemplateColumns"))
print("first tools:", ev("""(function(){var l=document.querySelectorAll('#toolGrid .tool');
  return Array.prototype.map.call(l,function(b){return b.getAttribute('data-tool')||b.getAttribute('data-panel')||b.id;}).slice(0,14);})()"""))
tap('#panelToggle')
print("after toggle -> tools dock:", ev("""(function(){var d=document.getElementById('panelTools');var b=d.getBoundingClientRect();
  var cs=getComputedStyle(d);return {open:d.classList.contains('is-open'),y:Math.round(b.y),h:Math.round(b.height),vis:cs.visibility};})()"""))
tap('[data-open-panel="assets"]')
print("after Assets tab:", ev("""(function(){var d=document.getElementById('panelAssets');var b=d.getBoundingClientRect();
  return {open:d.classList.contains('is-open'),y:Math.round(b.y),h:Math.round(b.height)};})()"""))
print("tools closed:", ev("!document.getElementById('panelTools').classList.contains('is-open')"))
tap('[data-open-panel="properties"]')
print("after Edit tab:", ev("""(function(){var d=document.getElementById('shapePanel');var b=d.getBoundingClientRect();
  return {hidden:d.hidden,h:Math.round(b.height),y:Math.round(b.y)};})()"""))
tap('#panelToggle')
print("after toggle close:", ev("""(function(){var open=document.querySelectorAll('.dock.is-open').length;
  return {openDocks:open, shapeHidden:document.getElementById('shapePanel').hidden};})()"""))
print("overflow:", ev("({sw:document.documentElement.scrollWidth, iw:document.documentElement.clientWidth})"))
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
