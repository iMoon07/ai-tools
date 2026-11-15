import json, time, urllib.request, subprocess, tempfile
import websocket
exec(open('mobaudit.py').read().split("AUDIT =")[0])
ev("(function(){var el=document.querySelector('.alur-canvas-node'); var r=el.getBoundingClientRect(); el.dispatchEvent(new PointerEvent('pointerdown',{clientX:r.x+r.width/2,clientY:r.y+r.height/2,button:0,buttons:1,pointerId:1,pointerType:'touch',bubbles:true})); el.dispatchEvent(new PointerEvent('pointerup',{clientX:r.x+r.width/2,clientY:r.y+r.height/2,button:0,buttons:0,pointerId:1,pointerType:'touch',bubbles:true}));})()")
time.sleep(0.6)
print(ev("""(function(){var out=[];
  Array.prototype.forEach.call(document.querySelectorAll('#shapePanelBody input'), function(el){
    var cs=getComputedStyle(el);
    out.push({type:el.type, cls:el.className, id:el.id, bg:cs.backgroundColor, inline:el.getAttribute('style'),
              label:(el.closest('label')||{}).textContent ? el.closest('label').textContent.trim().slice(0,20) : null,
              parentCls: el.parentNode? String(el.parentNode.className):null});
  }); return out;})()"""))
print('---vars---')
print(ev("({field:getComputedStyle(document.body).getPropertyValue('--field-bg'), surface2:getComputedStyle(document.body).getPropertyValue('--surface-2')})"))
c.close(); proc.terminate()
