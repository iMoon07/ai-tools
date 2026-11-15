import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9984
W=int(sys.argv[1]); H=int(sys.argv[2]); MOBILE = W<700
tmp=tempfile.mkdtemp(prefix="pn")
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
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")
print("== %dx%d ==" % (W,H))
print("panels:", ev("""(function(){var o={};
  ['blockSection','templateFold','linkSection','chartSection','playbackSection'].forEach(function(id){
    var d=document.getElementById(id); if(!d){o[id]='missing';return;}
    o[id]={tag:d.tagName,open:!!d.open,hidden:!!d.hidden,items:d.querySelectorAll('.block-item').length};
  }); return o;})()"""))
print("blockList cols:", ev("getComputedStyle(document.getElementById('blockList')).gridTemplateColumns"))
print("items:", ev("""(function(){var l=document.querySelectorAll('#blockList .block-item');
  return Array.prototype.map.call(l,function(b){return b.textContent.trim().replace(/\\s+/g,' ');});})()"""))
print("overflow:", ev("""(function(){var d=document.documentElement;return {sw:d.scrollWidth,iw:d.clientWidth,sh:d.scrollHeight,ih:d.clientHeight};})()"""))
print("stage:", ev("""(function(){var s=document.getElementById('stage');var b=s.getBoundingClientRect();
  return {x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height)};})()"""))
ev("document.getElementById('templateFold').open=true")
time.sleep(0.4)
print("tpl groups:", ev("document.querySelectorAll('#templateList .tpl-group').length"),
      "items:", ev("document.querySelectorAll('#templateList .block-item').length"))
print("tpl scroll:", ev("""(function(){var h=document.getElementById('templateList');var b=h.getBoundingClientRect();
  return {h:Math.round(b.height),sh:h.scrollHeight,ovf:getComputedStyle(h).overflowY};})()"""))
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
