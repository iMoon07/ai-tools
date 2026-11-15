import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9995
W,H=1600,1000
tmp=tempfile.mkdtemp(prefix="lg")
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
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")
ev("document.querySelector('[data-panel=\"assets\"]').click()")
time.sleep(0.7)
print("tiles:", ev("document.querySelectorAll('#logoGrid .logo-tile').length"))
print("first tile:", ev("""(function(){var t=document.querySelector('#logoGrid .logo-tile');
  if(!t) return null; var img=t.querySelector('img'); var cap=t.querySelector('.lg-name');
  return {name:cap?cap.textContent:null, src:img?(img.getAttribute('src')||'').slice(0,50):null,
    loaded:img?(img.complete&&img.naturalWidth>0):null, title:t.title};})()"""))
r = ev("""(function(){var t=document.querySelector('#logoGrid .logo-tile');
  var b=t.getBoundingClientRect(); return [Math.round(b.x+b.width/2), Math.round(b.y+b.height/2)];})()""")
cmd("Input.dispatchMouseEvent", type="mousePressed", x=r[0], y=r[1], button="left", clickCount=1)
cmd("Input.dispatchMouseEvent", type="mouseReleased", x=r[0], y=r[1], button="left", clickCount=1)
time.sleep(0.6)
print("after click:", ev("""(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec')||'{}');
  var ns=s.nodes||{}; var logos=[];
  Object.keys(ns).forEach(function(k){var n=ns[k]; if(n.logo) logos.push({id:k,logo:n.logo,shape:n.shape});});
  return {nodes:Object.keys(ns).length, logos:logos};})()"""))
print("on tiles:", ev("document.querySelectorAll('#logoGrid .logo-tile.is-on').length"))
print("search filter:", ev("""(function(){var e=document.getElementById('logoSearch'); e.value='docker';
  e.dispatchEvent(new Event('input',{bubbles:true}));
  var n=document.querySelectorAll('#logoGrid .logo-tile').length;
  e.value=''; e.dispatchEvent(new Event('input',{bubbles:true}));
  return {filtered:n, restored:document.querySelectorAll('#logoGrid .logo-tile').length};})()"""))
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
