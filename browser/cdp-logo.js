(async()=>{
const targets=await (await fetch('http://127.0.0.1:9223/json')).json(); const page=targets.find(t=>t.type==='page'); const ws=new WebSocket(page.webSocketDebuggerUrl); let id=0; const p=new Map(); ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}}; await new Promise(r=>ws.onopen=r); const send=(method,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method,params}))}); const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,300));return r.result&&r.result.result&&r.result.result.value}; const mouse=(type,x,y,extra={})=>send('Input.dispatchMouseEvent',{type,x,y,button:'left',buttons:type==='mouseReleased'?0:1,clickCount:1,...extra}); await send('Runtime.enable'); await send('Page.enable'); await send('Page.reload',{ignoreCache:true}); await new Promise(r=>setTimeout(r,1200));
console.log('railButtons',await ev("[...document.querySelectorAll('#editorBar button')].map(b=>b.id||b.dataset.tool||b.dataset.panel).filter(Boolean)"));
console.log('zoomBar',await ev("!!document.querySelector('.zoom-bar')"));
console.log('dockBottom',await ev("getComputedStyle(document.getElementById('panelAssets')).bottom"));
// open assets
await ev("document.querySelector('#editorBar [data-panel=\\\"assets\\\"]').click()"); await new Promise(r=>setTimeout(r,200));
console.log('assetsOpen',await ev("document.getElementById('panelAssets').classList.contains('is-open')"));
const tile=await ev("(()=>{const t=document.querySelector('.logo-tile');if(!t)return null;const r=t.getBoundingClientRect();return{x:r.left+r.width/2,y:r.top+r.height/2,src:t.querySelector('img').src}})()");
console.log('tile',tile);
const stage=await ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return{x:r.left+r.width/2,y:r.top+r.height/2}})()");
console.log('stage',stage);
if(tile){await mouse('mousePressed',tile.x,tile.y);for(let i=1;i<=8;i++)await mouse('mouseMoved',tile.x+(stage.x-tile.x)*i/8,tile.y+(stage.y-tile.y)*i/8);await mouse('mouseReleased',stage.x,stage.y);}
await new Promise(r=>setTimeout(r,300));
console.log('nodes',await ev("document.querySelectorAll('.alur-canvas-node').length"));
console.log('logos',await ev("[...document.querySelectorAll('.alur-logo-img')].map(i=>i.getAttribute('src'))"));
console.log('selected',await ev("document.querySelectorAll('.alur-canvas-node.is-selected').length"));
console.log('shapeTitle',await ev("document.getElementById('shapePanelTitle').textContent"));
ws.close();})();
