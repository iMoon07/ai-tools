(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();
const page=targets.find(t=>t.type==='page');
const ws=new WebSocket(page.webSocketDebuggerUrl); let id=0; const p=new Map();
ws.onmessage=e=>{const m=JSON.parse(e.data); if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id);}};
await new Promise(r=>ws.onopen=r);
const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});
const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true}); return r.result&&r.result.result&&r.result.result.value};
await send('Runtime.enable'); await send('Page.enable');
await send('Page.navigate',{url:'file:///tmp/kilo/charttest/line.html'}); await new Promise(r=>setTimeout(r,1000));
const pt=await ev("(()=>{const s=document.querySelectorAll('.alur-donut-seg')[1];const r=s.getBoundingClientRect();const cx=r.left+r.width/2, cy=r.top+r.height/2;return {x:cx,y:r.top+2,cx,cy,w:r.width,h:r.height}})()");
console.log('pt',pt);
await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:pt.x,y:pt.y,buttons:0}); await new Promise(r=>setTimeout(r,300));
console.log('donutHover',await ev("(()=>{const tips=[...document.querySelectorAll('.alur-chart-tip')];return tips.map(t=>({hidden:t.hidden,text:t.textContent,place:t.getAttribute('data-place')}))})()"));
console.log('hoveredSeg',await ev("document.querySelectorAll('.alur-donut-seg.is-hover').length"));
ws.close();})();
