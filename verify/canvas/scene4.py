import json, sys, time, urllib.request, subprocess, tempfile
import websocket
PORT=int(sys.argv[1]); W=int(sys.argv[2]); H=int(sys.argv[3])
tmp=tempfile.mkdtemp(prefix="s4")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=%d,%d"%(W,H),"about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
    if r.get("subtype")=="error": print("JS ERROR:",r.get("description"))
    return r.get("value")
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=W<600)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")

print("viewport", W, H)
print("block items:", ev("""(function(){var h=document.getElementById('blockList');
 if(!h) return 'MISSING';
 return Array.prototype.map.call(h.querySelectorAll('.block-item'),function(b){
   return b.querySelector('.blk-no').textContent+' '+b.querySelector('b').textContent;});})()"""))
print("plus signs left:", ev("(document.body.innerText.match(/＋/g)||[]).length"))
print("chartSection hidden (no sel):", ev("document.getElementById('chartSection').hidden"))

# open Scene panel and click Chart block
ev("document.querySelector('[data-panel=\"scene\"]').click()"); time.sleep(0.5)
ev("document.querySelector('#blockList [data-scene-module=\"chart\"]').click()"); time.sleep(1.0)
print("after add chart -> chart nodes:", ev("(function(){var n=0;document.querySelectorAll('#stage .alur-canvas-node').forEach(function(e){n++});return n;})()"))
print("chartSection hidden (chart selected):", ev("document.getElementById('chartSection').hidden"))
print("chart head:", ev("(function(){var s=document.getElementById('chartSection');return s.querySelector('.scene-step-head').innerText.replace(/\\n/g,' | ');})()"))
print("chartType value:", ev("document.getElementById('chartType').value"))
def spec():
    return ev("JSON.parse(document.getElementById('stage').getAttribute('data-spec')||'{}')")
print("selected:", spec().get('selected'))

# change type -> must NOT replace the scene
before = ev("(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));return {nodes:Object.keys(s.nodes||{}).length, mod:s.module, sel:s.selected};})()")
ev("""(function(){var s=document.getElementById('chartType');s.value='donut';
 s.dispatchEvent(new Event('change',{bubbles:true}));return 1;})()""")
time.sleep(0.9)
after = ev("(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));return {nodes:Object.keys(s.nodes||{}).length, mod:s.module, sel:s.selected};})()")
print("before type change:", before)
print("after  type change:", after)
print("block chartType:", ev("(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));var n=s.nodes[s.selected];return n?n.chartType:'none';})()"))
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
