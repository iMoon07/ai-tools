import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9661
tmp=tempfile.mkdtemp(prefix="tp8")
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
    r=cmd("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": return {"__err":res.get("description")}
    return res.get("value")
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1400,height=900,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html?cb="+str(time.time())); time.sleep(3.5)
out={}
out['errs']=[]
ev("window.__errs=[];window.addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.3)
ev("window._editor.tool='text'")
ev("""(function(){
  var st=document.getElementById('stage'); var r=st.getBoundingClientRect();
  var x=r.left+r.width*0.45, y=r.top+r.height*0.45;
  st.dispatchEvent(new PointerEvent('pointerdown',{clientX:x,clientY:y,button:0,buttons:1,pointerId:1,pointerType:'mouse',bubbles:true}));
  st.dispatchEvent(new PointerEvent('pointerup',{clientX:x,clientY:y,button:0,buttons:0,pointerId:1,pointerType:'mouse',bubbles:true}));
})();""")
time.sleep(0.4)
out['editOpen']=ev("""(function(){var a=document.getElementById('inlineText');return {has:!!a, editing:!!(window._editor.textEdit), disp:a?a.style.display:null, focus:document.activeElement?document.activeElement.id:null};})()""")
# real typing via CDP
ev("document.getElementById('inlineText').focus();")
cmd("Input.insertText",text="hello")
time.sleep(0.4)
out['typed']=ev("""(function(){var a=document.getElementById('inlineText');
  var ids=Object.keys(window._state.spec.nodes); var n=ids.length?window._state.spec.nodes[ids[ids.length-1]]:null;
  return {ta:a?a.value:null, editing:!!(window._editor.textEdit), label:n?n.label:null, disp:a?a.style.display:null, focus:document.activeElement?document.activeElement.id:null};})()""")
# now click a text-colour swatch in the shape panel while editing
out['swatch']=ev("""(function(){
  var p=document.getElementById('shapePanel');
  if(!p) return {panel:false};
  var b=Array.prototype.slice.call(p.querySelectorAll('.swatch')).filter(function(x){return x.dataset.color && x.dataset.color.toLowerCase()!=='transparent';});
  return {panel:true, open:p.className, n:b.length, first:b.length?b[0].dataset.color:null};
})()""")
ev("""(function(){var p=document.getElementById('shapePanel');
  var b=Array.prototype.slice.call(p.querySelectorAll('.swatch')).filter(function(x){return x.dataset.color && x.dataset.color.toLowerCase()!=='transparent';})[0];
  if(b) b.click(); })();""")
time.sleep(0.4)
out['afterSwatch']=ev("""(function(){var a=document.getElementById('inlineText');
  var ids=Object.keys(window._state.spec.nodes); var n=ids.length?window._state.spec.nodes[ids[ids.length-1]]:null;
  return {ta:a?a.value:null, editing:!!(window._editor.textEdit), label:n?n.label:null, color:n?n.color:null, disp:a?a.style.display:null, focus:document.activeElement?document.activeElement.id:null, errs:window.__errs};})()""")
# keep typing after the swatch click
ev("document.getElementById('inlineText').focus();")
cmd("Input.insertText",text="XY")
time.sleep(0.4)
out['afterMore']=ev("""(function(){var a=document.getElementById('inlineText');
  var ids=Object.keys(window._state.spec.nodes); var n=ids.length?window._state.spec.nodes[ids[ids.length-1]]:null;
  return {ta:a?a.value:null, editing:!!(window._editor.textEdit), label:n?n.label:null, disp:a?a.style.display:null, focus:document.activeElement?document.activeElement.id:null, errs:window.__errs};})()""")
print(json.dumps(out, indent=1))
c.close(); proc.terminate()