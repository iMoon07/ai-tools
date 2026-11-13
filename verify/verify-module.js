(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();
const page=targets.find(t=>t.type==='page');
const ws=new WebSocket(page.webSocketDebuggerUrl); let id=0; const p=new Map(); const errs=[];
ws.onmessage=e=>{const m=JSON.parse(e.data); if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id);} else if(m.method==='Runtime.exceptionThrown'){errs.push(m.params.exceptionDetails.text);} else if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error'){errs.push('console:'+m.params.args.map(a=>a.value||a.description).join(' '));}};
await new Promise(r=>ws.onopen=r);
const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});
const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true}); if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,500)); return r.result&&r.result.result&&r.result.result.value};
await send('Runtime.enable'); await send('Page.enable');
await send('Page.navigate',{url:'file:///home/moon/Projects/imoon07.github.io/preview.html'});
await new Promise(r=>setTimeout(r,1500));
// open assets if closed
console.log('assetsOpen',await ev("document.getElementById('panelAssets').classList.contains('is-open')"));
await ev("document.querySelector('[data-panel=\\\"assets\\\"]').click()");
await new Promise(r=>setTimeout(r,300));
console.log('sceneSection',await ev("(()=>{const s=document.getElementById('sceneSection');return s?{h3:[...s.querySelectorAll('h3')].map(x=>x.textContent),buttons:[...s.querySelectorAll('[data-insert-module]')].map(b=>b.getAttribute('data-insert-module'))}:null})()"));
console.log('assetsHead',await ev("document.querySelector('#panelAssets .dock-head').innerText"));
await ev("document.querySelector('[data-insert-module=\\\"flow\\\"]').click()");
await new Promise(r=>setTimeout(r,700));
console.log('afterInsert',await ev("(()=>{const ns=[...document.querySelectorAll('.alur-module-node')];return {count:ns.length, html:ns.map(n=>n.outerHTML.slice(0,600)), embeds:document.querySelectorAll('.alur-module-embed').length, embedsSpec:document.querySelector('.alur-module-embed')&&document.querySelector('.alur-module-embed').getAttribute('data-module')}})()"));
console.log('delBtns',await ev("document.querySelectorAll('[data-module-delete]').length"));
console.log('rects',await ev("(()=>{const n=document.querySelector('.alur-module-node');return n?[...n.querySelectorAll('rect')].map(r=>({cls:r.getAttribute('class'),fill:r.getAttribute('fill'),stroke:r.getAttribute('stroke')})):null})()"));
console.log('foPE',await ev("(()=>{const f=document.querySelector('.alur-module-fo');const e=document.querySelector('.alur-module-embed');return {fo:getComputedStyle(f).pointerEvents, embed:getComputedStyle(e).pointerEvents, bg:getComputedStyle(e).backgroundColor}})()"));
console.log('errs',errs);
ws.close();})();
