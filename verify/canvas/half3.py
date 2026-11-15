import json,time,urllib.request,subprocess,tempfile
import websocket
PORT=9800
tmp=tempfile.mkdtemp(prefix="half3")
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

for w,h in [(1200,820),(1000,820),(900,800),(800,800),(700,800)]:
    cmd("Emulation.setDeviceMetricsOverride",width=w,height=h,deviceScaleFactor=1,mobile=False)
    cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html?cb="+str(time.time()))
    time.sleep(3.0)
    ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
    time.sleep(0.2)
    r = ev("""(function(){
      function label(e){var t=(e.getAttribute('data-name')||e.getAttribute('title')||'').trim();
        if(!t) t=(e.textContent||'').trim().slice(0,14);
        return (e.id?'#'+e.id:'')+(e.getAttribute('data-tool')?'['+e.getAttribute('data-tool')+']':'')+' '+t;}
      var out={vw:window.innerWidth, bars:{}};
      ['#editorBar','.topbar','#viewBar'].forEach(function(sel){
        var bar=document.querySelector(sel);
        if(!sel) return;
        if(!bar){out.bars[sel]='missing';return;}
        var b=bar.getBoundingClientRect();
        var kids=[].slice.call(bar.children).filter(function(k){
          var r=k.getBoundingClientRect(); var cs=getComputedStyle(k);
          return r.width>0&&r.height>0&&cs.display!=='none'&&cs.visibility!=='hidden';});
        var overlaps=[];
        for(var i=0;i<kids.length;i++)for(var j=i+1;j<kids.length;j++){
          var a=kids[i].getBoundingClientRect(),c2=kids[j].getBoundingClientRect();
          var ox=Math.min(a.right,c2.right)-Math.max(a.left,c2.left);
          if(ox>1) overlaps.push(label(kids[i])+' <> '+label(kids[j])+' ('+Math.round(ox)+'px)');
        }
        /* children whose text is wider than the button box */
        var clipped=kids.filter(function(k){
          if(!k.querySelector('.tool-text')) return false;
          return k.scrollWidth>k.clientWidth+1;}).map(function(k){return label(k)+' '+k.scrollWidth+'>'+k.clientWidth;});
        out.bars[sel]={x:Math.round(b.left),w:Math.round(b.width),scrollW:bar.scrollWidth,
                       clientW:bar.clientWidth,overlaps:overlaps.slice(0,6),clipped:clipped.slice(0,8)};
      });
      return out;})()""")
    print(w, json.dumps(r))
proc.terminate()
