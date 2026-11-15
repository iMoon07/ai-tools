import json, time, urllib.request, subprocess, tempfile
import websocket

PORT = 9781
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

# --- 1. sticky default is paper, not a dark box -------------------------
ev("document.querySelector('[data-tool=\"sticky\"]').click()")
drag(ST['x'] + 300, ST['y'] + 220, ST['x'] + 420, ST['y'] + 340)
print('sticky shape:', ev("(function(){var n=window._state.spec.nodes[Object.keys(window._state.spec.nodes)[0]];"
                          "return n?JSON.stringify({shape:n.shape,fill:n.fill,text:n.textColor,slop:n.sloppiness}):null;})()"))
print('sticky box fill attr:', ev("(function(){var b=document.querySelector('.alur-sticky .alur-node-box');return b?b.getAttribute('fill'):null;})()"))
print('panel title:', ev("(function(){var b=document.querySelector('#shapePanel .shape-head b');return b?b.textContent.trim():null;})()"))
print('panel sections:', ev("(function(){var s=document.querySelectorAll('#shapePanel .pp-cap');"
                            "var o=[];for(var i=0;i<s.length;i++)o.push(s[i].textContent.trim());return o.join('|');})()"))
print('action labels:', ev("(function(){var s=document.querySelectorAll('#shapePanel .pp-acts .pp-txt');"
                           "var o=[];for(var i=0;i<s.length;i++)o.push(s[i].textContent);return o.join('|');})()"))

# Paper swatch click must repaint the note and the pressed state must move.
print('paper pressed before:', ev("(function(){var b=document.querySelector('#shapePanel .pp-dot[aria-pressed=\"true\"]');return b?b.dataset.color:null;})()"))
ev("(function(){var r=document.querySelectorAll('#shapePanel .pp-sw')[0];"
   "if(r) r.querySelectorAll('.pp-dot')[1].click();})()")
time.sleep(0.6)
print('paper pressed after :', ev("(function(){var b=document.querySelector('#shapePanel .pp-dot[aria-pressed=\"true\"]');return b?b.dataset.color:null;})()"))
print('sticky box fill after:', ev("(function(){var b=document.querySelector('.alur-sticky .alur-node-box');return b?b.getAttribute('fill'):null;})()"))
print('hex chip width/scroll:', ev("(function(){var h=document.querySelector('#shapePanel .pp-hex');"
                                   "return h?JSON.stringify({w:h.clientWidth,sw:h.scrollWidth}):null;})()"))

# --- 2. link field on the sticky ---------------------------------------
print('link field present:', ev("!!document.querySelector('#shapePanel .pp-link input')"))
ev("(function(){var i=document.querySelector('#shapePanel .pp-link input');"
   "i.value='example.com';i.dispatchEvent(new Event('input',{bubbles:true}));"
   "var b=document.querySelectorAll('#shapePanel .pp-link button');if(b[0])b[0].click();})()")
time.sleep(0.6)
print('link stored:', ev("(function(){var n=window._state.spec.nodes[Object.keys(window._state.spec.nodes)[0]];return n?String(n.link):null;})()"))
print('link badge in svg:', ev("(function(){var a=document.querySelector('.alur-node-link');"
                               "return a?JSON.stringify({href:a.getAttribute('href'),target:a.getAttribute('target')}):null;})()"))

# --- 3. fill tool has a panel ------------------------------------------
ev("document.querySelector('[data-tool=\"fill\"]').click()")
time.sleep(0.5)
print('fill panel hidden:', ev("document.getElementById('shapePanel').hidden"))
print('fill panel title:', ev("(function(){var b=document.querySelector('#shapePanel .shape-head b');return b?b.textContent.trim():null;})()"))
print('fill dots:', ev("document.querySelectorAll('#shapePanel .pp-dot').length"))
ev("(function(){var r=document.querySelectorAll('#shapePanel .pp-sw')[0];"
   "if(r) r.querySelectorAll('.pp-dot')[3].click();})()")
time.sleep(0.4)
print('editor.fillColor:', ev("String(window._editor.fillColor)"))
ev("(function(){var s=document.querySelectorAll('#shapePanel .pp-seg');"
   "if(s[1]) s[1].querySelectorAll('button')[2].click();})()")
time.sleep(0.4)
print('editor.fillStyle:', ev("String(window._editor.fillStyle)"))

# fill a box by tapping it
ev("document.querySelector('[data-tool=\"box\"]').click()")
drag(ST['x'] + 700, ST['y'] + 200, ST['x'] + 860, ST['y'] + 300)
ev("document.querySelector('[data-tool=\"fill\"]').click()")
time.sleep(0.3)
tap(ST['x'] + 780, ST['y'] + 250)
time.sleep(0.5)
print('filled node:', ev("(function(){var s=window._state.spec.nodes;var k=Object.keys(s);"
                         "for(var i=k.length-1;i>=0;i--){if(s[k[i]].shape==='box')"
                         "return JSON.stringify({fill:s[k[i]].fill,style:s[k[i]].fillStyle});}return null;})()"))
print('errs:', ev("window.__errs"))
c.close(); proc.terminate()