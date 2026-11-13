(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,500));return r.result&&r.result.result&&r.result.result.value};
async function inspect(label,w,h){
  await send('Emulation.setDeviceMetricsOverride',{width:w,height:h,deviceScaleFactor:1,mobile:true});
  await send('Page.navigate',{url:'http://localhost:8000/imoon07.github.io/read.html?url=http%3A%2F%2Flocalhost%3A8000%2FPenjelajah-CyberSecurity%2Fblog-post-template%2Ftemplate-for-you-en.md'});
  await new Promise(r=>setTimeout(r,3000));await send('Page.reload',{ignoreCache:true});await new Promise(r=>setTimeout(r,5000));
  console.log(label, await ev("(()=>{const topo=[...document.querySelectorAll('.topology')].find(t=>t.querySelector('.topo-group-label')&&[...t.querySelectorAll('.topo-group-label')].some(g=>/Hospital|Runtime/.test(g.textContent)));const alur=[...document.querySelectorAll('.alur')].find(a=>a.querySelector('.alur-bar'));const t=topo;const cs=t?getComputedStyle(t):null;const cols=t?t.querySelector('.topo-columns'):null;const ccs=cols?getComputedStyle(cols):null;const a=alur;const acs=a?getComputedStyle(a):null;const svg=a?a.querySelector('svg'):null;return {topoClass:t?t.className:null,topoW:t?t.getBoundingClientRect().width:null,colsDir:ccs?ccs.flexDirection:null,colsW:cols?cols.getBoundingClientRect().width:null,colsScroll:cols?cols.scrollWidth:null,narrow:!!(t&&t.classList.contains('topo--narrow')),alurPad:acs?acs.padding:null,alurW:a?a.getBoundingClientRect().width:null,svgW:svg?svg.getBoundingClientRect().width:null,svgVB:svg?svg.getAttribute('viewBox'):null}})()"));
}
await inspect('DESKTOP',1280,900);
await inspect('MOBILE',390,844);
await send('Emulation.clearDeviceMetricsOverride');
ws.close();})();
