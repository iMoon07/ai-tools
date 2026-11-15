import json, time, urllib.request, subprocess, tempfile
import websocket

PORT = 9795
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
ev("document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'n',bubbles:true,cancelable:true}));")
time.sleep(0.9)

def state():
    return ev("(function(){var n=document.querySelector('.alur-sticky');var t=document.querySelector('.alur-sticky-label');"
              "var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));"
              "var k=null;Object.keys(s.nodes).forEach(function(x){if(s.nodes[x].shape==='sticky')k=x;});"
              "var o=s.nodes[k];return 'fill='+(n?n.getAttribute('fill'):'?')+' ink='+(t?(t.style.fill||''):'?')+' size='+(t?t.getAttribute('font-size'):'?')+' | spec fill='+o.fill+' text='+o.textColor+' size='+o.fontSize+' align='+o.textAlign+' slop='+o.sloppiness+' link='+o.link;})()")

def press(sel, idx=0):
    pos = ev("(function(){var e=document.querySelectorAll(%s)[%d];if(!e)return null;"
             "e.scrollIntoView({block:'center'});var r=e.getBoundingClientRect();"
             "var cx=Math.round(r.x+r.width/2),cy=Math.round(r.y+r.height/2);"
             "var t=document.elementFromPoint(cx,cy);"
             "return JSON.stringify({x:cx,y:cy,top:t?t.tagName:'null'});})()" % (json.dumps(sel), idx))
    if not pos or pos == 'null':
        print('   MISS', sel, idx); return
    q = json.loads(pos)
    real_click(q['x'], q['y'])
    print('   hit', q['top'])

print('initial        :', state())
print('Paper  -> green')
press('#shapePanel .pp-sw:nth-of-type(1) .pp-dot', 1)
print('               :', state())
print('Ink    -> red')
press('#shapePanel .pp-sw:nth-of-type(2) .pp-dot', 1)
print('               :', state())
print('Size   -> last (XL)')
press('#shapePanel .pp-seg:nth-of-type(1) button', 3)
print('               :', state())
print('Align  -> last (right)')
press('#shapePanel .pp-seg:nth-of-type(2) button', 2)
print('               :', state())
print('Slop   -> last (cartoonist)')
press('#shapePanel .pp-seg:nth-of-type(3) button', 2)
print('               :', state())

print('Opacity -> 40%')
ev("(function(){var r=document.querySelector('#shapePanel .pp-range');"
   "r.value=40;r.dispatchEvent(new Event('input',{bubbles:true}));"
   "r.dispatchEvent(new Event('change',{bubbles:true}));})()")
time.sleep(0.6)
print('               :', state())

print('Link   -> example.com')
ev("(function(){var i=document.querySelector('#shapePanel .pp-link input');i.value='example.com';"
   "var b=document.querySelectorAll('#shapePanel .pp-link button');b[0].click();})()")
time.sleep(0.8)
print('               :', state())
print('badge           :', ev("(function(){var a=document.querySelector('.alur-node-link');"
                             "return a?a.getAttribute('href'):'none';})()"))
print('errs:', ev("window.__errs"))
c.close(); proc.terminate()