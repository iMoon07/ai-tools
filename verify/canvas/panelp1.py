import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9747
tmp=tempfile.mkdtemp(prefix="ppi")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=1400,900","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
    r=cmd("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1400,height=900,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html?cb="+str(time.time())); time.sleep(3.5)
ev("window.__errs=[];window.addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.4)

def ptr(t, x, y, buttons=1):
    ev("(function(){var s=document.getElementById('stage');"
       "s.dispatchEvent(new PointerEvent(" + json.dumps(t) + ",{bubbles:true,cancelable:true,"
       "clientX:%d,clientY:%d,button:0,buttons:%d,pointerId:1,pointerType:'mouse',isPrimary:true}));})()"
       % (x, y, buttons))

ST = ev("(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()")
def create(shape, dx, dy):
    ev("document.querySelector('[data-tool=\"" + shape + "\"]').click()")
    time.sleep(0.15)
    x0, y0 = ST['x'] + 250, ST['y'] + 280
    ptr("pointerdown", x0, y0)
    for k in range(1, 13):
        ptr("pointermove", x0 + dx * k / 12, y0 + dy * k / 12)
    ptr("pointerup", x0 + dx, y0 + dy, 0)
    time.sleep(0.5)
    return ev("(function(){var e=document.querySelectorAll('.alur-canvas-node');"
              "return e.length?e[e.length-1].getAttribute('data-node-id'):null;})()")

nid = create('box', 220, 120)
print('node', nid)
# select it
ev("(function(){var el=document.querySelector('.alur-canvas-node[data-node-id=\"%s\"]');"
   "var r=el.getBoundingClientRect();var s=document.getElementById('stage');"
   "s.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,clientX:%d,clientY:%d,button:0,buttons:1,pointerId:1,pointerType:'mouse',isPrimary:true}));"
   "s.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,cancelable:true,clientX:%d,clientY:%d,button:0,buttons:0,pointerId:1,pointerType:'mouse',isPrimary:true}));})()"
   % (nid, r_x := ST['x'] + 360, r_y := ST['y'] + 340, r_x, r_y))
time.sleep(0.5)

print(json.dumps(ev("""(function(){
  var host=document.getElementById('shapePanel');
  var rows=[].map.call(host.querySelectorAll('.prop-row'), function(r){
    return {label:(r.querySelector('.shape-label')||{}).textContent||null,
            btns:r.querySelectorAll('.prop-btn').length,
            on:r.querySelectorAll('.prop-btn.is-on').length};
  });
  return {hidden: host.hidden, rows: rows,
          selects: host.querySelectorAll('select').length,
          swatches: host.querySelectorAll('.swatch').length,
          hexes: host.querySelectorAll('.color-hex').length,
          title: (host.querySelector('.shape-head')||{}).textContent};
})()"""), indent=1))

def row(name):
    return "(function(){var rs=document.querySelectorAll('#shapePanel .prop-row');" \
           "for(var k=0;k<rs.length;k++){var l=rs[k].querySelector('.shape-label');" \
           "if(l&&l.textContent.trim()==='%s') return rs[k];}return null;})()" % name

# click the Artist sloppiness icon (2nd button of that row)
print('artist click ->', ev("(function(){var r=%s; if(!r) return 'no row';"
    "var b=r.querySelectorAll('.prop-btn')[1]; b.click(); return b.title;})()" % row('Sloppiness')))
time.sleep(0.5)
print('spec slop', ev("(function(){var n=window._state.spec.nodes[%s];return n.sloppiness;})()" % json.dumps(nid)))
print('rough paths', ev("(function(){var e=document.querySelector('.alur-canvas-node[data-node-id=\"%s\"]');return e.querySelectorAll('.alur-node-rough').length;})()" % nid))

# width bold
print('bold click ->', ev("(function(){var r=%s; var b=r.querySelectorAll('.prop-btn')[2]; b.click(); return b.title;})()" % row('Width')))
time.sleep(0.4)
print('strokeWidth', ev("(function(){var n=window._state.spec.nodes[%s];return n.strokeWidth;})()" % json.dumps(nid)))

# background colour quick swatch (#a5d8ff is 4th quick)
print('bg ->', ev("(function(){var r=%s; var s=r.querySelectorAll('.swatch');"
    "for(var k=0;k<s.length;k++){ if(s[k].dataset.color==='#a5d8ff'){ s[k].click(); return s[k].dataset.color; } }"
    "return 'not found';})()" % row('Background')))
time.sleep(0.5)
print('fill', ev("(function(){var n=window._state.spec.nodes[%s];return n.fill;})()" % json.dumps(nid)))
print('fill style row?', ev("(function(){var rs=document.querySelectorAll('#shapePanel .prop-row');"
    "for(var k=0;k<rs.length;k++){var l=rs[k].querySelector('.shape-label');"
    "if(l&&l.textContent.trim()==='Fill') return rs[k].querySelectorAll('.prop-btn').length;}return -1;})()"))

# open the colour popover
print('open pop ->', ev("(function(){var r=%s; var b=r.querySelector('.color-open'); b.click();"
    "var p=document.querySelector('.color-pop'); return p? {pal:p.querySelectorAll('.pal .swatch').length,"
    "shades:p.querySelectorAll('.shades .swatch').length, hex:!!p.querySelector('.color-hex')}:null;})()" % row('Stroke')))
time.sleep(0.3)
print('pop pick ->', ev("(function(){var p=document.querySelector('.color-pop');"
    "var s=p.querySelectorAll('.pal .swatch'); s[1].click();"
    "return {closed: !document.querySelector('.color-pop')};})()"))
time.sleep(0.5)
print('stroke color', ev("(function(){var n=window._state.spec.nodes[%s];return n.color;})()" % json.dumps(nid)))

# edge panel
ptr("pointerdown", ST['x'] + 60, ST['y'] + 500)
ptr("pointerup", ST['x'] + 60, ST['y'] + 500, 0)
time.sleep(0.3)
print('errs', ev("window.__errs"))
c.close(); proc.terminate()