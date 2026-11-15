import json, time, urllib.request, subprocess, tempfile
import websocket

PORT = 9811
tmp = tempfile.mkdtemp(prefix="repro")
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
        cmd("Input.dispatchMouseEvent", type=kind, x=x, y=y, button="left", buttons=buttons, clickCount=1)
        time.sleep(0.06)
    time.sleep(0.55)

cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride", width=1400, height=900, deviceScaleFactor=1, mobile=False)
cmd("Page.navigate", url="http://127.0.0.1:8123/draw.html?cb=" + str(time.time()))
time.sleep(3.8)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.3)

def spec_fill():
    return ev("(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));"
              "var o=[];Object.keys(s.nodes).forEach(function(k){if(s.nodes[k].shape==='sticky')"
              "o.push(k+' fill='+s.nodes[k].fill+' ink='+s.nodes[k].textColor);});return o.join(' | ');})()")
def panel_hex():
    return ev("(function(){var h=document.querySelectorAll('#shapePanel .pp-hex');"
              "var o=[];for(var i=0;i<h.length;i++)o.push(h[i].value);return o.join(' , ');})()")
def pressed():
    return ev("(function(){var o=[];document.querySelectorAll('#shapePanel .pp-dot[aria-pressed=\"true\"]')"
              ".forEach(function(b){o.push(b.dataset.color);});return o.join(' , ');})()")

ev("document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'n',bubbles:true,cancelable:true}));")
time.sleep(0.9)
print('start     :', spec_fill(), '| hex', panel_hex(), '| pressed', pressed())

print('\n-- open custom picker, pick WHITE --')
pos = ev("(function(){var e=document.querySelector('#shapePanel .pp-custom');var r=e.getBoundingClientRect();"
         "return Math.round(r.x+r.width/2)+','+Math.round(r.y+r.height/2);})()")
x, y = [int(v) for v in pos.split(',')]
real_click(x, y)
time.sleep(0.5)
print('pop open  :', ev("!!document.querySelector('.color-pop')"))
print('swatches  :', ev("document.querySelectorAll('.color-pop .pal .swatch').length"))
clicked = ev("(function(){var s=document.querySelectorAll('.color-pop .pal .swatch');"
             "for(var i=0;i<s.length;i++){var bg=s[i].style.background||'';"
             "if(bg.indexOf('255, 255, 255')>=0||bg.indexOf('#fff')>=0||bg.indexOf('white')>=0){s[i].click();return i;}}"
             "return 'no-white';})()")
time.sleep(0.7)
print('white idx :', clicked)
print('after     :', spec_fill(), '| hex', panel_hex(), '| pressed', pressed())

print('\n-- now click the YELLOW Paper dot (real mouse) --')
pos = ev("(function(){var d=document.querySelectorAll('#shapePanel .pp-sw')[0];"
         "var b=d.querySelectorAll('.pp-dot')[0];var r=b.getBoundingClientRect();"
         "return Math.round(r.x+r.width/2)+','+Math.round(r.y+r.height/2);})()")
print('dot at    :', pos, 'top=', ev("(function(){var p='%s'.split(',');var e=document.elementFromPoint(+p[0],+p[1]);"
                                     "return e?e.tagName+'#'+e.id+'.'+(e.className||''):'null';})()" % pos))
x, y = [int(v) for v in pos.split(',')]
real_click(x, y)
time.sleep(0.7)
print('after     :', spec_fill(), '| hex', panel_hex(), '| pressed', pressed())
print('\nerrs:', ev("window.__errs"))
c.close(); proc.terminate()