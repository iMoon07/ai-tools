import json, time, urllib.request, subprocess, tempfile
import websocket

PORT = 9782
tmp = tempfile.mkdtemp(prefix="fx")
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

SPEC = ("(function(){try{return JSON.parse(document.getElementById('stage').getAttribute('data-spec'))||{};}"
        "catch(e){return {__err:String(e)};}})()")
def nodes():
    return ev("(function(){var s=" + SPEC + ";return JSON.stringify(s&&s.nodes?s.nodes:{});})()")

cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride", width=1400, height=900, deviceScaleFactor=1, mobile=False)
cmd("Page.navigate", url="http://127.0.0.1:8123/draw.html?cb=" + str(time.time()))
time.sleep(3.6)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.3)

def ptr(t, x, y, buttons=1):
    ev("(function(){var s=document.getElementById('stage');"
       "s.dispatchEvent(new PointerEvent(" + json.dumps(t) + ",{bubbles:true,cancelable:true,"
       "clientX:%d,clientY:%d,button:0,buttons:%d,pointerId:1,pointerType:'mouse',isPrimary:true}));})()" % (x, y, buttons))
ST = ev("(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y};})()")
def drag(x0, y0, x1, y1, steps=10):
    ptr("pointerdown", x0, y0)
    for k in range(1, steps + 1):
        ptr("pointermove", x0 + (x1 - x0) * k / steps, y0 + (y1 - y0) * k / steps)
    ptr("pointerup", x1, y1, 0); time.sleep(0.5)
def tap(x, y):
    ptr("pointerdown", x, y); ptr("pointerup", x, y, 0); time.sleep(0.45)

print("--- sticky default ---")
ev("document.querySelector('[data-tool=\"sticky\"]').click()")
drag(ST['x'] + 300, ST['y'] + 220, ST['x'] + 420, ST['y'] + 340)
print('node:', ev("(function(){var n=" + nodes() + ";var k=Object.keys(n)[0];"
                  "return JSON.stringify({shape:n[k].shape,fill:n[k].fill,text:n[k].textColor,slop:n[k].sloppiness});})()"))
print('sticky box fill:', ev("(function(){var b=document.querySelector('.alur-sticky');return b?b.getAttribute('fill'):'none';})()"))
print('sections:', ev("(function(){var s=document.querySelectorAll('#shapePanel .pp-cap');var o=[];"
                      "for(var i=0;i<s.length;i++)o.push(s[i].textContent.trim());return o.join('|');})()"))
print('actions:', ev("(function(){var s=document.querySelectorAll('#shapePanel .pp-acts .pp-txt');var o=[];"
                     "for(var i=0;i<s.length;i++)o.push(s[i].textContent);return o.join('|');})()"))
print('hex chip:', ev("(function(){var h=document.querySelector('#shapePanel .pp-hex');return h?h.clientWidth+'/'+h.scrollWidth:null;})()"))

ev("(function(){var r=document.querySelectorAll('#shapePanel .pp-sw')[0];if(r)r.querySelectorAll('.pp-dot')[1].click();})()")
time.sleep(0.6)
print('paper after click:', ev("(function(){var b=document.querySelector('.alur-sticky');return b?b.getAttribute('fill'):'none';})()"))
print('pressed after click:', ev("(function(){var b=document.querySelector('#shapePanel .pp-dot[aria-pressed=\"true\"]');return b?b.dataset.color:null;})()"))

print("--- link ---")
print('link input:', ev("!!document.querySelector('#shapePanel .pp-link input')"))
ev("(function(){var i=document.querySelector('#shapePanel .pp-link input');i.value='example.com';"
   "var b=document.querySelectorAll('#shapePanel .pp-link button');if(b[0])b[0].click();})()")
time.sleep(0.7)
print('link stored:', ev("(function(){var n=" + nodes() + ";var k=Object.keys(n)[0];return String(n[k].link);})()"))
print('badge:', ev("(function(){var a=document.querySelector('.alur-node-link');"
                   "return a?JSON.stringify({href:a.getAttribute('href'),target:a.getAttribute('target'),cls:a.getAttribute('class')}):null;})()"))

print("--- fill tool panel ---")
ev("document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))")
time.sleep(0.3)
ev("document.querySelector('[data-tool=\"fill\"]').click()")
time.sleep(0.5)
print('panel hidden:', ev("document.getElementById('shapePanel').hidden"))
print('panel title:', ev("(function(){var b=document.querySelector('#shapePanel .shape-head b');return b?b.textContent.trim():null;})()"))
print('fill sections:', ev("(function(){var s=document.querySelectorAll('#shapePanel .pp-cap');var o=[];"
                           "for(var i=0;i<s.length;i++)o.push(s[i].textContent.trim());return o.join('|');})()"))
print('hint:', ev("(function(){var h=document.querySelector('#shapePanel .pp-note,#shapePanel .hint');return h?h.textContent.trim():null;})()"))
ev("(function(){var r=document.querySelectorAll('#shapePanel .pp-sw')[0];if(r)r.querySelectorAll('.pp-dot')[3].click();})()")
time.sleep(0.5)
print('fill swatch now pressed:', ev("(function(){var b=document.querySelector('#shapePanel .pp-dot[aria-pressed=\"true\"]');return b?b.dataset.color:null;})()"))

print("--- bucket paints a box ---")
ev("document.querySelector('[data-tool=\"box\"]').click()")
drag(ST['x'] + 700, ST['y'] + 200, ST['x'] + 860, ST['y'] + 300)
ev("document.querySelector('[data-tool=\"fill\"]').click()")
time.sleep(0.3)
tap(ST['x'] + 780, ST['y'] + 250)
time.sleep(0.5)
print('box nodes:', ev("(function(){var n=" + nodes() + ";var o=[];var k=Object.keys(n);"
                       "for(var i=0;i<k.length;i++){if(n[k[i]].shape==='box')o.push(JSON.stringify({fill:n[k[i]].fill,style:n[k[i]].fillStyle}));}"
                       "return o.join(' | ');})()"))
print('rendered fill:', ev("(function(){var b=document.querySelectorAll('.alur-canvas-node .alur-node-box');var o=[];"
                           "for(var i=0;i<b.length;i++)o.push(b[i].getAttribute('fill'));return o.join(',');})()"))
print('errs:', ev("window.__errs"))
c.close(); proc.terminate()