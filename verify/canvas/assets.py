import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9994
W=int(sys.argv[1]); H=int(sys.argv[2]); MOBILE=W<700
tmp=tempfile.mkdtemp(prefix="as")
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
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=MOBILE)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("document.querySelector('[data-panel=\"assets\"]').click()")
time.sleep(0.8)
print("== %dx%d assets ==" % (W,H))
print("dock:", ev("""(function(){var d=document.getElementById('panelAssets');var b=d.getBoundingClientRect();
  return {l:Math.round(b.left),t:Math.round(b.top),w:Math.round(b.width),h:Math.round(b.height),
    inView:(b.left>=0&&b.top>=0&&b.right<=%d&&b.bottom<=%d)};})()""" % (W,H)))
print("gridcss:", ev("""(function(){var g=document.getElementById('logoGrid');var c=getComputedStyle(g);
  var par=g.parentElement;return {maxH:c.maxHeight,flex:c.flex,disp:c.display,h:Math.round(g.getBoundingClientRect().height),
    parDisp:getComputedStyle(par).display,parH:Math.round(par.getBoundingClientRect().height),
    parFlex:getComputedStyle(par).flex};})()"""))
print("tiles:", ev("""(function(){var g=document.getElementById('logoGrid');
  var t=g.querySelectorAll('.logo-tile'); var first=t[0];
  var fb=first?first.getBoundingClientRect():null;
  return {n:t.length,cols:getComputedStyle(g).gridTemplateColumns,
    tile:fb?{w:Math.round(fb.width),h:Math.round(fb.height)}:null,
    hasCap:!!g.querySelector('.lg-name'), capText:(g.querySelector('.lg-name')||{}).textContent,
    gridH:Math.round(g.getBoundingClientRect().height), sh:g.scrollHeight};})()"""))
print("imgs loaded:", ev("""(function(){var a=document.querySelectorAll('#logoGrid img');
  var bad=0; for(var k=0;k<a.length;k++){ if(!a[k].complete||a[k].naturalWidth===0) bad++; }
  return {n:a.length,broken:bad};})()"""))
print("cats:", ev("document.querySelectorAll('#logoCats .chip').length"),
      "search:", ev("""(function(){var e=document.getElementById('logoSearch');var b=e.getBoundingClientRect();
        return {h:Math.round(b.height),w:Math.round(b.width)};})()"""))
print("sections:", ev("""(function(){var o=[];var p=document.getElementById('logoPanel');
  Array.prototype.forEach.call(p.children,function(e){var b=e.getBoundingClientRect();
    o.push({c:(e.className||e.tagName).toString().slice(0,20),h:Math.round(b.height)});});return o;})()"""))
print("overflow:", ev("""(function(){var d=document.documentElement;return {sw:d.scrollWidth,iw:d.clientWidth};})()"""))
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
