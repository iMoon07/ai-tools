(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();
const page=targets.find(t=>t.type==='page');
const ws=new WebSocket(page.webSocketDebuggerUrl); let id=0; const p=new Map(); const errs=[];
ws.onmessage=e=>{const m=JSON.parse(e.data); if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id);} else if(m.method==='Runtime.exceptionThrown'){errs.push(m.params.exceptionDetails.text+':'+(m.params.exceptionDetails.exception&&m.params.exceptionDetails.exception.description||''));} else if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error'){errs.push('console:'+m.params.args.map(a=>a.value||a.description).join(' '));}};
await new Promise(r=>ws.onopen=r);
const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});
const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true}); if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,400)); return r.result&&r.result.result&&r.result.result.value};
await send('Runtime.enable'); await send('Page.enable');
await send('Page.navigate',{url:'http://localhost:8000/imoon07.github.io/read.html?post=blog-post-template&lang=id'});
await new Promise(r=>setTimeout(r,3500));
console.log('alur',await ev("document.querySelectorAll('.alur').length"));
console.log('charts',await ev("document.querySelectorAll('.alur-chart').length"));
console.log('modules',await ev("[...document.querySelectorAll('.alur')].map(x=>x.getAttribute('data-module'))"));
console.log('hostPos',await ev("(()=>{const h=document.querySelector('.alur-host');return h?getComputedStyle(h).position:null})()"));
console.log('tipCSS',await ev("(()=>{const t=document.querySelector('.alur-chart-tip');return t?{pos:getComputedStyle(t).position,disp:getComputedStyle(t).display}:null})()"));
console.log('errs',errs);
ws.close();})();
