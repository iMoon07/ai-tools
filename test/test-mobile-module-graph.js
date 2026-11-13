(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();const errs=[];ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}else if(m.method==='Runtime.exceptionThrown'){errs.push(m.params.exceptionDetails.text)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,900));return r.result&&r.result.result&&r.result.result.value};
await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});await send('Page.navigate',{url:'http://localhost:8000/imoon07.github.io/preview.html'});await new Promise(r=>setTimeout(r,5000));
await ev("document.querySelector('.tool.mobile-panel[data-panel=assets]').click()");await new Promise(r=>setTimeout(r,400));
const before=await ev("({n:document.querySelectorAll('.alur-canvas-node').length,e:document.querySelectorAll('.alur-canvas-edge').length})");
const has=await ev("!!document.querySelector('[data-insert-module=graph]')");
if(has){await ev("document.querySelector('[data-insert-module=graph]').click()");await new Promise(r=>setTimeout(r,700));}
const after=await ev("({n:document.querySelectorAll('.alur-canvas-node').length,e:document.querySelectorAll('.alur-canvas-edge').length})");
console.log({before,has,after,errs});ws.close();})();
