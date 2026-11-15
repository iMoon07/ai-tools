import json,time,urllib.request,subprocess,tempfile
import websocket
PORT=9794
tmp=tempfile.mkdtemp(prefix="mag")
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
print(json.dumps(ev("""(function(){
  function dev(n){
    var r=AlurKit.nodeRough(n);
    if(!r) return null;
    return r.strokes.map(function(d){
      var tmp=document.createElementNS('http://www.w3.org/2000/svg','path');
      tmp.setAttribute('d',d);
      var L=tmp.getTotalLength(), worst=0, w=n.w, h=n.h, kind=n.shape;
      for(var s=0;s<=L;s+=Math.max(1,L/200)){
        var pt=tmp.getPointAtLength(s), d2;
        if(kind==='box'||kind==='pill'||kind==='round'){ var dx=Math.max(-pt.x,pt.x-w,0), dy=Math.max(-pt.y,pt.y-h,0); d2=Math.hypot(dx,dy); }
        else if(kind==='diamond'){ var q=Math.abs(pt.x-w/2)/(w/2)+Math.abs(pt.y-h/2)/(h/2); d2=Math.abs(q-1)*Math.min(w,h)/2; }
        else { var ex=(pt.x-w/2)/(w/2-2), ey=(pt.y-h/2)/(h/2-2); d2=Math.abs(Math.hypot(ex,ey)-1)*Math.min(w,h)/2; }
        if(d2>worst) worst=d2;
      }
      return Math.round(worst*10)/10;
    });
  }
  var out={};
  ['box','diamond','circle','pill'].forEach(function(k){
    [1,2].forEach(function(r){
      out[k+'_r'+r]=dev({id:'x',shape:k,w:200,h:110,sloppiness:"artist":"cartoonist"});
    });
  });
  return out;})()""")))
print("errs:", ev("window.__errs"))
proc.terminate()
