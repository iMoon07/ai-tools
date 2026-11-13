(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();const errs=[];ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}else if(m.method==='Runtime.exceptionThrown'){errs.push(m.params.exceptionDetails.text)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,500));return r.result&&r.result.result&&r.result.result.value};
await send('Runtime.enable');await send('Page.enable');await send('Page.navigate',{url:'file:///home/moon/Projects/imoon07.github.io/preview.html'});await new Promise(r=>setTimeout(r,1600));
await ev("document.querySelector('[data-panel=\\\"assets\\\"]').click()");await new Promise(r=>setTimeout(r,250));
await ev("document.querySelector('[data-insert-module=\\\"chart\\\"]').click()");await new Promise(r=>setTimeout(r,900));
console.log('embeds',await ev("document.querySelectorAll('.alur-module-embed[data-module=\\\"chart\\\"]').length"));
const before=await ev("document.querySelector('.alur-module-node').getAttribute('transform')");
const pt=await ev("(()=>{const b=document.querySelector('.alur-module-embed[data-module=\\\"chart\\\"] .alur-bar');if(!b)return null;const r=b.getBoundingClientRect();return{x:r.left+r.width/2,y:r.top+r.height/2}})()");
console.log('pt',pt);
if(pt){await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:pt.x,y:pt.y,buttons:0});await new Promise(r=>setTimeout(r,350));}
console.log('hover',await ev("(()=>{const t=document.querySelector('.alur-chart-tip');const h=document.querySelector('.alur-module-embed[data-module=\\\"chart\\\"] .alur-bar.is-hover');return {tipHidden:t&&t.hidden,text:t&&t.textContent,hovered:!!h}})()"));
const after=await ev("document.querySelector('.alur-module-node').getAttribute('transform')");
console.log('transformSame',before===after,before,after);
console.log('errs',errs);
ws.close();})();
