(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();const errs=[];ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}else if(m.method==='Runtime.exceptionThrown'){errs.push(m.params.exceptionDetails.text)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,900));return r.result&&r.result.result&&r.result.result.value};
const mouse=(type,x,y,buttons=1)=>send('Input.dispatchMouseEvent',{type,x,y,button:type==='mouseMoved'?'none':'left',buttons,clickCount:type==='mousePressed'||type==='mouseReleased'?1:0});
await send('Emulation.setDeviceMetricsOverride',{width:1280,height:900,deviceScaleFactor:1,mobile:false});
await send('Page.navigate',{url:'http://localhost:8000/imoon07.github.io/preview.html'});await new Promise(r=>setTimeout(r,5000));
// create a box
await ev("document.querySelector('[data-tool=box]').click()");
const stage=await ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})()");
const sx=Math.round(stage.x+stage.w*0.72), sy=Math.round(stage.y+stage.h*0.68);
await mouse('mousePressed',sx,sy); await mouse('mouseMoved',sx+90,sy+50); await mouse('mouseReleased',sx+90,sy+50);
await new Promise(r=>setTimeout(r,500));
const before=await ev("({nodes:document.querySelectorAll('.alur-canvas-node').length,edges:document.querySelectorAll('.alur-canvas-edge').length})");
const last=await ev("(()=>{const ns=[...document.querySelectorAll('.alur-canvas-node')];const n=ns[ns.length-1];const r=n.getBoundingClientRect();return {id:n.getAttribute('data-node-id'),x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)}})()");
// line from last node to first flow node
await ev("document.querySelector('[data-tool=line]').click()");
const target=await ev("(()=>{const n=document.querySelector('.alur-canvas-node');const r=n.getBoundingClientRect();return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)}})()");
await mouse('mousePressed',last.x,last.y); await mouse('mouseMoved',(last.x+target.x)/2,(last.y+target.y)/2); await mouse('mouseMoved',target.x,target.y); await mouse('mouseReleased',target.x,target.y);
await new Promise(r=>setTimeout(r,800));
const afterLine=await ev("({nodes:document.querySelectorAll('.alur-canvas-node').length,edges:document.querySelectorAll('.alur-canvas-edge').length})");
// delete selected node
await ev("(()=>{const n=document.querySelector('.alur-canvas-node[data-node-id=\""+last.id+"\"]');n.dispatchEvent(new MouseEvent('pointerdown',{bubbles:true,clientX:0,clientY:0}));})()");
await ev("document.dispatchEvent(new KeyboardEvent('keydown',{key:'Delete',bubbles:true}))");
await new Promise(r=>setTimeout(r,600));
const afterDelete=await ev("({nodes:document.querySelectorAll('.alur-canvas-node').length,edges:document.querySelectorAll('.alur-canvas-edge').length})");
// undo
await ev("document.dispatchEvent(new KeyboardEvent('keydown',{key:'z',ctrlKey:true,bubbles:true}))");
await new Promise(r=>setTimeout(r,600));
const afterUndo=await ev("({nodes:document.querySelectorAll('.alur-canvas-node').length,edges:document.querySelectorAll('.alur-canvas-edge').length})");
console.log({before,last,afterLine,afterDelete,afterUndo,errs});
ws.close();})();
