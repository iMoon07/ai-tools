import json, time, urllib.request, subprocess, tempfile
import websocket

PORT = 9793
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
    time.sleep(0.5)

cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride", width=1400, height=900, deviceScaleFactor=1, mobile=False)
cmd("Page.navigate", url="http://127.0.0.1:8123/draw.html?cb=" + str(time.time()))
time.sleep(3.6)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.3)
ev("document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'n',bubbles:true,cancelable:true}));")
time.sleep(0.8)
# close the inline editor so it cannot keep focus
ev("if(window.__closeInline&&__closeInline)0; document.getElementById('inlineText')&&document.getElementById('inlineText').blur();")
time.sleep(0.2)

SECTIONS = ["Paper", "Ink", "Text size", "Align", "Opacity", "Roughness", "Link"]
print('panel scrollHeight/clientHeight:', ev("(function(){var b=document.querySelector('#shapePanel .shape-body');"
                                             "return b?b.scrollHeight+'/'+b.clientHeight:'none';})()"))
print('swatch rows:', ev("document.querySelectorAll('#shapePanel .pp-sw').length"))
print('seg rows:', ev("document.querySelectorAll('#shapePanel .pp-seg').length"))

def click_sel(sel, idx=0, label=""):
    pos = ev("(function(){var e=document.querySelectorAll(%s)[%d];if(!e)return null;"
             "e.scrollIntoView({block:'center'});var r=e.getBoundingClientRect();"
             "return JSON.stringify({x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),"
             "top:(document.elementFromPoint(Math.round(r.x+r.width/2),Math.round(r.y+r.height/2))||{}).className||''});})()"
             % (json.dumps(sel), idx))
    if not pos or pos == 'null':
        print('  %-18s -> element missing' % label); return
    p = json.loads(pos)
    real_click(p['x'], p['y'])
    print('  %-18s -> clicked %s (top=%s)' % (label, p['x'], p['y']))

def state():
    return ev("(function(){var n=document.querySelector('.alur-sticky');var t=document.querySelector('.alur-sticky-label');"
              "var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));"
              "var k=null;Object.keys(s.nodes).forEach(function(x){if(s.nodes[x].shape==='sticky')k=x;});"
              "var o=s.nodes[k];return JSON.stringify({fill:n?n.getAttribute('fill'):null,"
              "ink:t?(t.style.fill||''):'',size:t?t.getAttribute('font-size'):null,"
              "spec:{fill:o.fill,text:o.textColor,size:o.fontSize,align:o.textAlign,op:o.opacity,slop:o.sloppiness,link:o.link}});})()")

print('initial:', state())
click_sel('#shapePanel .pp-sw', 1, 'Ink dot #2')
print('after ink:', state())
click_sel('#shapePanel .pp-seg', 3, 'Text size XL')
print('after size:', state())
click_sel('#shapePanel .pp-seg', 3, 'Align right')
print('after align:', state())
click_sel('#shapePanel .pp-seg', 2, 'Roughness cartoonist')
print('after slop:', state())
click_sel('#shapePanel .pp-range', 0, 'Opacity slider')
print('after opacity:', state())
print('errs:', ev("window.__errs"))
c.close(); proc.terminate()