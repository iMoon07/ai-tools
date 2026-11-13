(async()=>{
const fs=require('fs');
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});return r.result&&r.result.result&&r.result.result.value};
await send('Runtime.enable');await send('Page.enable');await send('Page.navigate',{url:'http://localhost:8000/imoon07.github.io/read.html?post=blog-post-template&lang=id'});await new Promise(r=>setTimeout(r,3500));
await ev("const d=document.querySelector('.alur-donut-seg'); if(d) d.scrollIntoView({block:'center',behavior:'instant'})");await new Promise(r=>setTimeout(r,600));
const clip=await ev("(()=>{const s=document.querySelector('.alur-donut-seg');const svg=s.closest('svg');const r=svg.getBoundingClientRect();return {x:Math.max(0,r.left-20),y:Math.max(0,r.top-20),width:Math.min(900,r.width+40),height:Math.min(600,r.height+40),scale:1}})()");
console.log(clip);
const shot=await send('Page.captureScreenshot',{format:'png',clip});fs.writeFileSync('/home/moon/Projects/ai-tools/renders/donut.png',Buffer.from(shot.result.data,'base64'));
ws.close();})();
