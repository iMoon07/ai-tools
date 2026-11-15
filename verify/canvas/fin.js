(async function(){
  var wait=function(ms){return new Promise(function(r){setTimeout(r,ms);});};
  var errs=[]; window.addEventListener('error',function(e){errs.push(String(e.message));});
  document.querySelector('[data-tool="text"]').click(); await wait(100);
  var st=document.getElementById('stage'); var r=st.getBoundingClientRect();
  var x=Math.round(r.left+300), y=Math.round(r.top+430);
  function pe(t,cx,cy,b){return new PointerEvent(t,{bubbles:true,cancelable:true,clientX:cx,clientY:cy,button:0,buttons:b,pointerId:1,pointerType:'mouse',isPrimary:true});}
  var el=document.elementFromPoint(x,y);
  el.dispatchEvent(pe('pointerdown',x,y,1)); document.dispatchEvent(pe('pointerup',x,y,0));
  await wait(200);
  var area=document.getElementById('inlineText');
  area.value='underlined';
  area.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',code:'Enter',bubbles:true}));
  await wait(250);
  var last=document.querySelectorAll('.alur-canvas-node');
  var id=last[last.length-1].getAttribute('data-node-id');
  var lbl=document.querySelector('[data-node-id="'+id+'"] .alur-node-label');
  var before=lbl?lbl.getAttribute('text-decoration'):null;
  var panel=document.getElementById('shapePanelBody');
  var btns=Array.prototype.map.call(panel.querySelectorAll('button'),function(b){return b.textContent;});
  var u=Array.prototype.filter.call(panel.querySelectorAll('button'),function(b){return b.textContent==='U';})[0];
  if(u) u.click();
  await wait(250);
  var lbl2=document.querySelector('[data-node-id="'+id+'"] .alur-node-label');
  return {id:id, before:before, after:lbl2?lbl2.getAttribute('text-decoration'):null,
    buttons:btns, fontRow:/Font/.test(panel.textContent), errs:errs};
})()