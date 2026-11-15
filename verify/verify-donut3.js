(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();const errs=[];ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}else if(m.method==='Runtime.exceptionThrown'){errs.push(m.params.exceptionDetails.text)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});return r.result&&r.result.result&&r.result.result.value};
await send('Runtime.enable');await send('Page.enable');await send('Emulation.setTouchEmulationEnabled',{enabled:true,maxTouchPoints:5});await send('Page.navigate',{url:'file:///tmp/alur-probes/charttest/line.html'});await new Promise(r=>setTimeout(r,1200));
await ev("document.querySelectorAll('.alur')[1].scrollIntoView({block:'center',behavior:'instant'})");await new Promise(r=>setTimeout(r,400));
const pt=await ev("(()=>{const s=document.querySelectorAll('.alur-donut-seg')[1];const r=s.getBoundingClientRect();const cx=r.left+r.width/2,cy=r.top+r.height/2,rad=r.width/2-8;for(let a=0;a<360;a+=10){const x=cx+rad*Math.cos(a*Math.PI/180),y=cy+rad*Math.sin(a*Math.PI/180);const el=document.elementFromPoint(x,y);if(el&&el.classList&&el.classList.contains('alur-donut-seg')&&[...document.querySelectorAll('.alur-donut-seg')].indexOf(el)===1)return{x,y}}return null})()");
console.log('pt',pt);
await send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:pt.x,y:pt.y}]});await new Promise(r=>setTimeout(r,200));
await send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await new Promise(r=>setTimeout(r,400));
console.log('afterTap',await ev("(()=>{const h=document.querySelector('.alur-donut-seg.is-hover');return {hovered:!!h,idx:h?[...document.querySelectorAll('.alur-donut-seg')].indexOf(h):null,total:document.querySelectorAll('.alur-donut-total')[0].textContent,label:document.querySelectorAll('.alur-donut-label')[0].textContent}})()"));
// legend hover
const lp=await ev("(()=>{const s=document.querySelectorAll('.alur-legend-swatch')[2];const r=s.getBoundingClientRect();return{x:r.left+r.width/2,y:r.top+r.height/2}})()");
await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:lp.x,y:lp.y,buttons:0});await new Promise(r=>setTimeout(r,250));
console.log('legend',await ev("(()=>{const h=document.querySelector('.alur-donut-seg.is-hover');return {hovered:!!h,idx:h?[...document.querySelectorAll('.alur-donut-seg')].indexOf(h):null,total:document.querySelectorAll('.alur-donut-total')[0].textContent,label:document.querySelectorAll('.alur-donut-label')[0].textContent}})()"));
console.log('errs',errs);
ws.close();})();
