import json, time, urllib.request, subprocess, tempfile
import websocket

PORT = 9796
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
ev("document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'n',bubbles:true,cancelable:true}));")
time.sleep(0.9)


STATE_JS = "(function(){var n=document.querySelector('.alur-sticky');var t=document.querySelector('.alur-sticky-label');"
STATE_JS += "var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));"
STATE_JS += "var k=null;Object.keys(s.nodes).forEach(function(x){if(s.nodes[x].shape==='sticky')k=x;});var o=s.nodes[k];"
STATE_JS += "var sk=document.querySelectorAll('.alur-node-rough').length;"
STATE_JS += "return 'fill='+(n?n.getAttribute('fill'):'?')+' ink='+(t?(t.style.fill||''):'?')+' fs='+(t?t.getAttribute('font-size'):'?')"
STATE_JS += " + ' anchor='+(t?t.getAttribute('text-anchor'):'?')+' roughPaths='+sk+' op='+(n?n.getAttribute('opacity'):'?')"
STATE_JS += " + ' | spec fill='+o.fill+' text='+o.textColor+' size='+o.fontSize+' align='+o.textAlign+' slop='+o.sloppiness+' op='+o.opacity+' link='+o.link;})()"

def state():
    return ev(STATE_JS)
def hit(sel, idx):
    return ev("(function(){var e=document.querySelectorAll(%s)[%d];if(!e)return 'missing';"
              "e.scrollIntoView({block:'center'});var r=e.getBoundingClientRect();"
              "var t=document.elementFromPoint(Math.round(r.x+r.width/2),Math.round(r.y+r.height/2));"
              "return t?t.tagName+'.'+(t.className||''):'null';})()" % (json.dumps(sel), idx))

def js(expr):
    ev(expr); time.sleep(0.6)

print('initial   :', state())
print('hit Paper :', hit('#shapePanel .pp-sw', 0), '| hit Ink:', hit('#shapePanel .pp-sw', 1))
print('hit Size  :', hit('#shapePanel .pp-seg', 0), '| hit Align:', hit('#shapePanel .pp-seg', 1),
      '| hit Slop:', hit('#shapePanel .pp-seg', 2))
print('hit Opacity:', hit('#shapePanel .pp-range', 0), '| hit Link:', hit('#shapePanel .pp-link input', 0))

print('\n-- Paper -> #ffc9c9')
js("(function(){var d=document.querySelectorAll('#shapePanel .pp-sw')[0];d.querySelectorAll('.pp-dot')[3].click();})()")
print('  ', state())

print('-- Ink -> #e03131')
js("(function(){var d=document.querySelectorAll('#shapePanel .pp-sw')[1];d.querySelectorAll('.pp-dot')[1].click();})()")
print('  ', state())

print('-- Text size -> XL')
js("(function(){var b=document.querySelectorAll('#shapePanel .pp-seg')[0].querySelectorAll('button');b[b.length-1].click();})()")
print('  ', state())

print('-- Align -> right')
js("(function(){var b=document.querySelectorAll('#shapePanel .pp-seg')[1].querySelectorAll('button');b[2].click();})()")
print('  ', state())

print('-- Roughness -> cartoonist')
js("(function(){var b=document.querySelectorAll('#shapePanel .pp-seg')[2].querySelectorAll('button');b[2].click();})()")
print('  ', state())

print('-- Opacity -> 40')
js("(function(){var r=document.querySelector('#shapePanel .pp-range');r.value=40;"
   "r.dispatchEvent(new Event('input',{bubbles:true}));r.dispatchEvent(new Event('change',{bubbles:true}));})()")
print('  ', state())

print('-- Link -> example.com')
js("(function(){var i=document.querySelector('#shapePanel .pp-link input');i.value='example.com';"
   "document.querySelectorAll('#shapePanel .pp-link button')[0].click();})()")
print('  ', state())
print('   badge:', ev("(function(){var a=document.querySelector('.alur-node-link');return a?a.getAttribute('href'):'none';})()"))
print('\nerrs:', ev("window.__errs"))
c.close(); proc.terminate()