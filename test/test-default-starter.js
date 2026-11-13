(async()=>{
const ver=await (await fetch('http://127.0.0.1:9224/json/version')).json();
const bws=new WebSocket(ver.webSocketDebuggerUrl);let bid=0;const bp=new Map();bws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&bp.has(m.id)){bp.get(m.id)(m);bp.delete(m.id)}};await new Promise(r=>bws.onopen=r);const bsend=(method,params={})=>new Promise(res=>{const i=++bid;bp.set(i,res);bws.send(JSON.stringify({id:i,method,params}))});
const ctx=await bsend('Target.createBrowserContext',{disposeOnDetach:true});const browserContextId=ctx.result.browserContextId;
const tg=await bsend('Target.createTarget',{url:'http://localhost:8000/imoon07.github.io/preview.html',browserContextId});const targetId=tg.result.targetId;
await new Promise(r=>setTimeout(r,5000));
const list=await (await fetch('http://127.0.0.1:9224/json')).json();const page=list.find(t=>t.id===targetId);if(!page){console.log('no page');process.exit();}
const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});return r.result&&r.result.result&&r.result.result.value};
console.log(await ev("({nodes:[...document.querySelectorAll('.alur-canvas-node')].map(n=>n.getAttribute('data-node-id')),edges:document.querySelectorAll('.alur-canvas-edge').length,labels:[...document.querySelectorAll('.alur-node-label')].map(n=>n.textContent)})"));
ws.close();bws.close();})();
