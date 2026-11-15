import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=int(sys.argv[1]); URL=sys.argv[2]; W=int(sys.argv[3]); H=int(sys.argv[4])
tmp=tempfile.mkdtemp(prefix="st")
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
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=W<700)
cmd("Page.navigate",url=URL); time.sleep(2.8)
print("== %s %dx%d ==" % (URL.split('/')[-1], W, H))
print("doc:", ev("({sw:document.documentElement.scrollWidth, iw:document.documentElement.clientWidth, sh:document.documentElement.scrollHeight})"))
print("nav:", ev("""(function(){var n=document.querySelector('.navigation'); if(!n) return 'none';
  var b=n.getBoundingClientRect(); var cs=getComputedStyle(n);
  return {pos:cs.position, bottom:cs.bottom, top:cs.top, y:Math.round(b.y), h:Math.round(b.height), w:Math.round(b.width),
    items:Array.prototype.map.call(n.querySelectorAll('.nav-item'),function(a){var r=a.getBoundingClientRect();
      return {t:a.textContent.trim().split('\\n')[0].slice(0,10),fs:getComputedStyle(a).fontSize,h:Math.round(r.height),w:Math.round(r.width)};})};})()"""))
print("offscreen-x:", ev("""(function(){var out=[];var all=document.querySelectorAll('body *');
  for(var k=0;k<all.length;k++){var e=all[k];var b=e.getBoundingClientRect();
    if(b.width>0&&(b.right>%d+1||b.left<-1)) out.push({c:(e.className||'').toString().slice(0,30),l:Math.round(b.left),r:Math.round(b.right)});}
  return out.slice(0,10);})()""" % W))
c.close(); proc.terminate()
