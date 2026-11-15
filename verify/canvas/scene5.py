import json, sys, time, urllib.request, subprocess, tempfile
import websocket
PORT=int(sys.argv[1]); W=int(sys.argv[2]); H=int(sys.argv[3])
tmp=tempfile.mkdtemp(prefix="s5")
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
print("== %dx%d ==" % (W,H))
print("errors on load:", ev("window.__errs||[]"))
print("blocks:", ev("(function(){var h=document.getElementById('blockList');return h?h.querySelectorAll('.block-item').length:'MISSING';})()"))
print("templateList exists:", ev("!!document.getElementById('templateList')"))
print("sections:", ev("""(function(){var o=[];document.querySelectorAll('#panelScene .scene-step-head b').forEach(function(b){o.push(b.textContent)});return o;})()"""))
print("chartSection hidden:", ev("(function(){var e=document.getElementById('chartSection');return e?e.hidden:'MISSING';})()"))
print("chart type options:", ev("document.getElementById('chartType').options.length"))
print("chartSource:", ev("!!document.getElementById('chartSource')"))
print("Randomize present:", ev("(document.body.innerText.indexOf('Randomize')>=0)"))

# add a chart from step 1
ev("document.querySelector('[data-panel=\"scene\"]').click()"); time.sleep(0.4)
ev("document.querySelector('#blockList [data-scene-module=\"chart\"]').click()"); time.sleep(1.0)
print("after add chart -> nodes:", ev("document.querySelectorAll('#stage .alur-canvas-node').length"))
print("chartSection hidden:", ev("(function(){var e=document.getElementById('chartSection');return e?e.hidden:'MISSING';})()"))
print("chartType:", ev("document.getElementById('chartType').value"))
print("quickAdd hidden:", ev("(function(){var e=document.getElementById('chartQuickAdd');return e?e.hidden:'MISSING';})()"))
print("dataStatus:", ev("(function(){var e=document.getElementById('chartDataStatus');return e?e.textContent:'MISSING';})()"))
# change type to donut
ev("""(function(){var s=document.getElementById('chartType');s.value='donut';
 s.dispatchEvent(new Event('change',{bubbles:true}));return 1;})()""")
time.sleep(0.9)
print("after donut -> chartType:", ev("document.getElementById('chartType').value"))
print("node chartType:", ev("(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));var n=s.nodes[s.selected];return n?n.chartType:'none';})()"))
# second chart via quick list
ev("document.querySelector('#panelScene [data-close]').click()"); time.sleep(0.2)
ev("document.querySelector('[data-panel=\"scene\"]').click()"); time.sleep(0.4)
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
