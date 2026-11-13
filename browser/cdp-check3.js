(async()=>{
const targets=await (await fetch('http://127.0.0.1:9223/json')).json();
const page=targets.find(t=>t.type==='page');
const ws=new WebSocket(page.webSocketDebuggerUrl);
let id=0; const pending=new Map();
ws.onmessage=e=>{const m=JSON.parse(e.data); if(m.id&&pending.has(m.id)){pending.get(m.id)(m);pending.delete(m.id)}};
await new Promise(r=>ws.onopen=r);
function send(method,params={}){return new Promise(res=>{const i=++id;pending.set(i,res);ws.send(JSON.stringify({id:i,method,params}))})}
async function ev(expr){const r=await send('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails) console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,500));return r.result&&r.result.result&&r.result.result.value}
async function key(k,code,mods=[]){const p={type:'keyDown',key:k,code,windowsVirtualKeyCode:k.toUpperCase().charCodeAt(0)};for(const m of mods)p[m]=true;await send('Input.dispatchKeyEvent',p);await send('Input.dispatchKeyEvent',{...p,type:'keyUp'});}
async function mouse(type,x,y,extra={}){await send('Input.dispatchMouseEvent',{type,x,y,button:'left',buttons:type==='mouseReleased'?0:1,clickCount:1,...extra})}
await send('Runtime.enable'); await send('Page.enable');
await send('Page.reload',{ignoreCache:true}); await new Promise(r=>setTimeout(r,1200));
await ev('document.body.focus()');
await mouse('mousePressed',700,400); await mouse('mouseReleased',700,400);
await key('Delete','Delete',['ctrl']); await new Promise(r=>setTimeout(r,100));
await ev("document.querySelector('[data-tool=\\\"line\\\"]').click()");
await mouse('mousePressed',300,300);
for(let i=1;i<=6;i++) await mouse('mouseMoved',300+i*30,300+i*10);
await mouse('mouseReleased',480,360); await new Promise(r=>setTimeout(r,150));
console.log('lineEdges',await ev("document.querySelectorAll('.alur-canvas-edge').length"));
console.log('mid',await ev("(()=>{const h=document.querySelector('.alur-edge-point.is-mid'); if(!h)return null; const r=h.getBoundingClientRect(); return {x:r.left+r.width/2,y:r.top+r.height/2};})()"));
const h=await ev("(()=>{const h=document.querySelector('.alur-edge-point.is-mid'); if(!h)return null; const r=h.getBoundingClientRect(); return {x:r.left+r.width/2,y:r.top+r.height/2};})()");
if(h){await mouse('mousePressed',h.x,h.y);for(let i=1;i<=5;i++)await mouse('mouseMoved',h.x+i*12,h.y+i*8);await mouse('mouseReleased',h.x+60,h.y+40);}
await new Promise(r=>setTimeout(r,150));
console.log('bend',await ev("({pts:document.querySelectorAll('.alur-edge-point').length,paths:document.querySelectorAll('.alur-canvas-edge').length,title:document.getElementById('shapePanelTitle').textContent})"));
console.log('panelLabels',await ev("[...document.querySelectorAll('#shapePanelBody .shape-label')].map(x=>x.textContent)"));
// live width slider
console.log('widthBefore',await ev("(()=>{const p=[...document.querySelectorAll('#shapePanelBody path')][0];return p?p.getAttribute('stroke-width'):null})()"));
console.log('slider',await ev("(()=>{const l=[...document.querySelectorAll('#shapePanelBody .shape-label')].find(x=>x.textContent.startsWith('Width')); const i=l&&l.parentNode.querySelector('input'); if(!i)return null; i.value='6'; i.dispatchEvent(new Event('input',{bubbles:true})); return i.value})()"));
console.log('widthAfter',await ev("(()=>{const p=[...document.querySelectorAll('#shapePanelBody path')][0];return p?p.getAttribute('stroke-width'):null})()"));
console.log('panelLabelAfter',await ev("(()=>{const l=[...document.querySelectorAll('#shapePanelBody .shape-label')].find(x=>x.textContent.startsWith('Width'));return l?l.textContent:null})()"));
ws.close();
})();
