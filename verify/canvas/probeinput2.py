import json, time, urllib.request, subprocess, tempfile
import websocket
exec(open('mobaudit.py').read().split("AUDIT =")[0])
cmd("Emulation.setDeviceMetricsOverride",width=1400,height=900,deviceScaleFactor=1,mobile=False)
ev("(function(){var b=document.getElementById('themeToggle'); if(b && document.body.className.indexOf('theme--light')<0) b.click();})()")
time.sleep(0.5)
ev("""(function(){Array.prototype.forEach.call(document.querySelectorAll('.dock'),function(d){d.hidden=false; d.classList.add('is-open');}); var sp=document.getElementById('shapePanel'); if(sp) sp.hidden=false; if(window.syncShapePanel) syncShapePanel();})()""")
time.sleep(0.6)
ev("""(function(){var el=document.querySelector('.alur-canvas-node'); var r=el.getBoundingClientRect();
  el.dispatchEvent(new PointerEvent('pointerdown',{clientX:r.x+r.width/2,clientY:r.y+r.height/2,button:0,buttons:1,pointerId:1,pointerType:'touch',bubbles:true}));
  el.dispatchEvent(new PointerEvent('pointerup',{clientX:r.x+r.width/2,clientY:r.y+r.height/2,button:0,buttons:0,pointerId:1,pointerType:'touch',bubbles:true}));})()""")
time.sleep(0.6)
print(ev("""(function(){var b=document.getElementById('shapePanelBody');
  return {title:document.getElementById('shapePanelTitle').textContent,
          html: b.innerHTML.replace(/\\s+/g,' ').slice(0,1400)};})()"""))
c.close(); proc.terminate()
