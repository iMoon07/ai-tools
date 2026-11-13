(async()=>{
const targets=await (await fetch('http://127.0.0.1:9223/json')).json();
const page=targets.find(t=>t.type==='page');
const ws=new WebSocket(page.webSocketDebuggerUrl);
let id=0; const pending=new Map();
ws.onmessage=e=>{const m=JSON.parse(e.data); if(m.id&&pending.has(m.id)){pending.get(m.id)(m);pending.delete(m.id)}};
await new Promise(r=>ws.onopen=r);
function send(method,params={}){return new Promise(res=>{const i=++id;pending.set(i,res);ws.send(JSON.stringify({id:i,method,params}))})}
async function ev(expr){const r=await send('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true});return r.result&&r.result.result&&r.result.result.value}
async function key(k,code,mods=[]){const p={type:'keyDown',key:k,code,windowsVirtualKeyCode:k.toUpperCase().charCodeAt(0)};for(const m of mods)p[m]=true;await send('Input.dispatchKeyEvent',p);await send('Input.dispatchKeyEvent',{...p,type:'keyUp'});}
async function mouse(type,x,y,extra={}){await send('Input.dispatchMouseEvent',{type,x,y,button:'left',buttons:type==='mouseReleased'?0:1,clickCount:1,...extra})}
await send('Runtime.enable'); await send('Page.enable');
await send('Page.reload',{ignoreCache:true}); await new Promise(r=>setTimeout(r,1200));
console.log('title',await ev('document.title'));
console.log('topActions',await ev("!!document.querySelector('.top-actions')"));
console.log('shortcutOld',await ev("document.getElementById('shortcutCard').textContent.includes('insert image')"));
console.log('panelSide',await ev("getComputedStyle(document.getElementById('panelAssets')).bottom"));
// reset scene via Ctrl+Delete? first click body
await ev('document.body.focus()');
await mouse('mousePressed',700,400); await mouse('mouseReleased',700,400);
await key('Delete','Delete',['ctrl']);
await new Promise(r=>setTimeout(r,100));
// draw line
await ev("document.querySelector('[data-tool=\\\"line\\\"]').click()");
await mouse('mousePressed',300,300);
for(let i=1;i<=6;i++) await mouse('mouseMoved',300+i*30,300+i*10);
await mouse('mouseReleased',480,360);
await new Promise(r=>setTimeout(r,100));
console.log('afterLine',await ev("({edges:document.querySelectorAll('.alur-canvas-edge').length,status:document.getElementById('topStatus').textContent,tool:document.getElementById('editorMode').textContent})"));
// draw arrow
await ev("document.querySelector('[data-tool=\\\"arrow\\\"]').click()");
await mouse('mousePressed',300,420);
for(let i=1;i<=6;i++) await mouse('mouseMoved',300+i*30,420-i*5);
await mouse('mouseReleased',480,390);
await new Promise(r=>setTimeout(r,100));
console.log('afterArrow',await ev("({edges:document.querySelectorAll('.alur-canvas-edge').length,status:document.getElementById('topStatus').textContent})"));
// ctrl+a
await key('a','KeyA',['ctrl']); await new Promise(r=>setTimeout(r,100));
console.log('ctrlA',await ev("({sel:document.querySelectorAll('.alur-canvas-node.is-selected').length,edges:document.querySelectorAll('.alur-canvas-edge.is-selected').length,layers:document.getElementById('layerList').textContent})"));
// delete
await key('Delete','Delete'); await new Promise(r=>setTimeout(r,150));
console.log('del',await ev("({edges:document.querySelectorAll('.alur-canvas-edge').length,nodes:document.querySelectorAll('.alur-canvas-node').length,layers:document.getElementById('layerList').textContent})"));
ws.close();
})();
