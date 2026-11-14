import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9673; PROF="/tmp/kilo/prof-topom2"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=390,844","--remote-allow-origins=*","about:blank"],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def http(p,method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=method),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),method="PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=120,suppress_origin=True)
n=[0]; errs=[]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]:
            if r.get("method")=="Runtime.exceptionThrown":
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text")); print("   [EXC]", d.get("text"), (d.get("exception") or {}).get("description","")[:200])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:300])
    return res.get("value")
def tap(sel):
    r = ev("(()=>{const b=document.querySelector(%s); if(!b) return null; const r=b.getBoundingClientRect(); return {x:r.x+r.width/2,y:r.y+r.height/2,w:r.width,h:r.height};})()" % json.dumps(sel))
    if not r or not r['w']: print("  ! not tappable:", sel); return False
    send("Input.dispatchMouseEvent",type="mousePressed",x=r['x'],y=r['y'],button="left",clickCount=1,buttons=1,touchCount=1)
    send("Input.dispatchMouseEvent",type="mouseReleased",x=r['x'],y=r['y'],button="left",clickCount=1,buttons=0,touchCount=1)
    time.sleep(0.8); return True
send("Runtime.enable"); send("Page.enable")
send("Page.addScriptToEvaluateOnNewDocument", source="window.confirm=function(){return true;};window.alert=function(){};")
send("Emulation.setDeviceMetricsOverride",width=390,height=844,deviceScaleFactor=2,mobile=True)
send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(4.5)
print("nodes:", ev("document.querySelectorAll('#preview .topo-node').length"))
print("copy label:", ev("(()=>{const b=document.getElementById('copyBtn');return {long:getComputedStyle(b.querySelector('.copy-long')).display, short:getComputedStyle(b.querySelector('.copy-short')).display, w:Math.round(b.getBoundingClientRect().width)};})()"))
print("\n-- open panel --")
tap('#dockToggle')
print("dock:", ev("(()=>{const d=document.getElementById('dock');const r=d.getBoundingClientRect();const c=getComputedStyle(d);return {box:[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)],vis:c.visibility,open:d.classList.contains('is-open')};})()"))
print("tabs:", ev("[...document.querySelectorAll('.dock-tab')].map(b=>b.textContent.trim())"))
for t in ('edges','look','logos','json','nodes'):
    tap('.dock-tab[data-pane="%s"]' % t)
    print("  tab", t, "->", ev("(()=>{const p=document.querySelector('.pane.is-on');return p?p.getAttribute('data-pane'):'none';})()"))
print("\n-- starter + add node --")
print("preset options:", ev("document.getElementById('presetSel').options.length"))
print("preset values:", ev("[...document.getElementById('presetSel').options].map(o=>o.value+'|'+o.textContent.trim())"))
ev("(()=>{const s=document.getElementById('presetSel'); s.selectedIndex=1; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(1.2)
before = ev("document.querySelectorAll('#preview .topo-node').length")
tap('#addNode')
print("nodes:", before, "->", ev("document.querySelectorAll('#preview .topo-node').length"))
print("\n-- close panel --")
tap('#dockToggle')
print("dock open:", ev("document.getElementById('dock').classList.contains('is-open')"), "| vis:", ev("getComputedStyle(document.getElementById('dock')).visibility"))
print("\n-- stage scrollable --")
print(ev("(()=>{const s=document.getElementById('stage');return {sh:s.scrollHeight,ch:s.clientHeight,sw:s.scrollWidth,cw:s.clientWidth};})()"))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
