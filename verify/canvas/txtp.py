import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9641
tmp=tempfile.mkdtemp(prefix="tp5")
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
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.3)
ev("""(function(){
  var st=document.getElementById('stage'); var r=st.getBoundingClientRect();
  var x=r.left+r.width/2, y=r.top+r.height/2;
  st.dispatchEvent(new PointerEvent('pointerdown',{clientX:x,clientY:y,button:0,buttons:1,pointerId:1,pointerType:'mouse',bubbles:true}));
  st.dispatchEvent(new PointerEvent('pointerup',{clientX:x,clientY:y,button:0,buttons:0,pointerId:1,pointerType:'mouse',bubbles:true}));
})();""")
time.sleep(0.5)
ev("""(function(){var a=document.getElementById('inlineText'); if(a){a.value='Hello'; a.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));}})()""")
time.sleep(0.5)
ev("""(function(){var S=window._S,id=Object.keys(S.spec.nodes)[0]; S.spec.selected=id; window._sync();})()""")
time.sleep(0.3)
out={}
out['panel']=ev("""(function(){var p=document.getElementById('shapePanel');var b=document.getElementById('shapePanelBody');var btns=Array.from(b.querySelectorAll('button')).map(function(x){return (x.textContent||'').trim();}); return {hidden:p.hidden,btns:btns,title:document.getElementById('shapePanelTitle').textContent};})()""")
# click B (bold)
out['boldClick']=ev("""(function(){var b=document.getElementById('shapePanelBody');var btn=Array.from(b.querySelectorAll('button')).find(function(x){return (x.textContent||'').trim()==='B';}); if(!btn) return 'no B'; btn.click(); return 'clicked';})()""")
time.sleep(0.4)
out['afterBold']=ev("""(function(){var id=window._S.spec.selected; var n=window._S.spec.nodes[id]; return {fw:n.fontWeight,fs:n.fontStyle,hidden:document.getElementById('shapePanel').hidden};})()""")
print(json.dumps(out, indent=1))
c.close(); proc.terminate()
