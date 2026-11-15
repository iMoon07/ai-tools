import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9761
tmp=tempfile.mkdtemp(prefix="tpl")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=1400,900","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
for _ in range(80):
    try:
        urllib.request.urlopen("http://127.0.0.1:%d/json/version"%PORT,timeout=1).read(); break
    except Exception: time.sleep(0.25)
tabs=json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json"%PORT).read())
page=[t for t in tabs if t["type"]=="page"][0]
c=websocket.create_connection(page["webSocketDebuggerUrl"],timeout=30); i=[0]
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
errs=ev("(function(){window.__errs=[];window.addEventListener('error',function(e){window.__errs.push(String(e.message));});return 1;})()")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();})")
time.sleep(0.3)
def rect(sel):
    return ev("(function(){var e=document.querySelector(%s); if(!e) return null; var r=e.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height};})()" % json.dumps(sel))
def mouse(t,x,y,buttons=1,button="left",clicks=1):
    cmd("Input.dispatchMouseEvent",type=t,x=x,y=y,button=button,buttons=buttons,clickCount=clicks)
out={}
# 1. text via the text tool
st=rect("#stage"); px,py=st["x"]+st["w"]*0.3, st["y"]+st["h"]*0.7
ev("(function(){var b=document.querySelector('[data-tool=text]'); b.click();})()")
time.sleep(0.2)
mouse("mousePressed",px,py); mouse("mouseReleased",px,py,buttons=0)
time.sleep(0.3)
cmd("Input.insertText",text="Sized")
time.sleep(0.2)
cmd("Input.dispatchKeyEvent",type="keyDown",key="Enter",code="Enter",windowsVirtualKeyCode=13,nativeVirtualKeyCode=13)
cmd("Input.dispatchKeyEvent",type="keyUp",key="Enter",code="Enter",windowsVirtualKeyCode=13,nativeVirtualKeyCode=13)
time.sleep(0.4)
# select it and press XL + B
node=ev("""(function(){var els=document.querySelectorAll('.alur-canvas-node'); var last=els[els.length-1];
  var r=last.getBoundingClientRect();
  last.dispatchEvent(new PointerEvent('pointerdown',{clientX:r.x+r.width/2,clientY:r.y+r.height/2,button:0,buttons:1,pointerId:1,pointerType:'mouse',bubbles:true}));
  last.dispatchEvent(new PointerEvent('pointerup',{clientX:r.x+r.width/2,clientY:r.y+r.height/2,button:0,buttons:0,pointerId:1,pointerType:'mouse',bubbles:true}));
  return last.getAttribute('data-node-id');})()""")
time.sleep(0.5)
def clickbtn(label):
    return ev("""(function(){var b=Array.prototype.slice.call(document.querySelectorAll('#shapePanelBody button'))
      .filter(function(x){return (x.textContent||'').trim()===%s;})[0]; if(!b) return null; b.click(); return 'ok';})()""" % json.dumps(label))
out['XL']=clickbtn('XL'); time.sleep(0.3)
out['B']=clickbtn('B'); time.sleep(0.3)
out['label']=ev("""(function(){var el=document.querySelector('.alur-canvas-node[data-node-id="%s"]');
  var l=el?el.querySelector('.alur-node-label'):null; var cs=l?getComputedStyle(l):null;
  return {text:l?l.textContent:null, size:cs?cs.fontSize:null, weight:cs?cs.fontWeight:null, family:cs?(cs.fontFamily||'').split(',')[0]:null};})()""" % node)
# 2. arrow label through the draw code block
code = ev("(function(){var t=document.getElementById('drawCode'); return t?t.value.slice(0,80):null;})()")
out['codeHead']=code
# 2. arrow label through the draw code block (JSON spec), applied in one go
out['applyRes']=ev("""(function(){
  var t=document.getElementById('drawCode');
  var raw=t.value.replace(/^```[a-z]*\\s*/i,'').replace(/```\\s*$/,'');
  var spec=JSON.parse(raw);
  if(!spec.edges[0]) return {err:'no edges'};
  spec.edges[0].label='reads';
  t.value='```draw\\n'+JSON.stringify(spec,null,2)+'\\n```';
  var b=document.getElementById('applyCode');
  b.click();
  return {clicked:true};
})()""")
time.sleep(0.8)
out['edgeLabel']=ev("""(function(){var g=document.querySelector('.alur-edge-label');
  if(!g) return {present:false};
  var t=g.querySelector('.alur-canvas-edge-label');
  var plate=g.querySelector('.alur-canvas-edge-label-bg');
  return {present:true, text:t?t.textContent:null, anchor:t?t.getAttribute('text-anchor'):null,
          fill:t?getComputedStyle(t).fill:null, plate:!!plate, plateFill:plate?getComputedStyle(plate).fill:null,
          edges:document.querySelectorAll('.alur-canvas-edge').length};})()""")

# 3. typing in the centre-label field must not lose focus
mid = ev("""(function(){var p=document.querySelector('.alur-canvas-edge[data-edge="0"]');
  if(!p) return null; var pt=p.getPointAtLength(p.getTotalLength()/2); var m=p.getScreenCTM();
  return {x:m.a*pt.x+m.c*pt.y+m.e, y:m.b*pt.x+m.d*pt.y+m.f};})()""")
if mid:
    ev("""(function(){var p=document.querySelector('.alur-canvas-edge[data-edge="0"]');
      var r=p.getBoundingClientRect();
      p.dispatchEvent(new MouseEvent('dblclick',{bubbles:true,clientX:r.x+r.width/2,clientY:r.y+r.height/2}));})()""")
    time.sleep(0.4)
    out['dblclickEditor']=ev("(function(){var a=document.getElementById('inlineText'); return {open:!!a&&a.style.display==='block', val:a?a.value:null};})()")
    cmd("Input.dispatchKeyEvent",type="keyDown",key="Escape",code="Escape",windowsVirtualKeyCode=27,nativeVirtualKeyCode=27)
    time.sleep(0.3)
    ev("""(function(){var b=document.getElementById('shapePanelBody');
      var inp=Array.prototype.slice.call(b.querySelectorAll('input[type=text]')).filter(function(x){return x.value==='reads';})[0];
      if(!inp) return false; inp.focus(); return true;})()""")
    time.sleep(0.2)
    cmd("Input.insertText",text="!")
    time.sleep(0.4)
    out['panelTyping']=ev("""(function(){var b=document.getElementById('shapePanelBody');
      var inp=Array.prototype.slice.call(b.querySelectorAll('input[type=text]')).filter(function(x){return (x.value||'').indexOf('reads')===0;})[0];
      var g=document.querySelector('.alur-edge-label');
      return {value:inp?inp.value:null, focused:document.activeElement===inp,
              canvasLabel:g?(g.querySelector('.alur-canvas-edge-label')||{}).textContent:null};})()""")
out['errs']=ev("window.__errs")
print(json.dumps(out, indent=1))
c.close(); proc.terminate()
