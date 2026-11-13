(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,700));return r.result&&r.result.result&&r.result.result.value};
await send('Page.navigate',{url:'http://localhost:8000/imoon07.github.io/preview.html'});await new Promise(r=>setTimeout(r,3000));await send('Page.reload',{ignoreCache:true});await new Promise(r=>setTimeout(r,4000));
await ev("(()=>{const p=document.getElementById('preset');p.value='starter';p.dispatchEvent(new Event('change'));return true})()");await new Promise(r=>setTimeout(r,1200));
async function drag(a,b){await send('Input.dispatchMouseEvent',{type:'mousePressed',x:a.x,y:a.y,button:'left',clickCount:1});await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:(a.x+b.x)/2,y:(a.y+b.y)/2,button:'left',buttons:1});await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:b.x,y:b.y,button:'left',buttons:1});await send('Input.dispatchMouseEvent',{type:'mouseReleased',x:b.x,y:b.y,button:'left',clickCount:1});}
for (const tool of ['line','arrow']) {
  await ev(`(()=>{document.querySelector('[data-tool=${tool}]').click();return true})()`);await new Promise(r=>setTimeout(r,300));
  const pts=await ev("(()=>[...document.querySelectorAll('.alur-canvas-node')].filter(n=>['n1','n3'].includes(n.getAttribute('data-node-id'))).map(n=>{const r=n.getBoundingClientRect();return {id:n.getAttribute('data-node-id'),x:r.left+r.width/2,y:r.top+r.height/2}}))()");
  const before=await ev("document.querySelectorAll('.alur-canvas-edge').length");
  await drag(pts[0],pts[1]);await new Promise(r=>setTimeout(r,500));
  const after=await ev("document.querySelectorAll('.alur-canvas-edge').length");
  console.log(tool,{pts,before,after});
}
ws.close();})();
