(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();const errs=[];ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}else if(m.method==='Runtime.exceptionThrown'){errs.push(m.params.exceptionDetails.text)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,500));return r.result&&r.result.result&&r.result.result.value};
async function inspect(label,w,h){
 await send('Emulation.setDeviceMetricsOverride',{width:w,height:h,deviceScaleFactor:1,mobile:w<600});
 await send('Page.navigate',{url:'http://localhost:8000/imoon07.github.io/read.html?url=http%3A%2F%2Flocalhost%3A8000%2FPenjelajah-CyberSecurity%2Fblog-post-template%2Ftemplate-for-you-en.md'});await new Promise(r=>setTimeout(r,3000));await send('Page.reload',{ignoreCache:true});await new Promise(r=>setTimeout(r,5000));
 console.log(label, await ev("(()=>{const a=[...document.querySelectorAll('.alur')].find(a=>a.querySelector('.alur-bar'));const cap=a?a.querySelector('.alur-caption'):null;const g=[...document.querySelectorAll('.topo-group-label')].find(g=>g.textContent==='Edge & WAF');const t=g?g.closest('.topology'):null;const node=t?t.querySelector('.topo-node'):null;const cs=a?getComputedStyle(a):null;return {alurPad:cs?cs.padding:null,alurRadius:cs?cs.borderRadius:null,chartCap:cap?cap.textContent:null,topoNodeMax:node?getComputedStyle(node).maxWidth:null,narrow:!!(t&&t.classList.contains('topo--narrow')),overflow:t?[...t.querySelectorAll('.topo-node')].filter(n=>n.scrollWidth>n.clientWidth+1).length:null}})()"));
}
await inspect('DESKTOP',1280,900);
await inspect('MOBILE',390,844);
await send('Emulation.clearDeviceMetricsOverride');
console.log('errs',errs);ws.close();})();
