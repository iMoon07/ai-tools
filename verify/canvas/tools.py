import json, sys, time, urllib.request, subprocess, tempfile
import websocket
PORT=int(sys.argv[1]); W=int(sys.argv[2]); H=int(sys.argv[3])
tmp=tempfile.mkdtemp(prefix="tl")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=%d,%d"%(W,H),"about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
for _ in range(80):
    try:
        urllib.request.urlopen("http://127.0.0.1:%d/json/version"%PORT,timeout=1).read(); break
    except Exception: time.sleep(0.25)
tabs=json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json"%PORT).read())
page=[t for t in tabs if t["type"]=="page"][0]
c=websocket.create_connection(page["webSocketDebuggerUrl"],timeout=30)
i=[0]
def cmd(m,**p):
    i[0]+=1; c.send(json.dumps({"id":i[0],"method":m,"params":p}))
    while True:
        r=json.loads(c.recv())
        if r.get("id")==i[0]: return r.get("result",{})
def ev(e):
    r=cmd("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)["result"]
    if r.get("subtype")=="error": print("JS ERROR:",r.get("description"))
    return r.get("value")
def spec():
    return ev("JSON.parse(document.getElementById('stage').getAttribute('data-spec')||'{}')")
def drag(x0,y0,x1,y1):
    cmd("Input.dispatchMouseEvent", type="mousePressed", x=x0, y=y0, button="left", clickCount=1)
    for k in range(1,6):
        cmd("Input.dispatchMouseEvent", type="mouseMoved",
            x=x0+(x1-x0)*k/5.0, y=y0+(y1-y0)*k/5.0, button="left", buttons=1)
        time.sleep(0.03)
    cmd("Input.dispatchMouseEvent", type="mouseReleased", x=x1, y=y1, button="left", clickCount=1)
    time.sleep(0.35)

cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=W<600)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")

def scene():
    s = spec()
    kinds = {}
    for k,n in (s.get('nodes') or {}).items():
        kinds[n.get('shape') or n.get('module') or '?'] = kinds.get(n.get('shape') or n.get('module') or '?',0)+1
    return {"nodes": len(s.get('nodes') or {}), "edges": len(s.get('edges') or []),
            "drawings": len(s.get('drawings') or []), "kinds": kinds}

print("== %dx%d ==" % (W,H), "start:", scene())

def use(tool):
    ev("document.querySelector('[data-tool=\"%s\"]').click()" % tool)

# box
use('box'); drag(200,200,380,320)
print("box   ->", scene())
# diamond
use('diamond'); drag(450,200,610,320)
print("diamond ->", scene())
# circle
use('circle'); drag(200,400,340,520)
print("circle ->", scene())
# arrow between two nodes
use('arrow'); drag(290,260,530,260)
print("arrow ->", scene())
# text
use('text'); drag(650,400,760,440)
print("text  ->", scene())
# draw
use('draw'); drag(700,500,820,600)
print("draw  ->", scene())
# select + delete once
use('select')
ev("document.querySelector('#stage .alur-canvas-node').dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,clientX:0,clientY:0,pointerId:1,button:0,isPrimary:true}))")
time.sleep(0.2)
before = scene()
ev("document.dispatchEvent(new KeyboardEvent('keydown',{key:'Delete',bubbles:true}))")
time.sleep(0.4)
after = scene()
print("delete -> %s nodes => %s nodes" % (before['nodes'], after['nodes']))
print("doc:", ev("({sw:document.documentElement.scrollWidth, iw:innerWidth})"))
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
