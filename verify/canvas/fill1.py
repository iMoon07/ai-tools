import json,time,urllib.request,subprocess,tempfile
import websocket
PORT=9797
tmp=tempfile.mkdtemp(prefix="fill")
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
time.sleep(3.4)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
SPEC={"module":"canvas","nodes":{"a":{"x":200,"y":200,"w":200,"h":110,"text":"API","shape":"box"}},"edges":[]}
ev("""(function(){var box=document.getElementById('drawCode');
 box.value='```draw\\n'+JSON.stringify(%s,null,2)+'\\n```';
 document.getElementById('applyCode').click();})()""" % json.dumps(SPEC))
time.sleep(1.2)
def ptr(t,x,y,b=1,sel='#stage'):
    ev("""(function(){var s=document.querySelector(%s)||document.getElementById('stage');
      s.dispatchEvent(new PointerEvent(%s,{bubbles:true,cancelable:true,clientX:%f,clientY:%f,button:0,buttons:%d,pointerId:1,pointerType:'mouse',isPrimary:true}));})()""" % (json.dumps(sel),json.dumps(t),x,y,b))
def boxfill():
    return ev("""(function(){var n=document.querySelector('.alur-canvas-node .alur-node-box');
      return n?{fill:n.getAttribute('fill'), style:n.getAttribute('style')}:null;})()""")
print("before:", boxfill())
# pick a colour then use the fill tool
ev("document.querySelector('[data-tool=\\\"fill\\\"]').click()")
time.sleep(0.3)
print("tool:", ev("document.querySelector('.tool.is-on[data-tool]')?document.querySelector('.tool.is-on[data-tool]').getAttribute('data-tool'):null"))
NB = ev("(function(){var n=document.querySelector('.alur-canvas-node .alur-node-box');var b=n.getBoundingClientRect();return {x:b.x+b.width/2,y:b.y+b.height/2};})()")
print("node centre:", NB, "zoom:", ev("document.getElementById('zoomVal').textContent"))
ptr("pointerdown",NB["x"],NB["y"],sel="#stage")
ptr("pointerup",300,330,0)
time.sleep(0.8)
print("after fill click:", boxfill())
print("spec fill:", ev("(function(){var raw=JSON.parse(document.getElementById('drawCode').value.replace(/^```[a-zA-Z]*\\s*\\n/,'').replace(/\\n?```$/,''));return raw.nodes.a.fill||null;})()"))
# sticky
SPEC2={"module":"canvas","nodes":{"s":{"x":300,"y":300,"w":180,"h":180,"shape":"sticky","text":"hello"}},"edges":[]}
ev("""(function(){var box=document.getElementById('drawCode');
 box.value='```draw\\n'+JSON.stringify(%s,null,2)+'\\n```';
 document.getElementById('applyCode').click();})()""" % json.dumps(SPEC2))
time.sleep(1.2)
print("sticky:", json.dumps(ev("""(function(){
  var g=document.querySelector('[data-node-id="s"]');
  if(!g) return null;
  var body=g.querySelector('.alur-sticky');
  var txt=g.querySelector('.alur-node-label');
  return {bodyFill: body?body.getAttribute('fill'):null,
          bodyStyle: body?body.getAttribute('style'):null,
          textFill: txt?getComputedStyle(txt).fill:null,
          op: g.getAttribute('opacity')};})()""")))
print("errs:", ev("window.__errs"))
proc.terminate()
