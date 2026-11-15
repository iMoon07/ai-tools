import json, subprocess, time, urllib.parse, urllib.request, shutil, base64
PORT = 9741; PROF = "/tmp/alur-probes/prof-totoshoot"
shutil.rmtree(PROF, ignore_errors=True)
proc = subprocess.Popen(["chromium", "--headless=new", f"--remote-debugging-port={PORT}",
    f"--user-data-dir={PROF}", "--no-first-run", "--no-default-browser-check", "--disable-gpu",
    "--window-size=1600,1000", "--remote-allow-origins=*", "--hide-scrollbars", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
import websocket

def http(p, method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}", method=method), timeout=10).read())

for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)

t = http("/json/new?" + urllib.parse.quote("about:blank", safe=""), method="PUT")
ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
n = [0]; exc = []

def send(m, **p):
    n[0] += 1; ws.send(json.dumps({"id": n[0], "method": m, "params": p}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == n[0]: return r.get("result", {})
        if r.get("method") == "Runtime.exceptionThrown":
            d = r["params"]["exceptionDetails"]
            exc.append(d.get("text", "") + " " + (d.get("exception") or {}).get("description", "")[:200])

def ev(e):
    r = send("Runtime.evaluate", expression=e, returnByValue=True, awaitPromise=True).get("result", {})
    return r.get("value") if r.get("subtype") != "error" else {"__err": r.get("description")}

def shot(path):
    r = send("Page.captureScreenshot", format="png")
    open(path, 'wb').write(base64.b64decode(r["data"]))

send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride", width=1600, height=1000, deviceScaleFactor=1, mobile=False)
send("Page.navigate", url="http://127.0.0.1:8123/topology.html")
time.sleep(3.6)
shot('/tmp/alur-probes/shot-closed.png')

print("layout:", json.dumps(ev("""(()=>{const r=e=>{const b=e.getBoundingClientRect();return [Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height)]};
 return {bar:r(document.querySelector('.topbar')), stage:r(document.getElementById('stage')),
   tabs:r(document.getElementById('dockTabs')), preview:r(document.getElementById('preview')),
   status:document.getElementById('topStatus').textContent,
   overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+1};})()""")))

ev("document.querySelector('.dock-tab[data-pane=nodes]').click()"); time.sleep(0.9)
shot('/tmp/alur-probes/shot-nodes.png')
print("nodes dock:", json.dumps(ev("""(()=>{const d=document.getElementById('dock');const b=d.getBoundingClientRect();
 return {open:d.classList.contains('is-open'), side:d.dataset.side, rect:[Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height)],
   stageBottom:getComputedStyle(document.getElementById('stage')).bottom,
   cards:document.querySelectorAll('#nodeList .card').length};})()""")))

ev("document.querySelector('.dock-tab[data-pane=look]').click()"); time.sleep(0.9)
shot('/tmp/alur-probes/shot-look.png')
print("look dock:", json.dumps(ev("""(()=>{const d=document.getElementById('dock');const b=d.getBoundingClientRect();
 return {side:d.dataset.side, rect:[Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height)],
   stageRight:getComputedStyle(document.getElementById('stage')).right};})()""")))

ev("document.querySelector('.dock-tab[data-pane=logos]').click()"); time.sleep(0.9)
shot('/tmp/alur-probes/shot-logos.png')
print("logos:", json.dumps(ev("({tiles:document.querySelectorAll('#logoGrid .tile').length, cats:document.querySelectorAll('#logoCat option').length})")))

ev("document.querySelector('.dock-tab[data-pane=json]').click()"); time.sleep(0.8)
shot('/tmp/alur-probes/shot-source.png')
print("source:", json.dumps(ev("({chars:document.getElementById('specBox').value.length, status:document.getElementById('codeStatus').textContent})")))

send("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
ev("document.querySelector('.dock-tab[data-pane=nodes]').click()"); time.sleep(1.0)
shot('/tmp/alur-probes/shot-mobile.png')
print("mobile:", json.dumps(ev("""(()=>{const d=document.getElementById('dock');const b=d.getBoundingClientRect();
 const t=document.getElementById('dockTabs').getBoundingClientRect();
 return {dock:[Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height)],
   tabs:[Math.round(t.x),Math.round(t.y),Math.round(t.width),Math.round(t.height)],
   overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+1,
   tabsScroll:document.getElementById('dockTabs').scrollWidth>document.getElementById('dockTabs').clientWidth};})()""")))
# audit tampilan: pastikan tidak ada elemen kunci yang hilang atau warna yang salah
print("audit:", json.dumps(ev("""(()=>{const cs=e=>{const c=getComputedStyle(e);return [c.display,c.color,c.backgroundColor,c.fontSize,c.borderRadius]};
 const t=document.querySelector('.topbar');
 const kids=[...t.children].map(e=>[e.className.split(' ')[0]||e.tagName, Math.round(e.getBoundingClientRect().width), getComputedStyle(e).display]);
 const dockTab=document.querySelector('.dock-tab.is-on');
 return {topbar:cs(t), kids, onTab:cs(dockTab),
   preview:cs(document.getElementById('preview')),
   node:cs(document.querySelector('.tp-node')),
   title:cs(document.getElementById('preview').querySelector('.tp-title')),
   count:cs(document.getElementById('preview').querySelector('.tp-count')),
   tabsBar:cs(document.getElementById('dockTabs'))};})()""")))

send("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
time.sleep(0.6)
print("mobile topbar:", json.dumps(ev("""(()=>{const t=document.querySelector('.topbar');
 const out=[...t.children].map(e=>[e.className.split(' ')[0]||e.tagName, Math.round(e.getBoundingClientRect().width), getComputedStyle(e).display]);
 const ti=document.getElementById('docTitle').getBoundingClientRect();
 return {kids:out, titleW:Math.round(ti.width), barW:Math.round(t.getBoundingClientRect().width)};})()""")))

# uji Guides switch + Export + round-trip
ev("document.querySelector('.dock-tab[data-pane=look]').click()"); time.sleep(0.6)
print("guides:", json.dumps(ev("""(()=>{const g=document.getElementById('guidesBtn');
   const before=document.getElementById('stage').classList.contains('is-guides');
   g.checked=true; g.dispatchEvent(new Event('change',{bubbles:true}));
   const after=document.getElementById('stage').classList.contains('is-guides');
   g.checked=false; g.dispatchEvent(new Event('change',{bubbles:true}));
   return {before, after, label:g.closest('.switch').textContent.trim()};})()""")))

ev("document.querySelector('.dock-tab[data-pane=json]').click()"); time.sleep(0.6)
print("export:", json.dumps(ev("({exists:!!document.getElementById('exportBtn'), text:document.getElementById('exportBtn').textContent})")))

print("roundtrip:", json.dumps(ev("(function(){\n  var t=document.getElementById('specBox');\n  var a=t.value;\n  var body=a.slice(a.indexOf('\\n')+1);\n  body=body.slice(0,body.lastIndexOf('\\n```'));\n  var s=window.Topo.parse(body);\n  var b=window.Topo.stringify(s);\n  return {same:a===('```topology\\n'+b+'\\n```'), len:a.length, blen:b.length};\n})()\n")))

print("exceptions:", exc if exc else "none")
proc.terminate()