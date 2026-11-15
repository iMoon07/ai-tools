import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9330
tmp=tempfile.mkdtemp(prefix="hm")
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
cmd("Page.navigate",url="http://127.0.0.1:8123/index.html#about"); time.sleep(2.8)
print("stage:", ev("""(function(){var e=document.querySelector('main.stage');var b=e.getBoundingClientRect();
  return {y:Math.round(b.y),h:Math.round(b.height)};})()"""))
print("hero:", ev("""(function(){var e=document.querySelector('.home-art'); if(!e) return null; var b=e.getBoundingClientRect();
  var i=e.querySelector('img'); var ib=i?i.getBoundingClientRect():null;
  return {y:Math.round(b.y),h:Math.round(b.height),imgH:ib?Math.round(ib.height):null};})()"""))
print("copy:", ev("""(function(){var e=document.querySelector('.home-copy'); if(!e) return null; var b=e.getBoundingClientRect();
  return {y:Math.round(b.y),h:Math.round(b.height),fs:getComputedStyle(e.querySelector('h1')).fontSize};})()"""))
print("about visible:", ev("""(function(){var e=document.getElementById('aboutPage');return e?{hidden:e.hidden,h:Math.round(e.getBoundingClientRect().height)}:null;})()"""))
print("tap small:", ev("""(function(){var out=[];var all=document.querySelectorAll('a,button');
  for(var k=0;k<all.length;k++){var e=all[k];var b=e.getBoundingClientRect();
   if(b.width>0&&b.height>0&&(b.height<32||b.width<32)) out.push({c:(e.className||'').toString().slice(0,20),t:(e.textContent||'').trim().slice(0,10),w:Math.round(b.width),h:Math.round(b.height)});}
  return out.slice(0,8);})()"""))
c.close(); proc.terminate()
