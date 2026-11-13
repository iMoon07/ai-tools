(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();const errs=[];ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}else if(m.method==='Runtime.exceptionThrown'){errs.push(m.params.exceptionDetails.text)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,900));return r.result&&r.result.result&&r.result.result.value};
const touch=(type,x,y)=>send('Input.dispatchTouchEvent',{type,touchPoints:type==='touchEnd'?[]:[{x,y,id:1,radiusX:2,radiusY:2,force:1}]});
await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});await send('Page.navigate',{url:'http://localhost:8000/imoon07.github.io/preview.html'});await new Promise(r=>setTimeout(r,5000));
const before=await ev("document.querySelectorAll('.alur-canvas-edge').length");
// choose two nodes with no existing edge? just use first and last; connectNodes dedupes, so choose a node pair likely unconnected
const pts=await ev("(()=>{const ns=[...document.querySelectorAll('.alur-canvas-node')];const a=ns[0].getBoundingClientRect(),b=ns[ns.length-1].getBoundingClientRect();return {a:{x:Math.round(a.x+a.width/2),y:Math.round(a.y+a.height/2),id:ns[0].getAttribute('data-node-id')},b:{x:Math.round(b.x+b.width/2),y:Math.round(b.y+b.height/2),id:ns[ns.length-1].getAttribute('data-node-id')}}})()");
await ev("document.querySelector('[data-tool=arrow]').click()");await new Promise(r=>setTimeout(r,200));
await touch('touchStart',pts.a.x,pts.a.y);await new Promise(r=>setTimeout(r,80));
await touch('touchMove',(pts.a.x+pts.b.x)/2,(pts.a.y+pts.b.y)/2);await new Promise(r=>setTimeout(r,80));
await touch('touchMove',pts.b.x,pts.b.y);await new Promise(r=>setTimeout(r,80));
await touch('touchEnd',pts.b.x,pts.b.y);await new Promise(r=>setTimeout(r,600));
const after=await ev("({edges:document.querySelectorAll('.alur-canvas-edge').length,tool:document.querySelector('.tool.is-on')?.getAttribute('data-tool')})");
console.log({before,pts,after,errs});ws.close();})();
