import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9721
tmp=tempfile.mkdtemp(prefix="tpf")
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
    cmd("Input.dispatchMouseEvent",type=t,x=x,y=y,button=button,buttons=buttons,clickCount=clicks)
out={}
st=rect("#stage")
# click an existing arrow: Client(n1) -> API(n2)
path=ev("""(function(){var p=document.querySelector('.alur-canvas-edge[data-edge="0"]'); if(!p) return null;
  var pt=p.getPointAtLength(p.getTotalLength()/2); var m=p.getScreenCTM();
  return {x:m.a*pt.x+m.c*pt.y+m.e, y:m.b*pt.x+m.d*pt.y+m.f};})()""")
out['mid']=path
mouse("mousePressed",path["x"],path["y"]); mouse("mouseReleased",path["x"],path["y"],buttons=0)
time.sleep(0.3)
out['selected']=ev("({edge:window._state.spec.selectedEdge, node:window._state.spec.selected})")
# double click the arrow -> inline label editor
ev("""(function(){var p=document.querySelector('.alur-canvas-edge[data-edge="0"]');
  var r=p.getBoundingClientRect();
  p.dispatchEvent(new MouseEvent('dblclick',{bubbles:true,clientX:r.x+r.width/2,clientY:r.y+r.height/2}));})()""")
time.sleep(0.4)
out['editor']=ev("""(function(){var a=document.getElementById('inlineText');
  return {open:!!(window._editor.textEdit&&window._editor.textEdit.edge!=null), disp:a?a.style.display:null,
          focus:document.activeElement?document.activeElement.id:null, left:a?a.style.left:null, top:a?a.style.top:null};})()""")
cmd("Input.insertText",text="reads")
time.sleep(0.25)
cmd("Input.dispatchKeyEvent",type="keyDown",key="Enter",code="Enter",windowsVirtualKeyCode=13,nativeVirtualKeyCode=13)
cmd("Input.dispatchKeyEvent",type="keyUp",key="Enter",code="Enter",windowsVirtualKeyCode=13,nativeVirtualKeyCode=13)
time.sleep(0.5)
out['afterCommit']=ev("""(function(){var e=window._state.spec.edges[0];
  var g=document.querySelector('.alur-edge-label[data-edge="0"]');
  var t=g?g.querySelector('.alur-canvas-edge-label'):null;
  var plate=g?g.querySelector('.alur-canvas-edge-label-bg'):null;
  var bb=null; try{ bb=t?t.getBBox():null; }catch(err){}
  return {label:e.label, g:!!g, text:t?t.textContent:null, anchor:t?t.getAttribute('text-anchor'):null,
          fill:t?getComputedStyle(t).fill:null, plate:!!plate, plateFill:plate?getComputedStyle(plate).fill:null,
          bbox:bb?{x:Math.round(bb.x),y:Math.round(bb.y),w:Math.round(bb.width),h:Math.round(bb.height)}:null,
          errs:window.__errs};})()""")
# panel field reflects it, and edits it
out['panel']=ev("""(function(){var b=document.getElementById('shapePanelBody');
  var t=Array.prototype.slice.call(b.querySelectorAll('input[type=text]')).map(function(x){return x.value;});
  return {title:document.getElementById('shapePanelTitle').textContent, inputs:t};})()""")
ev("""(function(){var b=document.getElementById('shapePanelBody');
  var inp=Array.prototype.slice.call(b.querySelectorAll('input[type=text]')).filter(function(x){return x.value==='reads';})[0];
  if(!inp) return 'no input'; inp.value='writes'; inp.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})()""")
time.sleep(0.4)
out['panelEdit']=ev("""(function(){var e=window._state.spec.edges[0];
  var g=document.querySelector('.alur-edge-label[data-edge="0"]');
  return {label:e.label, text:g?g.querySelector('.alur-canvas-edge-label').textContent:null};})()""")
# remove
ev("""(function(){var b=Array.prototype.slice.call(document.querySelectorAll('#shapePanelBody button'))
  .filter(function(x){return (x.textContent||'').trim()==='Remove';})[0]; if(b) b.click();})()""")
time.sleep(0.4)
out['removed']=ev("""(function(){var e=window._state.spec.edges[0];
  return {label:e.label==null?null:e.label, g:!!document.querySelector('.alur-edge-label[data-edge="0"]')};})()""")
print(json.dumps(out, indent=1))
c.close(); proc.terminate()