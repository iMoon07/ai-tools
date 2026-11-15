import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9991
W=int(sys.argv[1]); H=int(sys.argv[2]); MOBILE=W<700
tmp=tempfile.mkdtemp(prefix="ly")
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
ev("document.querySelector('[data-panel=\"scene\"]').click()")
time.sleep(0.7)
print("== %dx%d scene panel ==" % (W,H))
print("dock rect:", ev("""(function(){var d=document.getElementById('panelScene');var b=d.getBoundingClientRect();
  return {l:Math.round(b.left),t:Math.round(b.top),w:Math.round(b.width),h:Math.round(b.height),
          inView:(b.left>=0&&b.top>=0&&b.right<=%d&&b.bottom<=%d)};})()""" % (W,H)))
print("folds:", ev("""(function(){var o=[];
  ['blockSection','templateFold','linkSection','chartSection','playbackSection'].forEach(function(id){
    var d=document.getElementById(id); if(!d) return; var s=d.querySelector('summary'); var b=s.getBoundingClientRect();
    o.push({id:id,h:Math.round(b.height),open:!!d.open});});
  return o;})()"""))
print("h overflow:", ev("""(function(){var d=document.getElementById('panelScene');var b=d.getBoundingClientRect();var out=[];
  Array.prototype.forEach.call(d.querySelectorAll('*'),function(e){var r=e.getBoundingClientRect();
    if(r.width>0&&(r.right>b.right+1||r.left<b.left-1)) out.push({c:(e.className||'').toString().slice(0,26),l:Math.round(r.left),r:Math.round(r.right)});});
  return out.slice(0,8);})()"""))
print("tap targets:", ev("""(function(){var d=document.getElementById('panelScene');var small=[];
  Array.prototype.forEach.call(d.querySelectorAll('button,summary,select,input'),function(e){
    var r=e.getBoundingClientRect(); if(r.width>0&&(r.height<28||r.width<28))
      small.push({c:(e.className||'').toString().slice(0,20),t:(e.textContent||'').trim().slice(0,16),w:Math.round(r.width),h:Math.round(r.height)});});
  return small.slice(0,10);})()"""))
print("body scroll:", ev("""(function(){var d=document.querySelector('#panelScene .dock-body');
  return {h:Math.round(d.clientHeight),sh:d.scrollHeight};})()"""))
print("export visible:", ev("""(function(){var e=document.getElementById('exportBox');var b=e.getBoundingClientRect();
  var d=document.querySelector('#panelScene .dock-body').getBoundingClientRect();
  return {top:Math.round(b.top),dockBottom:Math.round(d.bottom),pinned:b.top>=d.bottom-2};})()"""))
c.close(); proc.terminate()
