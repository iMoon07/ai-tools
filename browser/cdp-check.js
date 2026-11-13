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
await send('Runtime.enable');
await new Promise(r=>setTimeout(r,800));
console.log('topActions',await ev("!!document.querySelector('.top-actions')"));
console.log('bottomButtons',await ev("[...document.querySelectorAll('.zoom-bar [data-panel],#focusModeBottom')].map(b=>b.textContent.trim())"));
console.log('dockBottom',await ev("getComputedStyle(document.getElementById('panelAssets')).bottom"));
await ev(`state.spec.nodes={}; state.spec.edges=[{points:[[100,100],[200,100]],arrowStart:true,arrowEnd:true,curved:true},{points:[[100,180],[200,180]],arrowStart:false,arrowEnd:false,curved:false}]; state.spec.selected=null; state.spec.selectedEdge=null; state.spec.selectedEdges=[]; state.spec.selectedDrawing=null; render(); true`);
await ev('document.body.focus()');
await key('a','KeyA',['ctrl']);
console.log('afterCtrlA',await ev("({nodes:state.spec.selected.length||0,edges:(state.spec.selectedEdges||[]).length,edge:state.spec.selectedEdge})"));
await key('Delete','Delete');
console.log('afterDelete',await ev("({nodes:Object.keys(state.spec.nodes).length,edges:state.spec.edges.length})"));
await ev(`state.spec.nodes={}; state.spec.edges=[{points:[[100,100],[300,100]],arrowStart:true,arrowEnd:true,curved:true}]; state.spec.selected=null; state.spec.selectedEdge=0; state.spec.selectedEdges=[0]; state.spec.selectedDrawing=null; render(); true`);
const box=await ev("(()=>{const h=document.querySelector('.alur-edge-point.is-mid'); if(!h)return null; const r=h.getBoundingClientRect(); return {x:r.left+r.width/2,y:r.top+r.height/2,pts:state.spec.edges[0].points.length};})()");
console.log('midHandle',box);
if(box){await send('Input.dispatchMouseEvent',{type:'mousePressed',x:box.x,y:box.y,button:'left',buttons:1,clickCount:1});for(let i=1;i<=4;i++)await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:box.x+i*10,y:box.y+i*6,button:'left',buttons:1});await send('Input.dispatchMouseEvent',{type:'mouseReleased',x:box.x+40,y:box.y+24,button:'left',buttons:0,clickCount:1});}
console.log('afterBend',await ev("({pts:state.spec.edges[0].points.length,ptsData:state.spec.edges[0].points})"));
console.log('panelTitle',await ev("document.getElementById('shapePanelTitle').textContent"));
console.log('panelWidth',await ev("(()=>{const l=[...document.querySelectorAll('#shapePanelBody .shape-label')].find(x=>x.textContent.startsWith('Width')); return l?l.textContent:null})()"));
console.log('shortcutInactiveGone',await ev("document.getElementById('shortcutCard').textContent.includes('insert image')"));
ws.close();
})();
