import json,time,urllib.request,subprocess,tempfile,base64,io
import websocket
from PIL import Image
PORT=9798
tmp=tempfile.mkdtemp(prefix="half")
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

def load(w,h,mobile=False):
    cmd("Emulation.setDeviceMetricsOverride",width=w,height=h,deviceScaleFactor=1,mobile=mobile)
    cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html?cb="+str(time.time()))
    time.sleep(3.2)
    ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
    ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
    time.sleep(0.3)

def audit(label):
    r = ev("""(function(){
      var vw=window.innerWidth, out=[];
      document.querySelectorAll('body *').forEach(function(e){
        var b=e.getBoundingClientRect();
        if(b.width===0||b.height===0) return;
        if(b.right>vw+1||b.left<-1){
          var cs=getComputedStyle(e);
          if(cs.position==='fixed'||cs.visibility==='hidden'||cs.display==='none') return;
          out.push({sel:(e.id?'#'+e.id:'')+'.'+(e.className&&e.className.baseVal!==undefined?e.className.baseVal:e.className||''),
                    l:Math.round(b.left),r:Math.round(b.right),w:Math.round(b.width)});
        }
      });
      return {vw:vw, scrollW:document.documentElement.scrollWidth,
              bodyW:document.body.scrollWidth, over:out.slice(0,14), n:out.length,
              errs:window.__errs};})()""")
    print(label, json.dumps(r))
    return r

for w,h,mob in [(1400,900,False),(1100,820,False),(900,800,False),(760,800,False),(700,800,False),(600,800,True),(390,780,True)]:
    load(w,h,mob)
    audit("%dx%d%s" % (w,h," mobile" if mob else ""))
proc.terminate()
