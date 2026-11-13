const fs=require('fs');
(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});return r.result&&r.result.result&&r.result.result.value};
await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
await send('Page.navigate',{url:'http://localhost:8000/imoon07.github.io/read.html?url=http%3A%2F%2Flocalhost%3A8000%2FPenjelajah-CyberSecurity%2Fblog-post-template%2Ftemplate-for-you-en.md'});await new Promise(r=>setTimeout(r,3000));await send('Page.reload',{ignoreCache:true});await new Promise(r=>setTimeout(r,6000));
await ev("(()=>{const g=[...document.querySelectorAll('.topo-group-label')].find(g=>g.textContent==='Edge & WAF');const t=g.closest('.topology');t.scrollIntoView({block:'start'});window.scrollBy(0,-80);return true})()");
await new Promise(r=>setTimeout(r,500));
const shot=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync('/home/moon/Projects/ai-tools/browser/mobile-hospital.png',Buffer.from(shot.result.data,'base64'));
await ev("(()=>{const a=[...document.querySelectorAll('.alur')].find(a=>a.querySelector('.alur-bar'));a.scrollIntoView({block:'center'});return true})()");await new Promise(r=>setTimeout(r,400));
const shot2=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync('/home/moon/Projects/ai-tools/browser/mobile-chart.png',Buffer.from(shot2.result.data,'base64'));
await send('Emulation.clearDeviceMetricsOverride');ws.close();console.log('saved');
})();
