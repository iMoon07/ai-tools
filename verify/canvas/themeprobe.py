import json, time, urllib.request, subprocess, tempfile, sys
import websocket
W = int(sys.argv[1]) if len(sys.argv) > 1 else 1600
H = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
MOB = len(sys.argv) > 3 and sys.argv[3] == 'm'
PORT = 9613
tmp = tempfile.mkdtemp(prefix="theme")
proc = subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
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
    if r.get("subtype")=="error": return {"__err":r.get("description")}
    return r.get("value")
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=MOB)
if MOB: cmd("Emulation.setTouchEmulationEnabled",enabled=True,maxTouchPoints=5)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.4)
out = {}
out['initial'] = ev("({cls:document.body.className, theme:document.body.getAttribute('data-theme'), btn:!!document.getElementById('themeToggle')})")
out['dark'] = ev("""(function(){var b=document.getElementById('themeToggle'); if(!b) return 'no button'; b.click(); return 1;})()""")
time.sleep(0.4)
out['afterClick'] = ev("({cls:document.body.className, theme:document.body.getAttribute('data-theme'), stored:localStorage.getItem('ruang.theme.v1'), pressed:document.getElementById('themeToggle').getAttribute('aria-pressed'), ico:document.querySelector('#themeToggle .theme-ico').textContent, bg:getComputedStyle(document.body).backgroundColor, text:getComputedStyle(document.body).color, topbar:getComputedStyle(document.querySelector('.topbar')).backgroundColor, stage:getComputedStyle(document.getElementById('stage')).backgroundColor})")
out['btnRect'] = ev("""(function(){var b=document.getElementById('themeToggle');var r=b.getBoundingClientRect();return {w:Math.round(r.width),h:Math.round(r.height),x:Math.round(r.x),y:Math.round(r.y),vis:getComputedStyle(b).display};})()""")
out['reload'] = ev("1")
cmd("Page.reload"); time.sleep(3.0)
out['afterReload'] = ev("({cls:document.body.className, theme:document.body.getAttribute('data-theme'), stored:localStorage.getItem('ruang.theme.v1')})")
out['back'] = ev("""(function(){document.getElementById('themeToggle').click();return document.body.className;})()""")
time.sleep(0.3)
out['darkAgain'] = ev("({cls:document.body.className, stored:localStorage.getItem('ruang.theme.v1'), bg:getComputedStyle(document.body).backgroundColor})")
out['errs'] = ev("(window.__errs||[]).length")
print(json.dumps(out, indent=1))
c.close(); proc.terminate()
