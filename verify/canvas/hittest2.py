import json, time, urllib.request, subprocess, tempfile
import websocket

PORT = 9792
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
    time.sleep(0.55)

cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride", width=1400, height=900, deviceScaleFactor=1, mobile=False)
cmd("Page.navigate", url="http://127.0.0.1:8123/draw.html?cb=" + str(time.time()))
time.sleep(3.6)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.3)

# exactly what a user does: press N
ev("document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'n',bubbles:true,cancelable:true}));")
time.sleep(0.8)
print('nodes:', ev("(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));"
                   "var o=[];Object.keys(s.nodes).forEach(function(k){var n=s.nodes[k];"
                   "o.push(k+':'+n.shape+'/fill='+n.fill+'/ink='+n.textColor);});return o.join(' | ');})()"))
print('textEdit open:', ev("!!document.getElementById('inlineText')"))
print('inlineText rect:', ev("(function(){var t=document.getElementById('inlineText');if(!t)return 'none';"
                             "var r=t.getBoundingClientRect();return Math.round(r.x)+','+Math.round(r.y)+' '+Math.round(r.width)+'x'+Math.round(r.height);})()"))
print('panel z-index:', ev("getComputedStyle(document.getElementById('shapePanel')).zIndex"))
print('label fill rendered:', ev("(function(){var t=document.querySelector('.alur-sticky-label');return t?t.style.fill||t.getAttribute('fill'):'none';})()"))
print('outline stroke rendered:', ev("(function(){var b=document.querySelector('.alur-sticky');return b?b.getAttribute('stroke'):'none';})()"))

print('--- real mouse click: Paper swatch #2 ---')
pos = ev("(function(){var d=document.querySelectorAll('#shapePanel .pp-sw')[0];if(!d)return null;"
         "var b=d.querySelectorAll('.pp-dot')[1];var r=b.getBoundingClientRect();"
         "return JSON.stringify({x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)});})()")
print('pos:', pos)
if pos and pos != 'null':
    p = json.loads(pos)
    print('top element:', ev("(function(){var e=document.elementFromPoint(%d,%d);"
                             "return e?e.tagName+'#'+e.id+'.'+(e.className||''):'null';})()" % (p['x'], p['y'])))
    real_click(p['x'], p['y'])
    print('sticky fill:', ev("(function(){var b=document.querySelector('.alur-sticky');return b?b.getAttribute('fill'):'none';})()"))

print('--- real mouse click: Ink swatch #2 (red) ---')
pos = ev("(function(){var d=document.querySelectorAll('#shapePanel .pp-sw')[1];if(!d)return null;"
         "var b=d.querySelectorAll('.pp-dot')[1];var r=b.getBoundingClientRect();"
         "return JSON.stringify({x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)});})()")
if pos and pos != 'null':
    p = json.loads(pos)
    real_click(p['x'], p['y'])
    print('label fill:', ev("(function(){var t=document.querySelector('.alur-sticky-label');return t?t.style.fill||t.getAttribute('fill'):'none';})()"))
    print('outline stroke:', ev("(function(){var b=document.querySelector('.alur-sticky');return b?b.getAttribute('stroke'):'none';})()"))

print('--- real mouse click: Text size XL ---')
pos = ev("(function(){var s=document.querySelectorAll('#shapePanel .pp-seg')[0];"
         "if(!s)return null;var b=s.querySelectorAll('button');var r=b[b.length-1].getBoundingClientRect();"
         "return JSON.stringify({x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)});})()")
if pos and pos != 'null':
    p = json.loads(pos)
    real_click(p['x'], p['y'])
    print('font size:', ev("(function(){var t=document.querySelector('.alur-sticky-label');return t?t.getAttribute('font-size'):'none';})()"))
    print('spec fontSize:', ev("(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));"
                               "var o=[];Object.keys(s.nodes).forEach(function(k){if(s.nodes[k].shape==='sticky')o.push(s.nodes[k].fontSize);});return o.join(',');})()"))

print('errs:', ev("window.__errs"))
c.close(); proc.terminate()