(async function(){
  var wait=function(ms){return new Promise(function(r){setTimeout(r,ms);});};
  function pe(t,cx,cy,b){return new PointerEvent(t,{bubbles:true,cancelable:true,clientX:cx,clientY:cy,button:0,buttons:b,pointerId:1,pointerType:'mouse',isPrimary:true});}
  var sel=function(){return Array.prototype.map.call(document.querySelectorAll('.alur-canvas-node.is-selected'),function(e){return e.getAttribute('data-node-id');});};
  var pos=function(){return Array.prototype.map.call(document.querySelectorAll('.alur-canvas-node'),function(e){var m=/translate\(([-\d.]+) ([-\d.]+)\)/.exec(e.getAttribute('transform')||'');return e.getAttribute('data-node-id')+'='+(m?Math.round(+m[1])+','+Math.round(+m[2]):'?');});};
  var out={};
  document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'a',code:'KeyA',ctrlKey:true,bubbles:true,cancelable:true}));
  await wait(200);
  out.afterCtrlA=sel();
  var a=document.querySelector('[data-node-id="n1"]').getBoundingClientRect();
  var b=document.querySelector('[data-node-id="n3"]').getBoundingClientRect();
  var x=Math.round(a.right+40), y=Math.round(a.top+a.height/2);
  out.hit=document.elementFromPoint(x,y).getAttribute('class')+' @'+x+','+y;
  out.before=pos();
  var el=document.elementFromPoint(x,y);
  el.dispatchEvent(pe('pointerdown',x,y,1));
  document.dispatchEvent(pe('pointermove',x-30,y+20,1));
  document.dispatchEvent(pe('pointermove',x-60,y+40,1));
  document.dispatchEvent(pe('pointerup',x-60,y+40,0));
  await wait(200);
  out.after=pos();
  out.selAfter=sel();
  out.marqueeGone=!document.querySelector('.alur-marquee');
  return out;
})()