import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9653
tmp=tempfile.mkdtemp(prefix="la2")
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
ev("document.getElementById('themeToggle').click();")
time.sleep(0.4)
out = ev(r"""(function(){
  function rgba(s){ var m=s.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?/); return m?{r:+m[1],g:+m[2],b:+m[3],a:m[4]==null?1:+m[4]}:null; }
  function lum(c){ return c?(c.r+c.g+c.b)/3:null; }
  var bad=[], light=[];
  var sel='.dock,.dock *,.shape-panel,.shape-panel *,.tool-rail,.tool-rail *,.topbar,.topbar *,.zoom-bar,.zoom-bar *,#panelScene,#panelScene *,#panelAssets,#panelAssets *,#panelLayers,#panelLayers *';
  var els=document.querySelectorAll(sel);
  for(var i=0;i<els.length;i++){
    var el=els[i], cs=getComputedStyle(el); if(cs.display==='none'||cs.visibility==='hidden') continue;
    var bg=rgba(cs.backgroundColor);
    if(bg && bg.a>0.05 && lum(bg)<45){ var cls=(el.className||'').toString().slice(0,50); bad.push({tag:el.tagName,id:el.id||'',cls:cls,bg:cs.backgroundColor}); if(bad.length>=20) break; }
  }
  for(var i=0;i<els.length;i++){
    var el=els[i], cs=getComputedStyle(el); if(cs.display==='none'||cs.visibility==='hidden') continue;
    var fg=rgba(cs.color); var t=(el.innerText||'').trim();
    if(fg && fg.a>0.2 && lum(fg)>220 && t){ var cls=(el.className||'').toString().slice(0,50); light.push({tag:el.tagName,id:el.id||'',cls:cls,c:cs.color,t:t.slice(0,18)}); if(light.length>=20) break; }
  }
  return {bad:bad, light:light};
})()""")
print(json.dumps(out, indent=1))
c.close(); proc.terminate()
