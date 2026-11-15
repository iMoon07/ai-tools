import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9722
tmp=tempfile.mkdtemp(prefix="tpg")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=1400,900","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
    r=cmd("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1400,height=900,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html?cb="+str(time.time())); time.sleep(3.5)
ev("window.__errs=[];window.addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.3)
print('dblclicks seen:', ev("""(function(){window.__dc=0; var st=document.getElementById('stage');
  st.addEventListener('dblclick',function(){window.__dc++;},true); return 'ok';})()"""))
print('dispatch dblclick on edge path:',
  ev("""(function(){var p=document.querySelector('.alur-canvas-edge[data-edge="0"]'); if(!p) return 'no path';
    var r=p.getBoundingClientRect();
    p.dispatchEvent(new MouseEvent('dblclick',{bubbles:true,clientX:r.x+r.width/2,clientY:r.y+r.height/2}));
    return 'sent';})()"""))
time.sleep(0.5)
print('seen:', ev("window.__dc"))
print('editor:', ev("""(function(){var a=document.getElementById('inlineText');
  return {edge:window._editor.textEdit?window._editor.textEdit.edge:null, disp:a?a.style.display:null,
          focus:document.activeElement?document.activeElement.id:null, left:a?a.style.left:null, top:a?a.style.top:null};})()"""))
print('midpoint:', ev("""(function(){var p=document.querySelector('.alur-canvas-edge[data-edge="0"]');
  var pt=p.getPointAtLength(p.getTotalLength()/2); var m=p.getScreenCTM();
  return {x:m.a*pt.x+m.c*pt.y+m.e, y:m.b*pt.x+m.d*pt.y+m.f};})()"""))
print('errs', ev("window.__errs"))
c.close(); proc.terminate()
