import json, time, urllib.request, subprocess, tempfile
import websocket

PORT = 9794
tmp = tempfile.mkdtemp(prefix="hit")
proc = subprocess.Popen(["chromium", "--headless=new", "--disable-gpu", "--no-sandbox",
    "--hide-scrollbars", "--remote-debugging-port=%d" % PORT, "--remote-allow-origins=*",
    "--user-data-dir=" + tmp, "--window-size=1400,900", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(80):
    try:
        urllib.request.urlopen("http://127.0.0.1:%d/json/version" % PORT, timeout=1).read(); break
    except Exception:
        time.sleep(0.25)
tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT).read())
page = [t for t in tabs if t["type"] == "page"][0]
c = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=30)
i = [0]
def cmd(m, **p):
    i[0] += 1; c.send(json.dumps({"id": i[0], "method": m, "params": p}))
    while True:
        r = json.loads(c.recv())
        if r.get("id") == i[0]: return r.get("result", {})
def ev(e):
    r = cmd("Runtime.evaluate", expression=e, returnByValue=True, awaitPromise=True).get("result", {})
    return r.get("value") if r.get("subtype") != "error" else {"__err": r.get("description")}
def real_click(x, y):
    for kind, buttons in (("mousePressed", 1), ("mouseReleased", 0)):
        cmd("Input.dispatchMouseEvent", type=kind, x=x, y=y, button="left",
            buttons=buttons, clickCount=1)
        time.sleep(0.06)
    time.sleep(0.6)

cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride", width=1400, height=900, deviceScaleFactor=1, mobile=False)
cmd("Page.navigate", url="http://127.0.0.1:8123/draw.html?cb=" + str(time.time()))
time.sleep(3.6)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.3)

# instrument: log every pointerdown/click target and whether the panel is replaced
ev("""window.__log=[];
document.addEventListener('pointerdown',function(e){
  var t=e.target; var n=t&&t.className?(t.className.baseVal!==undefined?t.className.baseVal:t.className):'';
  window.__log.push('down:'+t.tagName+'#'+(t.id||'')+'.'+n);
},true);
document.addEventListener('click',function(e){
  var t=e.target; var n=t&&t.className?(t.className.baseVal!==undefined?t.className.baseVal:t.className):'';
  window.__log.push('click:'+t.tagName+'#'+(t.id||'')+'.'+n);
},true);
window.__panelGen=0;
var sp=document.getElementById('shapePanel');
new MutationObserver(function(){window.__panelGen++;}).observe(sp,{childList:true,subtree:true});
""")

ev("document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'n',bubbles:true,cancelable:true}));")
time.sleep(0.9)
print('textEdit:', ev("!!document.getElementById('inlineText')"))
print('gen before:', ev("window.__panelGen"))

def click(sel, idx):
    pos = ev("(function(){var e=document.querySelectorAll(%s)[%d];if(!e)return null;"
             "var r=e.getBoundingClientRect();var cx=Math.round(r.x+r.width/2),cy=Math.round(r.y+r.height/2);"
             "var t=document.elementFromPoint(cx,cy);"
             "return JSON.stringify({x:cx,y:cy,top:t?t.tagName+'#'+(t.id||'')+'.'+(t.className||''):'null'});})()"
             % (json.dumps(sel), idx))
    if not pos or pos=='null':
        print('  MISS', sel, idx); return
    q=json.loads(pos); real_click(q['x'], q['y'])
    print('  clicked', sel, idx, q['top'], '-> fill', ev("(function(){var b=document.querySelector('.alur-sticky');return b?b.getAttribute('fill'):'none';})()"),
          'ink', ev("(function(){var t=document.querySelector('.alur-sticky-label');return t?t.style.fill:'';})()"),
          'size', ev("(function(){var t=document.querySelector('.alur-sticky-label');return t?t.getAttribute('font-size'):'';})()"))

click('#shapePanel .pp-sw', 0)
click('#shapePanel .pp-sw', 1)
click('#shapePanel .pp-seg', 3)
click('#shapePanel .pp-seg', 3)
print('gen:', ev("window.__panelGen"))
print('log:', ev("JSON.stringify(window.__log)"))
print('errs:', ev("window.__errs"))
c.close(); proc.terminate()