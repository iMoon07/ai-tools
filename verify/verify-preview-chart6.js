(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,500));return r.result&&r.result.result&&r.result.result.value};
await send('Runtime.enable');await send('Page.enable');await send('Page.navigate',{url:'file:///home/moon/Projects/imoon07.github.io/preview.html'});await new Promise(r=>setTimeout(r,1600));
await ev("localStorage.removeItem('ruang.scene.v1')");await send('Page.reload',{ignoreCache:true});await new Promise(r=>setTimeout(r,1600));
await ev("document.querySelector('[data-panel=\\\"assets\\\"]').click()");await new Promise(r=>setTimeout(r,250));
await ev("document.querySelector('[data-insert-module=\\\"chart\\\"]').click()");await new Promise(r=>setTimeout(r,900));
await ev("document.getElementById('shapePanel').hidden=true");
console.log(await ev("(()=>{const d=document.querySelector('.alur-module-embed[data-module=\\\"chart\\\"] .alur-line-dot');const r=d.getBoundingClientRect();const els=document.elementsFromPoint(r.left+r.width/2,r.top+r.height/2);return {dot:[r.left,r.top,r.width,r.height],els:els.slice(0,8).map(e=>({tag:e.tagName,id:e.id,cls:e.getAttribute('class')}))}})()"));
ws.close();})();
