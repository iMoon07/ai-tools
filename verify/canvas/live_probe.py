import json, subprocess, time, urllib.parse, urllib.request, shutil, base64
PORT=9553; PROF="/tmp/kilo/prof-live"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1500,1000","--remote-allow-origins=*","about:blank"],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
import websocket
def http(p,method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=method),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),method="PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=60,suppress_origin=True)
n=[0]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]:
            if r.get("method")=="Runtime.exceptionThrown":
                d=r["params"]["exceptionDetails"]
                print("[EXC]", d.get("text"), (d.get("exception") or {}).get("description","")[:160])
            if r.get("error"): raise RuntimeError(r["error"])
            return r.get("result",{})
def ev(expr):
    r=send("Runtime.evaluate",expression=expr,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    return res.get("value", res.get("description"))
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/topology.html")
time.sleep(3.5)
print("tabs:", ev("[...document.querySelectorAll('.dock-tab')].map(t=>t.textContent)"))
print("top buttons:", ev("[...document.querySelectorAll('.top-right button')].map(b=>b.textContent)"))
print("brand:", ev("document.querySelector('.brand').textContent.replace(/\\s+/g,' ').trim()"))
print("specBox fontsize:", ev("getComputedStyle(document.getElementById('specBox')).fontSize"))
print("specBox h:", ev("document.getElementById('specBox').getBoundingClientRect().height"))
# go to topology tab
ev("document.querySelector('.dock-tab[data-pane=json]').click()")
time.sleep(0.6)
print("status:", ev("document.getElementById('codeStatus').textContent + ' | ' + document.getElementById('codeStatus').className"))
print("starts with fence:", ev("document.getElementById('specBox').value.slice(0,13)"))
# edit: change node label live
ev("""(()=>{const b=document.getElementById('specBox');b.focus();
const i=b.value.indexOf('"Customer"'); b.value=b.value.slice(0,i)+'"Pengunjung"'+b.value.slice(i+10);
b.dispatchEvent(new Event('input',{bubbles:true}));})()""")
time.sleep(0.9)
print("after edit nodes:", ev("document.querySelectorAll('#preview .topo-node').length"))
print("after edit label:", ev("[...document.querySelectorAll('#preview .topo-node')].map(n=>n.textContent.trim().slice(0,14))"))
print("status2:", ev("document.getElementById('codeStatus').textContent"))
# invalid JSON
ev("""(()=>{const b=document.getElementById('specBox');b.focus();b.value='```topology\\n{ nope';b.dispatchEvent(new Event('input',{bubbles:true}));})()""")
time.sleep(0.9)
print("bad status:", ev("document.getElementById('codeStatus').textContent"), "|", ev("document.getElementById('codeStatus').className"))
print("canvas still alive:", ev("document.querySelectorAll('#preview .topo-node').length"))
# blur normalises
ev("""(()=>{const b=document.getElementById('specBox');b.focus();b.value='```topology\\n{\"vertical\":true,\"columns\":[[\"A\"],[\"B\"]],\"nodes\":{\"A\":[\"One\",\"a\",\"x\"],\"B\":[\"Two\",\"b\",\"x\"]},\"edges\":[{\"from\":\"A\",\"to\":\"B\",\"badge\":\"go\"}]}\\n```';b.dispatchEvent(new Event('input',{bubbles:true}));})()""")
time.sleep(0.9)
ev("document.getElementById('specBox').blur()")
time.sleep(0.5)
print("normalised:", repr(ev("document.getElementById('specBox').value.slice(0,30)")))
print("status3:", ev("document.getElementById('codeStatus').textContent"))
print("nodes:", ev("document.querySelectorAll('#preview .topo-node').length"))
ws.close(); proc.terminate()
