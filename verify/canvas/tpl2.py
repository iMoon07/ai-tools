import json, sys, time, urllib.request, subprocess, tempfile
import websocket
PORT=9922
tmp=tempfile.mkdtemp(prefix="t2")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox",
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
    if r.get("subtype")=="error": print("JS ERROR:",r.get("description"))
    return r.get("value")
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")

def panel():
    return ev("""(function(){
      var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));
      var n=s.nodes[s.selected];
      var q=document.getElementById('chartQuickAdd');
      var c=document.getElementById('chartBlockControls');
      var h=document.getElementById('chartHint');
      var sec=document.getElementById('chartSection');
      return {sel:s.selected, shape:n&&n.shape, mod:n&&n.module, type:n&&n.chartType,
              quickHidden:q?q.hidden:null, ctrlHidden:c?c.hidden:null,
              hint:h?h.textContent:null, secHidden:sec?sec.hidden:null};
    })()""")

ev("document.querySelector('#panelScene [data-close]') && document.querySelector('#panelScene [data-close]').click()")
ev("document.querySelector('#templateList [data-template-module=\"chart\"]').click()"); time.sleep(1.2)
print("after template:", panel())
ev("document.querySelector('#panelScene [data-close]') && document.querySelector('#panelScene [data-close]').click()")
time.sleep(0.3)
ev("document.querySelector('[data-panel=\"scene\"]').click()"); time.sleep(0.5)
print("after reopen  :", panel())
ev("document.querySelector('#panelScene [data-close]') && document.querySelector('#panelScene [data-close]').click()")
ev("document.querySelector('[data-panel=\"scene\"]').click()"); time.sleep(0.5)
print("after reopen2 :", panel())
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
