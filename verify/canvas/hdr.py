import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=int(sys.argv[1]); URL=sys.argv[2]
tmp=tempfile.mkdtemp(prefix="hd")
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
cmd("Page.navigate",url=URL); time.sleep(2.8)
print("==", URL.split('/')[-1])
print("hdrs:", ev("""(function(){var o=[];['docs-topbar','article-bar','docs-topnav'].forEach(function(c){
  var e=document.querySelector('.'+c); if(!e){o.push({c:c,none:true});return;}
  var b=e.getBoundingClientRect(); o.push({c:c,y:Math.round(b.y),h:Math.round(b.height),w:Math.round(b.width),disp:getComputedStyle(e).display});});
  return o;})()"""))
print("small btns:", ev("""(function(){var out=[];var all=document.querySelectorAll('button,a');
  for(var k=0;k<all.length;k++){var e=all[k];var b=e.getBoundingClientRect();
   if(b.width>0&&b.height>0&&(b.height<32||b.width<32)) out.push({c:(e.className||'').toString().slice(0,22),t:(e.textContent||'').trim().slice(0,10),w:Math.round(b.width),h:Math.round(b.height)});}
  return out.slice(0,8);})()"""))
c.close(); proc.terminate()
