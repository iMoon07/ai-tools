import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9691
tmp=tempfile.mkdtemp(prefix="tpc")
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
def rect(sel):
    return ev("(function(){var e=document.querySelector(%s); if(!e) return null; var r=e.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height};})()" % json.dumps(sel))
def mouse(t,x,y,buttons=1,button="left",clicks=1):
    cmd("Input.dispatchMouseEvent",type=t,x=x,y=y,button=button,buttons=buttons,clicks=clicks) if False else cmd("Input.dispatchMouseEvent",type=t,x=x,y=y,button=button,buttons=buttons,clickCount=clicks)
def drag(x0,y0,x1,y1,steps=6):
    mouse("mousePressed",x0,y0)
    for k in range(1,steps+1):
        mouse("mouseMoved",x0+(x1-x0)*k/steps,y0+(y1-y0)*k/steps)
        time.sleep(0.02)
    mouse("mouseReleased",x1,y1,buttons=0)
    time.sleep(0.25)
def snap():
    return ev("""(function(){var ns=window._state.spec.nodes; var ids=Object.keys(ns);
      return ids.map(function(k){var n=ns[k];return {id:k,shape:n.shape||'?',isText:!!n.isText,label:(n.label||'').slice(0,14),
        x:Math.round(n.x),y:Math.round(n.y),w:Math.round(n.w||0),h:Math.round(n.h||0),color:n.color||null};});})()""")
out={}
st=rect("#stage")
pts={'a':(st["x"]+st["w"]*0.22,st["y"]+st["h"]*0.30),'b':(st["x"]+st["w"]*0.45,st["y"]+st["h"]*0.30),
     'c':(st["x"]+st["w"]*0.22,st["y"]+st["h"]*0.62),'d':(st["x"]+st["w"]*0.45,st["y"]+st["h"]*0.62)}
out['start']=snap()
for tool in ['box','diamond','circle','draw']:
    ev("window._editor.tool=%s" % json.dumps(tool))
    drag(pts['a'][0],pts['a'][1],pts['b'][0],pts['b'][1])
    out[tool]={'nodes':snap(),'tool':ev("window._editor.tool"),'errs':ev("window.__errs")}
    ev("window._editor.tool='select'")
# arrow between two fresh nodes
ev("window._editor.tool='box'"); drag(pts['c'][0],pts['c'][1],pts['c'][0]+140,pts['c'][1]+80)
ev("window._editor.tool='select'")
ns=ev("window._state.spec.nodes"); ids=list(ns.keys())
last=ids[-1]
r=ev("""(function(){var el=document.querySelector('.alur-canvas-node[data-node-id=%s]'); var b=el.getBoundingClientRect();
  return {x:b.x+b.width/2,y:b.y+b.height/2};})()""" % json.dumps(last))
out['rectNode']=r
ev("window._editor.tool='arrow'")
drag(r["x"],r["y"],pts['a'][0]+20,pts['a'][1]+20)
out['arrow']={'edges':ev("(window._state.spec.edges||[]).length"),'nodes':len(ev("window._state.spec.nodes")),'tool':ev("window._editor.tool"),'errs':ev("window.__errs")}
ev("window._editor.tool='select'")
# text tool create + type + colour pick, then check rendered colour on canvas
ev("window._editor.tool='text'")
drag(pts['d'][0],pts['d'][1],pts['d'][0]+1,pts['d'][1]+1,steps=2)
time.sleep(0.3)
cmd("Input.insertText",text="green?")
time.sleep(0.3)
out['textEdit']={'open':ev("!!window._editor.textEdit"),'val':ev("(function(){var a=document.getElementById('inlineText');return a?a.value:null;})()")}
# pick the swatch titled '#2ea043'-ish: list swatch colours available
out['swatches']=ev("""(function(){var p=document.getElementById('shapePanel');
  return Array.prototype.slice.call(p.querySelectorAll('.swatch')).map(function(b){return b.dataset.color;});})()""")
pick=ev("""(function(){var p=document.getElementById('shapePanel');
  var b=Array.prototype.slice.call(p.querySelectorAll('.swatch')).filter(function(x){return /green|2ea043|3fb950/i.test(x.dataset.color||'');})[0];
  if(!b) return null; b.click(); return b.dataset.color;})()""")
time.sleep(0.4)
out['picked']=pick
out['afterPick']=ev("""(function(){var a=document.getElementById('inlineText'); var ns=window._state.spec.nodes;
  var ids=Object.keys(ns); var n=ns[ids[ids.length-1]];
  return {open:!!window._editor.textEdit, ta:a?a.value:null, color:n.color, style:n.color?getComputedStyle(a).color:null, errs:window.__errs};})()""")
cmd("Input.insertText",text="Z")
time.sleep(0.2)
cmd("Input.dispatchKeyEvent",type="keyDown",key="Enter",code="Enter",windowsVirtualKeyCode=13,nativeVirtualKeyCode=13)
cmd("Input.dispatchKeyEvent",type="keyUp",key="Enter",code="Enter",windowsVirtualKeyCode=13,nativeVirtualKeyCode=13)
time.sleep(0.4)
out['final']=ev("""(function(){var ns=window._state.spec.nodes; var ids=Object.keys(ns); var n=ns[ids[ids.length-1]];
  var el=document.querySelector('.alur-canvas-node[data-node-id=\\''+ids[ids.length-1]+'\\']');
  var lab=el?el.querySelector('.alur-node-label'):null;
  return {label:n.label, color:n.color, fillAttr:lab?lab.getAttribute('fill'):null, computedLab:lab?getComputedStyle(lab).fill:null,
          bodyBg:getComputedStyle(document.body).backgroundColor, errs:window.__errs};})()""")
print(json.dumps(out, indent=1))
c.close(); proc.terminate()