(async function(){
  var wait=function(ms){return new Promise(function(r){setTimeout(r,ms);});};
  function pe(t,cx,cy,b){return new PointerEvent(t,{bubbles:true,cancelable:true,clientX:cx,clientY:cy,button:0,buttons:b,pointerId:1,pointerType:'mouse',isPrimary:true});}
  var key=function(o){document.body.dispatchEvent(new KeyboardEvent('keydown',Object.assign({bubbles:true,cancelable:true},o)));};
  var sel=function(){return Array.prototype.map.call(document.querySelectorAll('.alur-canvas-node.is-selected'),function(e){return e.getAttribute('data-node-id');});};
  var cnt=function(){return document.querySelectorAll('.alur-canvas-node').length;};
  var out={};
  var st=document.getElementById('stage'); var r=st.getBoundingClientRect();
  var el=document.elementFromPoint(300, Math.round(r.bottom-60));
  out.start=el?el.tagName+'.'+(el.getAttribute('class')||''):'none';
  el.dispatchEvent(pe('pointerdown',300,Math.round(r.bottom-60),1));
  document.dispatchEvent(pe('pointermove',600,300,1));
  document.dispatchEvent(pe('pointerup',600,300,0));
  await wait(150);
  out.afterMarquee=sel();
  key({key:'a',code:'KeyA',ctrlKey:true}); await wait(120);
  out.ctrlA=sel();
  key({key:'ArrowRight',code:'ArrowRight'}); await wait(120);
  out.nudgeRight=Array.prototype.map.call(document.querySelectorAll('.alur-canvas-node'),function(e){var m=/translate\(([-\d.]+)/.exec(e.getAttribute('transform')||'');return m?Math.round(+m[1]):'?';});
  var n0=cnt();
  key({key:'d',code:'KeyD',ctrlKey:true}); await wait(200);
  out.dupCount=n0+'->'+cnt();
  key({key:'z',code:'KeyZ',ctrlKey:true}); await wait(200);
  out.undoCount=cnt();
  key({key:'Delete',code:'Delete'}); await wait(200);
  out.afterDel=cnt();
  key({key:'z',code:'KeyZ',ctrlKey:true}); await wait(200);
  out.afterUndoDel=cnt();
  return out;
})()