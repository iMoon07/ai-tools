import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9623
tmp=tempfile.mkdtemp(prefix="tp")
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
    r=cmd("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)["result"]
    if r.get("subtype")=="error": return {"__err":r.get("description")}
    return r.get("value")
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1400,height=900,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.4)
# close docks
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.3)
# create text
ev("setTool('text');")
ev("""(function(){
  var st=document.getElementById('stage'); var r=st.getBoundingClientRect();
  var x=r.left+r.width/2, y=r.top+r.height/2;
  st.dispatchEvent(new PointerEvent('pointerdown',{clientX:x,clientY:y,button:0,buttons:1,pointerId:1,pointerType:'mouse',bubbles:true}));
  st.dispatchEvent(new PointerEvent('pointerup',{clientX:x,clientY:y,button:0,buttons:0,pointerId:1,pointerType:'mouse',bubbles:true}));
})();""")
time.sleep(0.4)
ev("""(function(){
  var a=document.getElementById('inlineText');
  if(a){a.value='Hello'; commitTextEdit();}
})();""")
time.sleep(0.4)
# select the text node
ev("""(function(){
  var ids=Object.keys(state.spec.nodes); var id=ids[ids.length-1];
  state.spec.selected=id; setSelection([id]); syncShapePanel();
  return id;
})()""")
time.sleep(0.3)
out = ev("""(function(){
  var p=document.getElementById('shapePanel');
  var b=document.getElementById('shapePanelBody');
  var t=document.getElementById('shapePanelTitle');
  var id=state.spec.selected; var n=state.spec.nodes[id];
  var btns=b?Array.from(b.querySelectorAll('button')).map(function(x){return x.textContent;}):[];
  var labels=b?Array.from(b.querySelectorAll('.shape-label')).map(function(x){return x.textContent;}):[];
  var ranges=b?Array.from(b.querySelectorAll('input[type="range"]')).length:0;
  var selects=b?Array.from(b.querySelectorAll('select')).length:0;
  return {hidden:p?p.hidden:null, title:t?t.textContent:null, isText:n&&n.isText, shape:n&&n.shape, btns:btns.slice(0,15), labels:labels, ranges:ranges, selects:selects, inspectorOpen:inspectorOpen, bodyText:b?(b.innerText||'').slice(0,200):null};
})()""")
print(json.dumps(out, indent=1))
c.close(); proc.terminate()
