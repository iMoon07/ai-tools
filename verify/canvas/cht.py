import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9532
tmp=tempfile.mkdtemp(prefix="cht")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=1600,1000","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
cmd("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.2)

def snap(tag):
    print(tag, ev("""(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec')||'{}');
      var out={nodes:[],cards:0,chartEls:document.querySelectorAll('.alur-chart-node').length,
        hint:/drag to move/.test(document.body.textContent)};
      Object.keys(s.nodes||{}).forEach(function(k){var n=s.nodes[k];
        out.nodes.push({id:k,shape:n.shape,module:n.module,ct:n.chartType,ds:n.dataSource,w:Math.round(n.w||0),h:Math.round(n.h||0)});
        if(n.shape==='module') out.cards++;});
      return out;})()"""))

snap("before   :")
ev("document.querySelector('[data-scene-module=\"chart\"]').click()"); time.sleep(1.0)
snap("after bar:")
print("quick:", ev("document.querySelectorAll('#chartQuickList .block-item').length"))
print("inspector title:", ev("(function(){var t=document.querySelector('#panelProperties b');return t?t.textContent:null;})()"))
print("fo html:", ev("""(function(){var fo=document.querySelector('.alur-chart-fo'); if(!fo) return null;
  var d=fo.querySelector('div'); var sp=d&&d.querySelector('[data-spec]');
  var svg=d&&d.querySelector('svg');
  return {spec:sp?sp.getAttribute('data-spec').slice(0,120):null, svg:!!svg,
    rects:svg?svg.querySelectorAll('rect').length:0, txt:svg?Array.prototype.map.call(svg.querySelectorAll('text'),function(t){return t.textContent;}).slice(0,6):[]};})()"""))
print("selected:", ev("document.getElementById('stage').getAttribute('data-selected')"))
print("resize handles:", ev("document.querySelectorAll('.alur-node.is-selected .alur-handle, .alur-node.is-selected [data-handle]').length"))
c.close(); proc.terminate()