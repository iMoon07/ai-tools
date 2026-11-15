import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9753
tmp=tempfile.mkdtemp(prefix="rdp")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=1200,900","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
cmd("Emulation.setDeviceMetricsOverride",width=1200,height=900,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/read.html?cb="+str(time.time())); time.sleep(3.0)
ev("window.__errs=[];window.addEventListener('error',function(e){window.__errs.push(String(e.message));});")
print(json.dumps(ev("""(function(){
  var spec={module:'canvas',title:'reader check',grid:false,width:900,height:520,
    nodes:{
      a:{id:'a',shape:'circle',x:60,y:60,w:300,h:100,label:'oval',color:'#1971c2',fill:'#a5d8ff',sloppiness:'cartoonist',fillStyle:'solid'},
      b:{id:'b',shape:'diamond',x:60,y:220,w:220,h:130,label:'pick',color:'#e03131',fill:'#ffc9c9',sloppiness:'artist',fillStyle:'hachure'},
      c:{id:'c',shape:'box',x:340,y:220,w:200,h:100,label:'box',color:'#2f9e44',fill:'#b2f2bb',sloppiness:'architect'}
    },
    edges:[{from:'a',to:'b',label:'x'},{from:'b',to:'c',elbow:true,arrowType:'triangle'}],
    selected:null,selectedEdge:null,zoom:1,panX:0,panY:0};
  var d=document.createElement('div');
  d.className='alur draw';
  d.setAttribute('data-spec', JSON.stringify(spec));
  document.body.appendChild(d);
  var h=window.Alur.mount(d);
  var svg=d.querySelector('svg');
  return {nodes:svg.querySelectorAll('.alur-canvas-node').length,
          edges:svg.querySelectorAll('.alur-canvas-edge').length,
          rough:svg.querySelectorAll('.alur-node-rough').length,
          ellipses:svg.querySelectorAll('ellipse.alur-node-box').length,
          vb:svg.getAttribute('viewBox'),
          size:[Math.round(d.getBoundingClientRect().width), Math.round(d.getBoundingClientRect().height)]};
})()""")))
time.sleep(0.5)
print('errs', ev("window.__errs"))
c.close(); proc.terminate()