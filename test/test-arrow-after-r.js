(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();const errs=[];ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}else if(m.method==='Runtime.exceptionThrown'){errs.push(m.params.exceptionDetails.text)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,900));return r.result&&r.result.result&&r.result.result.value};
const mouse=(type,x,y,buttons=1)=>send('Input.dispatchMouseEvent',{type,x,y,button:type==='mouseMoved'?'none':'left',buttons,clickCount:type==='mousePressed'||type==='mouseReleased'?1:0});
await send('Emulation.setDeviceMetricsOverride',{width:1280,height:900,deviceScaleFactor:1,mobile:false});
await send('Page.navigate',{url:'http://localhost:8000/imoon07.github.io/preview.html'});await new Promise(r=>setTimeout(r,5000));
const before=await ev("({nodes:document.querySelectorAll('.alur-canvas-node').length,edges:document.querySelectorAll('.alur-canvas-edge').length})");
// R create box
await ev("document.querySelector('[data-tool=box]').click()");
const st=await ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})()");
const sx=Math.round(st.x+st.w*0.75), sy=Math.round(st.y+st.h*0.75);
await mouse('mousePressed',sx,sy);await mouse('mouseMoved',sx+90,sy+50);await mouse('mouseReleased',sx+90,sy+50);await new Promise(r=>setTimeout(r,500));
const created=await ev("(()=>{const ns=[...document.querySelectorAll('.alur-canvas-node')];const n=ns[ns.length-1];const r=n.getBoundingClientRect();return {id:n.getAttribute('data-node-id'),x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),tool:document.querySelector('.tool.is-on')?.getAttribute('data-tool')}})()");
// press A keyboard
await ev("document.dispatchEvent(new KeyboardEvent('keydown',{key:'a',bubbles:true}))");await new Promise(r=>setTimeout(r,200));
const toolA=await ev("document.querySelector('.tool.is-on')?.getAttribute('data-tool')");
// drag from created to first node
const target=await ev("(()=>{const n=document.querySelector('.alur-canvas-node');const r=n.getBoundingClientRect();return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)}})()");
await mouse('mousePressed',created.x,created.y);await mouse('mouseMoved',(created.x+target.x)/2,(created.y+target.y)/2);await mouse('mouseMoved',target.x,target.y);await mouse('mouseReleased',target.x,target.y);await new Promise(r=>setTimeout(r,800));
const after=await ev("({nodes:document.querySelectorAll('.alur-canvas-node').length,edges:document.querySelectorAll('.alur-canvas-edge').length})");
console.log({before,created,toolA,after,errs});ws.close();})();
