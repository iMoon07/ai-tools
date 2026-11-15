import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9745
tmp=tempfile.mkdtemp(prefix="rau")
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
time.sleep(0.4)

ev("""(function(){
  var st=window._state; var S=st.spec;
  var defs=[
    ['arch','circle',120,120,264,88,'architect','#a5d8ff','solid'],
    ['art','circle',440,120,264,88,'artist','#a5d8ff','hachure'],
    ['cart','circle',760,120,264,88,'cartoonist','#a5d8ff','cross-hatch'],
    ['dia','diamond',120,260,264,150,'cartoonist','#ffec99','solid'],
    ['box','box',440,260,264,110,'artist','#b2f2bb','solid'],
    ['pill','pill',760,260,180,80,'cartoonist','#a5d8ff','solid'],
    ['round','box',980,260,200,90,'artist','#a5d8ff','solid']
  ];
  defs.forEach(function(d,k){
    S.nodes['a'+k]={id:'a'+k,shape:d[1],x:d[2],y:d[3],w:d[4],h:d[5],sloppiness:d[6],
      fill:d[7],fillStyle:d[8],color:'#1f2328',label:d[0],edge:'sharp'};
  });
  S.nodes['ar1']=Object.assign({},S.nodes['a6'],{id:'ar1',edge:'round'});
  window._render();
})()""")
time.sleep(1.0)

print(json.dumps(ev("""(function(){
  var out=[];
  document.querySelectorAll('.alur-canvas-node').forEach(function(el){
    var id=el.getAttribute('data-node-id');
    if (!/^a/.test(id)) return;
    var n=window._state.spec.nodes[id];
    var box=el.querySelector('.alur-node-box');
    var r=el.querySelectorAll('.alur-node-rough');
    var bb=null; try{ bb=r.length?r[0].getBBox():null; }catch(e){}
    out.push({id:id,shape:n.shape,slop:n.sloppiness,
      boxTag: box?box.tagName:null, boxFill: box?box.getAttribute('fill'):null,
      boxStroke: box?box.getAttribute('stroke'):null,
      rFill: r.length?r[0].getAttribute('fill'):null,
      rStroke: r.length?r[0].getAttribute('stroke'):null,
      rWidth: r.length?r[0].getAttribute('stroke-width'):null,
      subpaths: r.length?(r[0].getAttribute('d').match(/M/g)||[]).length:0,
      dlen: r.length?r[0].getAttribute('d').length:0,
      passes: r.length,
      bbox: bb?[Math.round(bb.x),Math.round(bb.y),Math.round(bb.width),Math.round(bb.height)]:null,
      want: [n.w,n.h]});
  });
  return out;})()"""), indent=1))
print('errs', ev("window.__errs"))
c.close(); proc.terminate()