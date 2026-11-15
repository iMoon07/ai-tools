import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9832; PROF="/tmp/alur-probes/prof-mob"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",f"--user-data-dir={PROF}",
 "--no-first-run","--no-default-browser-check","--disable-gpu","--window-size=390,844",
 "--remote-allow-origins=*","--hide-scrollbars","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
import websocket
def http(p,m="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=m),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),"PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=60,suppress_origin=True)
n=[0]; exc=[]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]: return r.get("result",{})
        if r.get("method")=="Runtime.exceptionThrown":
            d=r["params"]["exceptionDetails"]; exc.append(d.get("text","")+" "+(d.get("exception") or {}).get("description","")[:180])
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=390,height=844,deviceScaleFactor=2,mobile=True)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.0)

ev("document.getElementById('mobileFab').click()"); time.sleep(0.6)
print("menu:", json.dumps(ev("""(()=>{const m=document.getElementById('mobileMenu'); const r=m.getBoundingClientRect();
 return {hidden:m.hidden, h:Math.round(r.height), top:Math.round(r.top), iw:innerWidth,
   tabs:[].map.call(m.querySelectorAll('.mobile-tab'),t=>t.textContent),
   panes:[].map.call(m.querySelectorAll('.mobile-pane'),p=>[p.getAttribute('data-pane'),p.classList.contains('is-on')]),
   visibleItems:[].filter.call(m.querySelectorAll('.mobile-menu-item'),b=>b.offsetParent).length};})()""")))

for tab in ('tools','edit','view','panels'):
    ev("document.querySelector('.mobile-tab[data-mobile-tab=%s]').click()"%tab); time.sleep(0.4)
    print(tab, json.dumps(ev("""(()=>{const m=document.getElementById('mobileMenu');
     const on=m.querySelector('.mobile-pane.is-on');
     return {on:on?on.getAttribute('data-pane'):null,
       items:[].map.call(on.querySelectorAll('.mobile-menu-item'),b=>b.textContent.trim()),
       h:Math.round(m.getBoundingClientRect().height),
       scroll:m.scrollHeight>m.clientHeight};})()""")))

# pick a tool from the sheet
ev("document.querySelector('.mobile-tab[data-mobile-tab=tools]').click()"); time.sleep(0.3)
ev("document.querySelector('[data-mobile-tool=diamond]').click()"); time.sleep(0.6)
print("after pick diamond:", json.dumps(ev("""(()=>{const m=document.getElementById('mobileMenu');
 const t=document.getElementById('statusTool');
 return {menuHidden:m.hidden, tool:t?t.textContent:null};})()""")))

# open Scene panel from the sheet
ev("document.getElementById('mobileFab').click()"); time.sleep(0.5)
ev("document.querySelector('.mobile-tab[data-mobile-tab=panels]').click()"); time.sleep(0.3)
ev("document.querySelector('[data-mobile-panel=scene]').click()"); time.sleep(0.9)
print("scene sheet:", json.dumps(ev("""(()=>{const d=document.getElementById('panelScene'); const r=d.getBoundingClientRect();
 return {open:d.classList.contains('is-open'), top:Math.round(r.top), h:Math.round(r.height),
   w:Math.round(r.width), iw:innerWidth, ovfX:document.documentElement.scrollWidth>innerWidth};})()""")))
print("exc:", exc if exc else "none")
proc.terminate()
