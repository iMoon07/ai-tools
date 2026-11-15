(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();const errs=[];ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}else if(m.method==='Runtime.exceptionThrown'){errs.push(m.params.exceptionDetails.text)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,500));return r.result&&r.result.result&&r.result.result.value};
await send('Runtime.enable');await send('Page.enable');await send('Page.navigate',{url:'file:///tmp/alur-probes/charttest/line.html'});await new Promise(r=>setTimeout(r,1200));
const pt=await ev("(()=>{const s=document.querySelectorAll('.alur-donut-seg')[1];const r=s.getBoundingClientRect();return{x:r.left+r.width/2,y:r.top+2}})()");
await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:pt.x,y:pt.y,buttons:0});await new Promise(r=>setTimeout(r,300));
console.log('hover',await ev("(()=>{const segs=[...document.querySelectorAll('.alur-donut-seg')];const h=document.querySelector('.alur-donut-seg.is-hover');const t=document.querySelectorAll('.alur-chart-tip')[1];return {tip:t.textContent,hovered:!!h,strokeW:getComputedStyle(segs[1]).strokeWidth,others:segs.filter(s=>s!==h).map(s=>getComputedStyle(s).opacity),total:document.querySelectorAll('.alur-donut-total')[0].textContent,label:document.querySelectorAll('.alur-donut-label')[0].textContent}})()"));
// leave
await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:5,y:5,buttons:0});await new Promise(r=>setTimeout(r,250));
console.log('reset',await ev("(()=>{const t=document.querySelectorAll('.alur-donut-total')[0];const l=document.querySelectorAll('.alur-donut-label')[0];return {total:t.textContent,label:l.textContent,hovered:document.querySelectorAll('.alur-donut-seg.is-hover').length}})()"));
// legend hover
const lp=await ev("(()=>{const s=document.querySelectorAll('.alur-legend-swatch')[2];const r=s.getBoundingClientRect();return{x:r.left+r.width/2,y:r.top+r.height/2}})()");
await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:lp.x,y:lp.y,buttons:0});await new Promise(r=>setTimeout(r,250));
console.log('legend',await ev("(()=>{return {hovered:document.querySelectorAll('.alur-donut-seg.is-hover').length,total:document.querySelectorAll('.alur-donut-total')[0].textContent,label:document.querySelectorAll('.alur-donut-label')[0].textContent}})()"));
console.log('errs',errs);
ws.close();})();
