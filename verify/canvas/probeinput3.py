import json, time, urllib.request, subprocess, tempfile
import websocket
exec(open('mobaudit.py').read().split("AUDIT =")[0])
cmd("Emulation.setDeviceMetricsOverride",width=1400,height=900,deviceScaleFactor=1,mobile=False)
print(ev("(function(){var b=document.getElementById('themeToggle'); if(b && document.body.className.indexOf('theme--light')<0) b.click(); return document.body.className;})()"))
time.sleep(0.6)
print(ev("""(function(){Array.prototype.forEach.call(document.querySelectorAll('.dock'),function(d){d.hidden=false; d.classList.add('is-open');}); var sp=document.getElementById('shapePanel'); if(sp) sp.hidden=false; if(window._sync) window._sync();})()"""))
time.sleep(0.6)
# select node via keyboard-free API: click with mouse events on first node
print(ev("""(function(){var el=document.querySelector('.alur-canvas-node'); var r=el.getBoundingClientRect();
  el.dispatchEvent(new PointerEvent('pointerdown',{clientX:r.x+r.width/2,clientY:r.y+r.height/2,button:0,buttons:1,pointerId:1,pointerType:'touch',bubbles:true}));
  el.dispatchEvent(new PointerEvent('pointerup',{clientX:r.x+r.width/2,clientY:r.y+r.height/2,button:0,buttons:0,pointerId:1,pointerType:'touch',bubbles:true}));
  return {sel: window._state.spec.selected, tool: window._editor.tool};})()"""))
time.sleep(0.7)
ev("window._sync && window._sync()")
time.sleep(0.4)
print(json.dumps(ev("""(function(){var out=[];
  Array.prototype.forEach.call(document.querySelectorAll('#shapePanelBody label.shape-group > input'), function(el){
    var cs=getComputedStyle(el);
    out.push({type:el.type, value:el.value, bg:cs.backgroundColor, fieldBg:cs.getPropertyValue('--field-bg'),
              bodyCls:document.body.className, inLight:!!el.closest('body.theme--light'),
              minH: Math.round(el.getBoundingClientRect().height)});
  });
  return {count:out.length, items:out, title:document.getElementById('shapePanelTitle').textContent};})()"""), indent=1))
c.close(); proc.terminate()
