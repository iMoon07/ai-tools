import json, time, urllib.request, subprocess, tempfile
import websocket

PORT = 9821
tmp = tempfile.mkdtemp(prefix="sfil")
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

JS = ("(function(){var p=document.querySelector('.alur-sticky');var t=document.querySelector('.alur-sticky-label');"
      "var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));"
      "var k=null;Object.keys(s.nodes).forEach(function(x){if(s.nodes[x].shape==='sticky')k=x;});var o=s.nodes[k];"
      "var pc=p?getComputedStyle(p):null;var tc=t?getComputedStyle(t):null;"
      "return 'COMPUTED paper='+(pc?pc.fill:'?')+' stroke='+(pc?pc.stroke:'?')+' | ink='+(tc?tc.fill:'?')"
      " + ' | attrFill='+(p?p.getAttribute('fill'):'?')+' style='+(p?(p.getAttribute('style')||''):'?')"
      " + ' | spec fill='+o.fill+' text='+o.textColor+' slop='+o.sloppiness;})()")

def state():
    return ev(JS)
def js(expr, wait=0.6):
    ev(expr); time.sleep(wait)

print('initial        :', state())

print('\n-- panel Paper dot 3 (#ffc9c9)')
js("(function(){var d=document.querySelectorAll('#shapePanel .pp-sw')[0];"
   "if(d)d.querySelectorAll('.pp-dot')[3].click();})()")
print('                :', state())

print('-- panel Paper dot 0 (first)')
js("(function(){var d=document.querySelectorAll('#shapePanel .pp-sw')[0];"
   "if(d)d.querySelectorAll('.pp-dot')[0].click();})()")
print('                :', state())

print('-- panel Ink dot 1')
js("(function(){var d=document.querySelectorAll('#shapePanel .pp-sw')[1];"
   "if(d)d.querySelectorAll('.pp-dot')[1].click();})()")
print('                :', state())

print('\n-- hex input paper -> #d0bfff')
js("(function(){var i=document.querySelector('#shapePanel .pp-hex');"
   "if(i){i.value='#d0bfff';i.dispatchEvent(new Event('change',{bubbles:true}));}"
   "else window.__nohex=1;})()")
print('                :', state())

print('\nscreenshot check:', ev("(function(){var p=document.querySelector('.alur-sticky');"
      "if(!p)return 'no sticky';var b=p.getBoundingClientRect();"
      "return Math.round(b.width)+'x'+Math.round(b.height);})()"))
print('errs:', ev("window.__errs"))
print('nohex:', ev("window.__nohex||0"))
c.close(); proc.terminate()