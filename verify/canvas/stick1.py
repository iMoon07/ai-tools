import json,time,urllib.request,subprocess,tempfile
import websocket
PORT=9802
tmp=tempfile.mkdtemp(prefix="st")
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
    i[0]+=1;c.send(json.dumps({"id":i[0],"method":m,"params":p}))
    while True:
        r=json.loads(c.recv())
        if r.get("id")==i[0]: return r.get("result",{})
def ev(e):
    r=cmd("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
cmd("Page.enable");cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1400,height=900,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html?cb="+str(time.time()))
time.sleep(3.3)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
SPEC={"module":"canvas","nodes":{"s":{"x":300,"y":300,"w":180,"h":180,"shape":"sticky","text":"hello"}},"edges":[]}
ev("""(function(){var box=document.getElementById('drawCode');
 box.value='```draw\\n'+JSON.stringify(%s,null,2)+'\\n```';
 document.getElementById('applyCode').click();})()""" % json.dumps(SPEC))
time.sleep(1.2)
NB=ev("(function(){var n=document.querySelector('.alur-canvas-node .alur-sticky');var b=n.getBoundingClientRect();return {x:b.x+b.width/2,y:b.y+b.height/2};})()")
ev("""(function(){var s=document.querySelector('.alur-canvas-node');
 s.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,clientX:%f,clientY:%f,button:0,buttons:1,pointerId:1,pointerType:'mouse'}));
 s.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,cancelable:true,clientX:%f,clientY:%f,button:0,buttons:0,pointerId:1,pointerType:'mouse'}));})()""" % (NB["x"],NB["y"],NB["x"],NB["y"]))
time.sleep(0.8)
print("panel:", json.dumps(ev("""(function(){
  var b=document.getElementById('shapePanelBody');
  return {title:document.getElementById('shapePanelTitle').textContent,
          sections:[].slice.call(b.querySelectorAll('.pp-cap')).map(function(e){return e.textContent.trim();}),
          actions:[].slice.call(b.querySelectorAll('.pp-acts button')).map(function(e){return e.getAttribute('title')||e.textContent.trim();})};})()""")))
print("rough before:", ev("document.querySelectorAll('[data-node-id=\\'s\\'] .alur-node-rough').length"))
# click cartoonist (3rd sloppiness segment in the sticky panel)
ev("""(function(){var secs=[].slice.call(document.querySelectorAll('#shapePanelBody .pp-sec'));
  var slop=secs.filter(function(s){return /Sloppiness/.test(s.textContent);})[0];
  var btns=[].slice.call(slop.querySelectorAll('button'));
  btns[btns.length-1].click();})()""")
time.sleep(0.9)
print("rough after:", ev("document.querySelectorAll('[data-node-id=\\'s\\'] .alur-node-rough').length"))
print("sticky stroke:", ev("(function(){var b=document.querySelector('[data-node-id=\\'s\\'] .alur-sticky');return b?b.getAttribute('stroke'):null;})()"))
print("spec slop:", ev("(function(){var raw=JSON.parse(document.getElementById('drawCode').value.replace(/^```[a-zA-Z]*\\s*\\n/,'').replace(/\\n?```$/,''));return raw.nodes.s.sloppiness||null;})()"))
print("errs:", ev("window.__errs"))
proc.terminate()
