(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,700));return r.result&&r.result.result&&r.result.result.value};
await send('Page.enable');await send('Runtime.enable');await send('Page.navigate',{url:'http://localhost:8000/imoon07.github.io/preview.html'});await new Promise(r=>setTimeout(r,3000));await send('Page.reload',{ignoreCache:true});await new Promise(r=>setTimeout(r,4000));
console.log('setup', await ev("(()=>{const p=document.getElementById('preset');if(!p)return 'no preset';p.value='starter';p.dispatchEvent(new Event('change'));return {value:p.value,nodes:document.querySelectorAll('.alur-canvas-node').length,edges:document.querySelectorAll('.alur-canvas-edge').length}})()"));
await new Promise(r=>setTimeout(r,500));
console.log('nodes', await ev("(()=>[...document.querySelectorAll('.alur-canvas-node')].map(n=>{const r=n.getBoundingClientRect();return {id:n.getAttribute('data-node-id'),x:r.left+r.width/2,y:r.top+r.height/2,w:r.width,h:r.height}}))()"));
const pts=await ev("(()=>[...document.querySelectorAll('.alur-canvas-node')].map(n=>{const r=n.getBoundingClientRect();return {id:n.getAttribute('data-node-id'),x:r.left+r.width/2,y:r.top+r.height/2}}))()");
// choose arrow tool
console.log('tool', await ev("(()=>{document.querySelector('[data-tool=arrow]').click();return document.getElementById('statusTool').textContent})()"));
async function drag(a,b){
 await send('Input.dispatchMouseEvent',{type:'mousePressed',x:a.x,y:a.y,button:'left',clickCount:1});
 await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:(a.x+b.x)/2,y:(a.y+b.y)/2,button:'left',buttons:1});
 await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:b.x,y:b.y,button:'left',buttons:1});
 await send('Input.dispatchMouseEvent',{type:'mouseReleased',x:b.x,y:b.y,button:'left',clickCount:1});
}
await drag(pts[0],pts[1]);
await new Promise(r=>setTimeout(r,400));
console.log('after arrow', await ev("(()=>({edges:document.querySelectorAll('.alur-canvas-edge').length,selected:[...document.querySelectorAll('.alur-canvas-edge')].map(e=>e.getAttribute('d')).slice(0,3)}))()"));
// line tool
console.log('tool2', await ev("(()=>{document.querySelector('[data-tool=line]').click();return document.getElementById('statusTool').textContent})()"));
await drag(pts[1],pts[2]);
await new Promise(r=>setTimeout(r,400));
console.log('after line', await ev("(()=>({edges:document.querySelectorAll('.alur-canvas-edge').length,drawings:document.querySelectorAll('.alur-drawing').length}))()"));
ws.close();})();
