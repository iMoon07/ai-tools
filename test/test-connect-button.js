(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();const errs=[];ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}else if(m.method==='Runtime.exceptionThrown'){errs.push(m.params.exceptionDetails.text)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,900));return r.result&&r.result.result&&r.result.result.value};
await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
await send('Page.navigate',{url:'http://localhost:8000/imoon07.github.io/preview.html'});await new Promise(r=>setTimeout(r,5000));
// layout
console.log('layout', await ev("(()=>{const rail=document.getElementById('editorBar'),stage=document.getElementById('stage').getBoundingClientRect();const rr=rail.getBoundingClientRect();const tools=[...rail.querySelectorAll('.tool')];return {rail:{x:Math.round(rr.x),y:Math.round(rr.y),w:Math.round(rr.width),h:Math.round(rr.height)},stage:{w:Math.round(stage.width),h:Math.round(stage.height)},toolCount:tools.length,overflowX:document.documentElement.scrollWidth-document.documentElement.clientWidth}})()"));
// select first node, open shape panel, click Connect
await ev("(()=>{const n=document.querySelector('.alur-canvas-node');const r=n.getBoundingClientRect();n.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,clientX:r.x+r.width/2,clientY:r.y+r.height/2}));n.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,clientX:r.x+r.width/2,clientY:r.y+r.height/2}));})()");
await new Promise(r=>setTimeout(r,400));
const panel=await ev("(()=>{const p=document.getElementById('shapePanel');return {hidden:p.hidden,text:document.getElementById('shapePanelBody').textContent.slice(0,120)}})()");
const connect=await ev("(()=>{const b=[...document.querySelectorAll('#shapePanelBody button')].find(b=>b.textContent.trim()==='Connect');return !!b})()");
if(connect) await ev("(()=>{[...document.querySelectorAll('#shapePanelBody button')].find(b=>b.textContent.trim()==='Connect').click()})()");
await new Promise(r=>setTimeout(r,300));
const state1=await ev("({tool:document.querySelector('.tool.is-on')?.getAttribute('data-tool'),status:document.getElementById('statusTool').textContent})");
// tap target node (second node)
const target=await ev("(()=>{const ns=[...document.querySelectorAll('.alur-canvas-node')];const n=ns[1];const r=n.getBoundingClientRect();return {id:n.getAttribute('data-node-id'),x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)}})()");
await send('Input.dispatchMouseEvent',{type:'mousePressed',x:target.x,y:target.y,button:'left',buttons:1,clickCount:1});
await send('Input.dispatchMouseEvent',{type:'mouseReleased',x:target.x,y:target.y,button:'left',buttons:0,clickCount:1});
await new Promise(r=>setTimeout(r,600));
const after=await ev("({nodes:document.querySelectorAll('.alur-canvas-node').length,edges:document.querySelectorAll('.alur-canvas-edge').length})");
console.log({panel,connect,state1,target,after,errs});ws.close();})();
