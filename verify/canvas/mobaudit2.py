import json, time, urllib.request, subprocess, tempfile
import websocket
exec(open('mobaudit.py').read().split("AUDIT =")[0])

AUDIT = """
(function(){
  function lum(r,g,b){ return (0.2126*r + 0.7152*g + 0.0722*b) / 255; }
  function parse(s){
    var m = String(s).match(/rgba?\\(([^)]+)\\)/); if(!m) return null;
    var p = m[1].split(',').map(function(x){ return parseFloat(x); });
    return {r:p[0], g:p[1], b:p[2], a: p.length>3 ? p[3] : 1};
  }
  function path(el){
    var out=[], n=el;
    for(var k=0;k<3 && n && n.tagName;k++){
      var s=(n.tagName||'').toLowerCase();
      if(n.id) s += '#'+n.id;
      if(n.getAttribute && n.getAttribute('class')) s += '.'+String(n.getAttribute('class')).trim().split(/\\s+/).join('.');
      out.unshift(s); n=n.parentElement;
    }
    return out.join(' > ');
  }
  var bad=[], seen=0;
  Array.prototype.forEach.call(document.querySelectorAll('.dock, .shape-panel'), function(root){
    var all=[root].concat(Array.prototype.slice.call(root.querySelectorAll('*')));
    Array.prototype.forEach.call(all, function(el){
      var cs=getComputedStyle(el);
      if(cs.display==='none' || cs.visibility==='hidden') return;
      var r=el.getBoundingClientRect(); if(!r.width || !r.height) return;
      seen++;
      var bg=parse(cs.backgroundColor);
      var darkBg = bg && bg.a>0.05 && lum(bg.r,bg.g,bg.b) < 0.32;
      var img = cs.backgroundImage && cs.backgroundImage !== 'none' ? cs.backgroundImage : null;
      var darkImg = false;
      if(img){
        var nums = String(img).match(/rgba?\\([^)]+\\)/g) || [];
        darkImg = nums.some(function(c){
          var p = parse(c);
          return p && p.a > 0.05 && lum(p.r,p.g,p.b) < 0.32;
        });
      }
      var isSvg = el.namespaceURI && String(el.namespaceURI).indexOf('svg') >= 0;
      var fillDark = false, fillCss = null;
      if(isSvg){
        fillCss = cs.fill;
        if(fillCss && fillCss !== 'none'){ var pf = parse(fillCss); fillDark = !!(pf && pf.a>0.05 && lum(pf.r,pf.g,pf.b) < 0.32); }
      }
      if(darkBg || darkImg || fillDark){
        bad.push({p:path(el), bg:bg?cs.backgroundColor:null, img:img, fill:fillCss,
                  color:cs.color, w:Math.round(r.width), h:Math.round(r.height)});
      }
    });
  });
  return {seen:seen, total:bad.length, bad:bad.slice(0,25)};
})()
"""
def audit(tag):
    r = ev(AUDIT)
    print('---', tag, 'seen', r.get('seen'), 'bad', r.get('total'))
    for b in r.get('bad') or []:
        print('   ', b['p'], '| bg', b['bg'], '| img', b['img'], '| fill', b['fill'], '| color', b['color'], '|', b['w'], 'x', b['h'])

audit('light, all docks closed')
# select a node so properties dock has content, then force-open every dock
ev("""(function(){var el=document.querySelector('.alur-canvas-node'); var r=el.getBoundingClientRect();
  el.dispatchEvent(new PointerEvent('pointerdown',{clientX:r.x+r.width/2,clientY:r.y+r.height/2,button:0,buttons:1,pointerId:1,pointerType:'touch',bubbles:true}));
  el.dispatchEvent(new PointerEvent('pointerup',{clientX:r.x+r.width/2,clientY:r.y+r.height/2,button:0,buttons:0,pointerId:1,pointerType:'touch',bubbles:true}));})()""")
time.sleep(0.5)
ev("""(function(){Array.prototype.forEach.call(document.querySelectorAll('.dock'),function(d){d.hidden=false; d.classList.add('is-open'); d.scrollTop=0;});
  var sp=document.getElementById('shapePanel'); if(sp){ sp.hidden=false; } if(window.syncShapePanel) syncShapePanel();})()""")
time.sleep(0.8)
audit('light, every dock forced open')
c.close(); proc.terminate()
