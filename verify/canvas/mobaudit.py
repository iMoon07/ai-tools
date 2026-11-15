import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9731
tmp=tempfile.mkdtemp(prefix="tph")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=390,844","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
cmd("Emulation.setDeviceMetricsOverride",width=390,height=844,deviceScaleFactor=2,mobile=True)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html?cb="+str(time.time())); time.sleep(3.5)
print('theme:', ev("document.body.className"))
ev("window._editor && (window._editor.tool='select')")
ev("(function(){var b=document.getElementById('themeToggle'); if(b) b.click();})()")
time.sleep(0.6)
print('theme now:', ev("({cls:document.body.className, bg:getComputedStyle(document.body).backgroundColor, stored:localStorage.getItem('ruang.theme.v1')})"))

AUDIT = """
(function(){
  var roots = document.querySelectorAll('.dock, .shape-panel, .topbar, .view-bar, .mobile-tabs-bar, #mobileTabs, .shortcut-card');
  function lum(r,g,b){ return (0.2126*r + 0.7152*g + 0.0722*b) / 255; }
  function parse(s){
    var m = String(s).match(/rgba?\\(([^)]+)\\)/); if(!m) return null;
    var p = m[1].split(',').map(function(x){ return parseFloat(x); });
    return {r:p[0], g:p[1], b:p[2], a: p.length>3 ? p[3] : 1};
  }
  function path(el){
    var out=[]; var n=el;
    for(var k=0;k<3 && n && n.tagName;k++){
      var s=(n.tagName||'').toLowerCase();
      if(n.id) s += '#'+n.id;
      if(n.getAttribute && n.getAttribute('class')) s += '.'+String(n.getAttribute('class')).trim().split(/\\s+/).join('.');
      out.unshift(s); n=n.parentElement;
    }
    return out.join(' > ');
  }
  var bad = [], seen = 0;
  Array.prototype.forEach.call(roots, function(root){
    if(!root || root.hidden) return;
    var all = [root].concat(Array.prototype.slice.call(root.querySelectorAll('*')));
    Array.prototype.forEach.call(all, function(el){
      var cs = getComputedStyle(el);
      if(cs.display === 'none' || cs.visibility === 'hidden') return;
      var r = el.getBoundingClientRect();
      if(!r.width || !r.height) return;
      var bg = parse(cs.backgroundColor);
      var op = parseFloat(cs.opacity);
      seen++;
      var darkBg = bg && bg.a > 0.05 && lum(bg.r,bg.g,bg.b) < 0.30;
      var lightText = (function(){ var c2 = parse(cs.color); return c2 && lum(c2.r,c2.g,c2.b) > 0.75; })();
      var isSvg = el.namespaceURI && String(el.namespaceURI).indexOf('svg') >= 0;
      var fill = null;
      if(isSvg){
        var f = cs.fill;
        if(f && f !== 'none'){ var pf = parse(f); if(pf) fill = pf; }
      }
      var darkFill = fill && fill.a > 0.05 && lum(fill.r,fill.b*0+fill.g,fill.b) < 0.30;
      if(darkBg || darkFill){
        bad.push({p:path(el), bg: bg?cs.backgroundColor:null, fill: fill?cs.fill:null,
                  color: cs.color, opacity: op,
                  w: Math.round(r.width), h: Math.round(r.height)});
      }
    });
  });
  return {seen: seen, bad: bad.slice(0, 60), total: bad.length};
})()
"""

def audit(tag):
    r = ev(AUDIT)
    print('---', tag, 'seen', r.get('seen'), 'bad', r.get('total'))
    for b in r.get('bad') or []:
        print('   ', b['p'], '| bg', b['bg'], '| fill', b['fill'], '| color', b['color'], '|', b['w'], 'x', b['h'])

audit('initial')
# select a node so the properties/shape panel opens
print('select:', ev("""(function(){var el=document.querySelector('.alur-canvas-node'); if(!el) return 'no node';
  var r=el.getBoundingClientRect();
  el.dispatchEvent(new PointerEvent('pointerdown',{clientX:r.x+r.width/2,clientY:r.y+r.height/2,button:0,buttons:1,pointerId:1,pointerType:'touch',bubbles:true}));
  el.dispatchEvent(new PointerEvent('pointerup',{clientX:r.x+r.width/2,clientY:r.y+r.height/2,button:0,buttons:0,pointerId:1,pointerType:'touch',bubbles:true}));
  return 'clicked';})()"""))
time.sleep(0.6)
audit('shape panel')
# view mode (read-only)
ev("document.body.classList.add('view-mode')")
time.sleep(0.5)
audit('view mode')
# open each mobile panel in turn
for name in ['tools', 'scene', 'assets', 'layers']:
    ev("""(function(){var b=document.querySelector('[data-open-panel=%s]'); if(b) b.click();})()""" % json.dumps(name))
    time.sleep(0.6)
    audit('panel ' + name)
    ev("""(function(){var b=document.querySelector('[data-open-panel=%s]'); if(b && b.classList.contains('is-on')) b.click();})()""" % json.dumps(name))
    time.sleep(0.4)
print('docks', ev("Array.prototype.map.call(document.querySelectorAll('.dock'),function(d){return {id:d.id, open:d.className, hidden:d.hidden};})"))
c.close(); proc.terminate()