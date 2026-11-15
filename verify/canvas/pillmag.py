import json,time,urllib.request,subprocess,tempfile
import websocket
PORT=9795
tmp=tempfile.mkdtemp(prefix="pill")
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
time.sleep(3.2)
print(json.dumps(ev("""(function(){
  function rrp(w,h,radius){
    var r=Math.max(0,Math.min(radius,Math.min(w,h)/2));
    return 'M '+r+' 0 L '+(w-r)+' 0 A '+r+' '+r+' 0 0 1 '+w+' '+r+
      ' L '+w+' '+(h-r)+' A '+r+' '+r+' 0 0 1 '+(w-r)+' '+h+
      ' L '+r+' '+h+' A '+r+' '+r+' 0 0 1 0 '+(h-r)+
      ' L 0 '+r+' A '+r+' '+r+' 0 0 1 '+r+' 0 Z';
  }
  function dev(d,w,h){
    var tmp=document.createElementNS('http://www.w3.org/2000/svg','path');
    tmp.setAttribute('d',d);
    var L=tmp.getTotalLength(),worst=0;
    for(var s=0;s<=L;s+=Math.max(1,L/200)){
      var pt=tmp.getPointAtLength(s);
      var dx=Math.max(-pt.x,pt.x-w,0),dy=Math.max(-pt.y,pt.y-h,0);
      var d2=Math.hypot(dx,dy); if(d2>worst) worst=d2;
    }
    return Math.round(worst*10)/10;
  }
  var g=window.rough.generator();
  var out={};
  [true,false].forEach(function(pv){
    var opts={roughness:1.8,bowing:1.35,seed:99,stroke:'#000',strokeWidth:1.5,
              fill:undefined,disableMultiStroke:false,preserveVertices:pv};
    var paths=g.toPaths(g.path(rrp(200,110,55),opts)).filter(function(p){return p&&p.d&&p.stroke!=='none';});
    out['pill_preserve_'+pv]=paths.map(function(p){return dev(p.d,200,110);});
    var paths2=g.toPaths(g.path(rrp(200,110,14),opts)).filter(function(p){return p&&p.d&&p.stroke!=='none';});
    out['round_preserve_'+pv]=paths2.map(function(p){return dev(p.d,200,110);});
  });
  return out;})()""")))
proc.terminate()
