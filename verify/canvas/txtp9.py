import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9711
tmp=tempfile.mkdtemp(prefix="tpe")
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

ST = """
(function(){
  var id = window.__nid;
  var n = window._state.spec.nodes[id];
  var el = document.querySelector('.alur-canvas-node[data-node-id="' + id + '"]');
  var lab = el ? el.querySelector('.alur-node-label') : null;
  var ts = lab ? lab.querySelectorAll('tspan') : [];
  var ys = []; for (var k = 0; k < ts.length; k++) ys.push(ts[k].getAttribute('y'));
  var bb = null; try { bb = lab ? lab.getBBox() : null; } catch (e) {}
  return {
    fontSize: n.fontSize, lineHeight: n.lineHeight, opacity: n.opacity,
    w: Math.round(n.w || 0), h: Math.round(n.h || 0),
    spans: ys, opacAttr: el ? el.getAttribute('opacity') : null,
    bbox: bb ? {w: Math.round(bb.width), h: Math.round(bb.height)} : null,
    label: n.label
  };
})()
"""
def state():
    return ev(ST)

st=rect("#stage"); px,py=st["x"]+st["w"]*0.35, st["y"]+st["h"]*0.55
ev("window._editor.tool='text'")
mouse("mousePressed",px,py); mouse("mouseReleased",px,py,buttons=0)
time.sleep(0.3)
cmd("Input.insertText",text="Hello")
time.sleep(0.2)
cmd("Input.dispatchKeyEvent",type="keyDown",key="Enter",code="Enter",windowsVirtualKeyCode=13,nativeVirtualKeyCode=13)
cmd("Input.dispatchKeyEvent",type="keyUp",key="Enter",code="Enter",windowsVirtualKeyCode=13,nativeVirtualKeyCode=13)
time.sleep(0.4)
nid=ev("(function(){var ns=window._state.spec.nodes; var ids=Object.keys(ns); for(var i=ids.length-1;i>=0;i--){ if(ns[ids[i]].isText) return ids[i]; } return null;})()")
ev("window.__nid=%s" % json.dumps(nid))
print("nid", nid, "base", json.dumps(state()))

def range_input(label, value):
    return ev("""(function(){var bs=Array.prototype.slice.call(document.querySelectorAll('#shapePanelBody input[type=range]'));
      var el=bs.filter(function(x){var l=x.parentNode.querySelector('.shape-label'); return l && l.textContent.indexOf(%s)===0;})[0];
      if(!el) return null; var old=el.value; el.value=String(%s); el.dispatchEvent(new Event('input',{bubbles:true}));
      return old + '->' + el.value;})()""" % (json.dumps(label), json.dumps(value)))

for lab, v in [("Line height", 2), ("Line height", 1), ("Opacity", 50), ("Line height", 1.25)]:
    r=range_input(lab, v); time.sleep(0.3)
    print(lab, v, "=>", r, json.dumps(state()))

ev("var n=window._state.spec.nodes[window.__nid]; n.label='one\\ntwo\\nthree'; window._render();")
time.sleep(0.3)
print("multiline", json.dumps(state()))
ev("""(function(){var b=Array.prototype.slice.call(document.querySelectorAll('#shapePanelBody button'))
  .filter(function(x){return (x.textContent||'').trim()==='XL';})[0]; if(b) b.click();})()""")
time.sleep(0.3)
print("XL", json.dumps(state()))
print("errs", ev("window.__errs"))
c.close(); proc.terminate()