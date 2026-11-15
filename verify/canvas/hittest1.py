import json, time, urllib.request, subprocess, tempfile
import websocket

PORT = 9791
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

cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride", width=1400, height=900, deviceScaleFactor=1, mobile=False)
cmd("Page.navigate", url="http://127.0.0.1:8123/draw.html?cb=" + str(time.time()))
time.sleep(3.6)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.3)

def ptr(t, x, y, b=1):
    ev("(function(){var s=document.getElementById('stage');s.dispatchEvent(new PointerEvent(" + json.dumps(t) +
       ",{bubbles:true,cancelable:true,clientX:%d,clientY:%d,button:0,buttons:%d,pointerId:1,pointerType:'mouse',isPrimary:true}));})()" % (x, y, b))
ST = ev("(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y};})()")

ev("document.querySelector('[data-tool=\"sticky\"]').click()")
ptr("pointerdown", ST['x'] + 300, ST['y'] + 220)
ptr("pointermove", ST['x'] + 360, ST['y'] + 280)
ptr("pointerup", ST['x'] + 420, ST['y'] + 340, 0)
time.sleep(0.7)

print('textEdit active:', ev("!!document.getElementById('inlineText')"))
print('inlineText rect:', ev("(function(){var t=document.getElementById('inlineText');"
                             "if(!t)return 'none';var r=t.getBoundingClientRect();"
                             "return JSON.stringify({x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)});})()"))
print('panel rect:', ev("(function(){var p=document.getElementById('shapePanel');var r=p.getBoundingClientRect();"
                        "return JSON.stringify({x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)});})()"))

print('--- elementFromPoint on each control ---')
print(ev("""(function(){
  var sel=['.pp-sw','.pp-seg','.pp-range','.pp-link input','.pp-acts button'];
  var out=[];
  sel.forEach(function(s){
    var el=document.querySelector('#shapePanel '+s);
    if(!el){out.push(s+': missing');return;}
    var r=el.getBoundingClientRect();
    var x=Math.round(r.x+r.width/2), y=Math.round(r.y+r.height/2);
    var top=document.elementFromPoint(x,y);
    out.push(s+' -> '+(top? (top.tagName+'.'+(top.className&&top.className.baseVal!==undefined?top.className.baseVal:top.className||'')+'#'+(top.id||'')) : 'null'));
  });
  return out.join('\\n');
})()"""))

print('--- real mouse click on Paper swatch (Input.dispatchMouseEvent) ---')
target = ev("""(function(){var d=document.querySelectorAll('#shapePanel .pp-sw')[0];
  if(!d)return null;var b=d.querySelectorAll('.pp-dot')[1];var r=b.getBoundingClientRect();
  return JSON.stringify({x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),color:b.dataset.color});})()""")
print('target:', target)
if target and target != 'null':
    t = json.loads(target)
    for kind in ("mousePressed", "mouseReleased"):
        cmd("Input.dispatchMouseEvent", type=kind, x=t['x'], y=t['y'], button="left",
            buttons=1 if kind == "mousePressed" else 0, clickCount=1)
        time.sleep(0.08)
    time.sleep(0.7)
    print('sticky fill after real click:', ev("(function(){var b=document.querySelector('.alur-sticky');return b?b.getAttribute('fill'):'none';})()"))
print('errs:', ev("window.__errs"))
c.close(); proc.terminate()