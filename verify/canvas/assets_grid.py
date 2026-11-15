import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9670; PROF="/tmp/alur-probes/prof-assets"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1500,1000","--remote-allow-origins=*","about:blank"],
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
def click_id(cid):
    r = ev("(()=>{const b=document.getElementById('%s');const r=b.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2,vis:r.width>0};})()" % cid)
    if not r or not r.get('vis'):
        print("  !", cid, "not visible"); return
    send("Input.dispatchMouseEvent",type="mousePressed",x=r['x'],y=r['y'],button="left",clickCount=1,buttons=1)
    send("Input.dispatchMouseEvent",type="mouseReleased",x=r['x'],y=r['y'],button="left",clickCount=1,buttons=0)
    time.sleep(0.8)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.5)
def grid(): return ev("JSON.parse(document.getElementById('stage').getAttribute('data-spec')).grid")
def assets_open(): return ev("document.getElementById('panelAssets').classList.contains('is-open')")
print("toolbar assets button:", ev("(()=>{const b=document.querySelector('#editorBar [data-panel=assets]');return {title:b.title,name:b.getAttribute('data-name'),svg:!!b.querySelector('svg'),text:b.textContent.trim()};})()"))
print("dock head:", ev("document.querySelector('#panelAssets .dock-head b').textContent.trim()"), "| icon:", ev("getComputedStyle(document.querySelector('#panelAssets .dock-head b'),'::before').content"))
print("mobile entry:", ev("(()=>{const b=document.querySelector('[data-mobile-panel=assets]');return b?b.textContent.trim():'none';})()"))
print("grid btn:", ev("(()=>{const b=document.getElementById('gridToggle');return {on:b.classList.contains('is-on'),title:b.title,pe:getComputedStyle(b).pointerEvents};})()"))
print("\n-- click grid --"); click_id('gridToggle')
print("grid:", grid(), "| assets open:", assets_open(), "| btn:", ev("(()=>{const b=document.getElementById('gridToggle');return {on:b.classList.contains('is-on'),title:b.title};})()"))
print("-- click assets --"); click_id('gridToggle')  # restore grid first
ev("document.querySelector('#editorBar [data-panel=assets]').click()"); time.sleep(0.9)
print("assets open:", assets_open(), "| grid:", grid(), "| stage:", ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return [Math.round(r.x),Math.round(r.width)];})()"))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
