import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9671
tmp=tempfile.mkdtemp(prefix="tpa")
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

def mouse(t,x,y,buttons=1,button="left",clicks=1):
    cmd("Input.dispatchMouseEvent",type=t,x=x,y=y,button=button,buttons=buttons,clickCount=clicks)

def rect(sel):
    return ev("(function(){var e=document.querySelector(%s); if(!e) return null; var r=e.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height};})()" % json.dumps(sel))

out={}
st=rect("#stage"); cx=st["x"]+st["w"]*0.5; cy=st["y"]+st["h"]*0.5

# --- A: real click with text tool on empty canvas
ev("window._editor.tool='text'")
mouse("mousePressed",cx,cy); mouse("mouseReleased",cx,cy,buttons=0)
time.sleep(0.4)
out['A_textToolClick']=ev("""(function(){var a=document.getElementById('inlineText');
 return {open:!!(window._editor.textEdit), disp:a?a.style.display:null, focus:document.activeElement?document.activeElement.id:null};})()""")
cmd("Input.insertText",text="real")
time.sleep(0.3)
out['A_typed']=ev("""(function(){var a=document.getElementById('inlineText');
 return {ta:a?a.value:null, open:!!(window._editor.textEdit)};})()""")
# commit with Enter key (real key event)
cmd("Input.dispatchKeyEvent",type="keyDown",key="Enter",code="Enter",windowsVirtualKeyCode=13,nativeVirtualKeyCode=13)
cmd("Input.dispatchKeyEvent",type="keyUp",key="Enter",code="Enter",windowsVirtualKeyCode=13,nativeVirtualKeyCode=13)
time.sleep(0.4)
out['A_committed']=ev("""(function(){var a=document.getElementById('inlineText'); var ns=window._state.spec.nodes;
 var ids=Object.keys(ns); var n=ns[ids[ids.length-1]];
 return {open:!!(window._editor.textEdit), disp:a?a.style.display:null, label:n?n.label:null, count:ids.length, errs:window.__errs};})()""")

# --- B: double click the created node with selection tool
ev("window._editor.tool='select'")
n=ev("""(function(){var ns=window._state.spec.nodes; var ids=Object.keys(ns); var n=ns[ids[ids.length-1]];
 var el=document.querySelector('.alur-canvas-node[data-node-id=\\''+ids[ids.length-1]+'\\']');
 if(!el) return null; var r=el.getBoundingClientRect(); return {x:r.x+r.width/2,y:r.y+r.height/2,w:r.width,h:r.height};})()""")
out['B_nodeRect']=n
if n:
    mouse("mousePressed",n["x"],n["y"],clicks=1); mouse("mouseReleased",n["x"],n["y"],buttons=0,clicks=1)
    mouse("mousePressed",n["x"],n["y"],clicks=2); mouse("mouseReleased",n["x"],n["y"],buttons=0,clicks=2)
    time.sleep(0.4)
    out['B_dblclick']=ev("""(function(){var a=document.getElementById('inlineText');
     return {open:!!(window._editor.textEdit), disp:a?a.style.display:null, ta:a?a.value:null, focus:document.activeElement?document.activeElement.id:null, sel:window._state.spec.selected||null, errs:window.__errs};})()""")
    cmd("Input.insertText",text="!")
    time.sleep(0.3)
    out['B_typed']=ev("""(function(){var a=document.getElementById('inlineText'); return {ta:a?a.value:null, open:!!(window._editor.textEdit)};})()""")

# --- C: while editing, click a panel colour swatch (real mouse)
p=rect("#shapePanel")
out['C_panel']=p
sw=ev("""(function(){var p=document.getElementById('shapePanel');
 var b=Array.prototype.slice.call(p.querySelectorAll('.swatch')).filter(function(x){return x.dataset.color&&x.dataset.color.toLowerCase()!=='transparent';});
 if(!b.length) return null; var r=b[0].getBoundingClientRect(); return {x:r.x+r.width/2,y:r.y+r.height/2,color:b[0].dataset.color};})()""")
out['C_swatch']=sw
if sw:
    mouse("mousePressed",sw["x"],sw["y"]); mouse("mouseReleased",sw["x"],sw["y"],buttons=0)
    time.sleep(0.4)
    out['C_afterSwatch']=ev("""(function(){var a=document.getElementById('inlineText'); var ns=window._state.spec.nodes;
     var ids=Object.keys(ns); var n=ids.length?ns[ids[ids.length-1]]:null;
     return {open:!!(window._editor.textEdit), ta:a?a.value:null, disp:a?a.style.display:null, color:n?n.color:null,
             focus:document.activeElement?document.activeElement.id:null, errs:window.__errs};})()""")
    cmd("Input.insertText",text="?")
    time.sleep(0.3)
    out['C_typedAfter']=ev("""(function(){var a=document.getElementById('inlineText'); return {ta:a?a.value:null, open:!!(window._editor.textEdit), disp:a?a.style.display:null};})()""")

# --- D: escape cancels
cmd("Input.dispatchKeyEvent",type="keyDown",key="Escape",code="Escape",windowsVirtualKeyCode=27,nativeVirtualKeyCode=27)
time.sleep(0.3)
out['D_escape']=ev("""(function(){var a=document.getElementById('inlineText'); var ns=window._state.spec.nodes;
 var ids=Object.keys(ns); var n=ids.length?ns[ids[ids.length-1]]:null;
 return {open:!!(window._editor.textEdit), disp:a?a.style.display:null, label:n?n.label:null, errs:window.__errs};})()""")

# --- E: box select tools sanity (rect/arrow/draw)
for tool in ['rect','arrow','draw','ellipse']:
    ev("window._editor.tool=%s" % json.dumps(tool))
    x0,y0=cx-120,cy-60
    mouse("mousePressed",x0,y0); mouse("mouseMoved",x0+120,y0+60,buttons=1)
    mouse("mouseMoved",x0+140,y0+70,buttons=1); mouse("mouseReleased",x0+140,y0+70,buttons=0)
    time.sleep(0.3)
    out['E_'+tool]=ev("""(function(){var ns=window._state.spec.nodes; var ids=Object.keys(ns);
      var last=ids.length?ns[ids[ids.length-1]]:null;
      return {count:ids.length, kind:last?last.shape||last.kind||'?':null, tool:window._editor.tool, errs:window.__errs};})()""")
ev("window._editor.tool='select'")
print(json.dumps(out, indent=1))
c.close(); proc.terminate()