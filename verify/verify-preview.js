(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();
let page=targets.find(t=>t.type==='page');
const ws=new WebSocket(page.webSocketDebuggerUrl); let id=0; const p=new Map(); const errs=[];
ws.onmessage=e=>{const m=JSON.parse(e.data); if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id);} else if(m.method==='Runtime.exceptionThrown'){errs.push(m.params.exceptionDetails.text+':'+(m.params.exceptionDetails.exception&&m.params.exceptionDetails.exception.description||''));} else if(m.method==='Runtime.consoleAPICalled' && m.params.type==='error'){errs.push('console:'+m.params.args.map(a=>a.value||a.description).join(' '));}};
await new Promise(r=>ws.onopen=r);
const send=(method,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method,params}))});
const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true}); if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,400)); return r.result&&r.result.result&&r.result.result.value};
await send('Runtime.enable'); await send('Page.enable');
await send('Page.navigate',{url:'file:///home/moon/Projects/imoon07.github.io/preview.html'});
await new Promise(r=>setTimeout(r,1800));
console.log('lang',await ev("document.documentElement.lang"));
console.log('title',await ev("document.title"));
console.log('emptyHint',await ev("document.getElementById('emptyHint') && {hidden:document.getElementById('emptyHint').hidden, text:document.getElementById('emptyHint').innerText}"));
console.log('docTitle',await ev("document.getElementById('docTitle').value"));
console.log('moduleNodes',await ev("document.querySelectorAll('.alur-module-node').length"));
console.log('canvasNodes',await ev("document.querySelectorAll('.alur-canvas-node').length"));
console.log('errs',errs);
ws.close();})();
