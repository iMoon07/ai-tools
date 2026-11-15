(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();const errs=[];ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}else if(m.method==='Runtime.exceptionThrown'){errs.push(m.params.exceptionDetails.text)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,500));return r.result&&r.result.result&&r.result.result.value};
await send('Runtime.enable');await send('Page.enable');await send('Page.navigate',{url:'file:///tmp/alur-probes/charttest/line.html'});await new Promise(r=>setTimeout(r,1200));
const pt=await ev("(()=>{const d=document.querySelectorAll('.alur-line-dot')[2];const r=d.getBoundingClientRect();return{x:r.left+r.width/2+8,y:r.top+r.height/2}})()");
console.log('pt',pt);
await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:pt.x,y:pt.y,buttons:0});await new Promise(r=>setTimeout(r,300));
console.log(await ev("(()=>{const h=document.querySelector('.alur-hit.is-hover');const dot=document.querySelectorAll('.alur-line-dot')[2];const t=document.querySelector('.alur-chart-tip');return {hit:!!h,tip:t.textContent,dotOpacity:getComputedStyle(dot).opacity,dotFilter:getComputedStyle(dot).filter}})()"));
console.log('errs',errs);
ws.close();})();
