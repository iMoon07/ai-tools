import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9651
tmp=tempfile.mkdtemp(prefix="la")
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
# switch to light
ev("document.getElementById('themeToggle').click();")
time.sleep(0.4)
# open panels
ev("""(function(){
  ['scene','assets','layers','properties'].forEach(function(p){
    var btn=document.querySelector('[data-panel=\"'+p+'\"]'); if(btn) btn.click();
  });
})();""")
time.sleep(0.4)
# find dark backgrounds
out = ev(r"""(function(){
  function lum(rgb){
    var m = rgb.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
    if(!m) return null;
    return (+m[1]+ +m[2]+ +m[3])/3;
  }
  var bad=[];
  var els = document.querySelectorAll('.dock, .dock *, .shape-panel, .shape-panel *, .tool-rail, .tool-rail *, .topbar, .topbar *, .zoom-bar, .zoom-bar *, #shortcutCard, #shortcutCard *');
  for(var i=0;i<els.length && bad.length<40;i++){
    var el=els[i]; var cs=getComputedStyle(el);
    var bg=cs.backgroundColor; var l=lum(bg);
    if(l!==null && l<40 && cs.display!=='none' && el.offsetParent!==null){
      var cls=(el.className&&el.className.toString) ? el.className.toString().slice(0,60):'';
      bad.push({tag:el.tagName,id:el.id||'',cls:cls,bg:bg,l:Math.round(l)});
    }
  }
  var txt=[];
  for(var i=0;i<els.length && txt.length<25;i++){
    var el=els[i]; var cs=getComputedStyle(el);
    var c=cs.color; var l=lum(c);
    if(l!==null && l>220 && cs.display!=='none' && el.offsetParent!==null && (el.innerText||'').trim().length){
      var cls=(el.className&&el.className.toString) ? el.className.toString().slice(0,60):'';
      txt.push({tag:el.tagName,id:el.id||'',cls:cls,color:c,l:Math.round(l),t:(el.innerText||'').slice(0,20)});
    }
  }
  return {bad:bad, txt:txt};
})()""")
print(json.dumps(out, indent=1))
c.close(); proc.terminate()
