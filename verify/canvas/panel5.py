import json,time,urllib.request,subprocess,tempfile
import websocket
PORT=9784
tmp=tempfile.mkdtemp(prefix="pn")
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
print("toolbar order:", ev("""(function(){
  var bar=document.getElementById('inspectorToggle').parentNode;
  return [].slice.call(bar.children).filter(function(c){return c.tagName==='BUTTON';})
    .map(function(b){return b.getAttribute('data-panel')||b.id||b.textContent.trim().slice(0,6);});})()"""))
print("in viewbar:", ev("!!document.querySelector('#viewBar #inspectorToggle')"))
def css(sel, prop):
    return ev("""(function(){var e=document.querySelector(%s);return e?getComputedStyle(e)[%s]:null;})()""" % (json.dumps(sel), json.dumps(prop)))
print("shape bg:", css('#shapePanel','backgroundColor'), "radius:", css('#shapePanel','borderRadius'))
print("assets bg:", css('#panelAssets','backgroundColor'), "radius:", css('#panelAssets','borderRadius'))
print("initial:", ev("(function(){var p=document.getElementById('shapePanel');return {hidden:p.hidden,on:document.getElementById('inspectorToggle').classList.contains('is-on')};})()"))
print("btn w/h:", ev("""(function(){var b=document.getElementById('inspectorToggle');var a=b.parentNode.querySelector('[data-panel="assets"]');
 var r=b.getBoundingClientRect(),q=a.getBoundingClientRect();
 return {props:[Math.round(r.width),Math.round(r.height)],assets:[Math.round(q.width),Math.round(q.height)],
         sameRow: Math.abs(r.top-q.top)<2, gap: Math.round(r.left-q.right)};})()"""))
# click it -> panel opens
ev("document.getElementById('inspectorToggle').click()")
print("  aria:", ev("document.getElementById('inspectorToggle').getAttribute('aria-pressed')"))
time.sleep(0.6)
print("open after click:", ev("""(function(){var p=document.getElementById('shapePanel');
 return {hidden:p.hidden, on:document.getElementById('inspectorToggle').classList.contains('is-on')};})()"""))
ev("document.getElementById('inspectorToggle').click()")
time.sleep(0.6)
print("closed after 2nd:", ev("document.getElementById('shapePanel').hidden"))
for _ in range(3):
    if ev("document.getElementById('inspectorToggle').getAttribute('aria-pressed')") == 'true': break
    ev("document.getElementById('inspectorToggle').click()")
    time.sleep(0.4)
print("aria before select:", ev("document.getElementById('inspectorToggle').getAttribute('aria-pressed')"))
# select a node and confirm the panel fills
ev("document.querySelector('[data-tool=\"box\"]').click()")
def ptr(t, x, y, b=1):
    ev("""(function(){var s=document.getElementById('stage');
      s.dispatchEvent(new PointerEvent(%s,{bubbles:true,cancelable:true,clientX:%f,clientY:%f,button:0,buttons:%d,pointerId:1,pointerType:'mouse',isPrimary:true}));})()""" % (json.dumps(t), x, y, b))
ST = ev("(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y};})()")
ptr("pointerdown", ST['x']+200, ST['y']+200)
for k in range(1,11):
    ptr("pointermove", ST['x']+200+18*k, ST['y']+200+6*k)
ptr("pointerup", ST['x']+380, ST['y']+260, 0)
time.sleep(0.6)
ev("(function(){var b=document.querySelector('[data-tool=\"select\"]');if(b)b.click();})()")
time.sleep(0.3)
ptr("pointerdown", ST['x']+290, ST['y']+230)
ptr("pointerup", ST['x']+290, ST['y']+230, 0)
time.sleep(0.8)
print("nodes:", ev("document.querySelectorAll('.alur-canvas-node').length"))
print("selected:", ev("document.querySelectorAll('.alur-canvas-node.is-selected').length"), "aria:", ev("document.getElementById('inspectorToggle').getAttribute('aria-pressed')"))
print("inspector:", ev("""(function(){var p=document.getElementById('shapePanel');
 return {hidden:p.hidden, title:document.getElementById('shapePanelTitle').textContent,
   btns:p.querySelectorAll('.pp-btn').length, swatch:p.querySelectorAll('.pp-dot').length};})()"""))
print("sections:", ev("[].slice.call(document.querySelectorAll('#shapePanelBody .pp-cap')).map(function(e){return e.textContent.trim();})"))
print("controls:", ev("(function(){var b=document.getElementById('shapePanelBody');return {btn:b.querySelectorAll('button').length,seg:b.querySelectorAll('.pp-seg').length,sw:b.querySelectorAll('.pp-dot').length,sl:b.querySelectorAll('input[type=range]').length,txt:b.querySelectorAll('input[type=text],input[type=number]').length};})()"))
print("errs:", ev("window.__errs"))
proc.terminate()
