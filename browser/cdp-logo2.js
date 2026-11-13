(async()=>{
const targets=await (await fetch('http://127.0.0.1:9223/json')).json(); const page=targets.find(t=>t.type==='page'); const ws=new WebSocket(page.webSocketDebuggerUrl); let id=0; const p=new Map(); ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}}; await new Promise(r=>ws.onopen=r); const send=(method,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method,params}))}); const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,400));return r.result&&r.result.result&&r.result.result.value}; await send('Runtime.enable'); await send('Page.enable'); await send('Page.reload',{ignoreCache:true}); await new Promise(r=>setTimeout(r,1000));
await ev("document.querySelector('#editorBar [data-panel=\\\"assets\\\"]').click()"); await new Promise(r=>setTimeout(r,200));
// click tile directly
const tile=await ev("(()=>{const t=document.querySelector('.logo-tile');const r=t.getBoundingClientRect();return{x:r.left+r.width/2,y:r.top+r.height/2,id:t.title}})()");
const mouse=(type,x,y)=>send('Input.dispatchMouseEvent',{type,x,y,button:'left',buttons:type==='mouseReleased'?0:1,clickCount:1});
await mouse('mousePressed',tile.x,tile.y); await mouse('mouseReleased',tile.x,tile.y); await new Promise(r=>setTimeout(r,300));
console.log('clickResult',await ev("({nodes:document.querySelectorAll('.alur-canvas-node').length,logos:[...document.querySelectorAll('.alur-logo-img')].map(i=>i.getAttribute('src')),title:document.getElementById('shapePanelTitle').textContent})"));
ws.close();})();
