(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});return r.result&&r.result.result&&r.result.result.value};
await send('Runtime.enable');await send('Page.enable');await send('Page.navigate',{url:'file:///tmp/alur-probes/charttest/index.html'});await new Promise(r=>setTimeout(r,1000));
const pt=await ev("(()=>{const b=document.querySelector('.alur-bar');const r=b.getBoundingClientRect();return{x:r.left+r.width/2,y:r.top+r.height/2}})()");
await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:pt.x,y:pt.y,buttons:0});await new Promise(r=>setTimeout(r,250));
console.log(await ev("(()=>{const t=document.querySelector('.alur-chart-tip');const d=t.querySelector('.alur-chart-tip-dot');return {text:t.textContent,dot:!!d,bg:d&&d.style.background,w:t.offsetWidth,h:t.offsetHeight}})()"));
ws.close();})();
