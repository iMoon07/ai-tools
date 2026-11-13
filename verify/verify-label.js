(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();
const page=targets.find(t=>t.type==='page');
const ws=new WebSocket(page.webSocketDebuggerUrl); let id=0; const p=new Map(); const errs=[];
ws.onmessage=e=>{const m=JSON.parse(e.data); if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id);} else if(m.method==='Runtime.exceptionThrown'){errs.push(m.params.exceptionDetails.text);} };
await new Promise(r=>ws.onopen=r);
const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});
const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true}); if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,500)); return r.result&&r.result.result&&r.result.result.value};
await send('Runtime.enable'); await send('Page.enable');
await send('Page.navigate',{url:'file:///home/moon/Projects/imoon07.github.io/preview.html'});
await new Promise(r=>setTimeout(r,1500));
await ev("document.querySelector('[data-panel=\\\"assets\\\"]').click()"); await new Promise(r=>setTimeout(r,200));
await ev("document.querySelector('[data-insert-module=\\\"flow\\\"]').click()"); await new Promise(r=>setTimeout(r,500));
// module should already be selected after insert; open shape panel via Alt+/ equivalent: call key handler? use syncShapePanel through clicking node
const box=await ev("(()=>{const n=document.querySelector('.alur-module-node');const r=n.getBoundingClientRect();return{x:r.left+20,y:r.top+Math.min(60,r.height/2)}})()");
const send2=(type,x,y)=>send('Input.dispatchMouseEvent',{type,x,y,button:'left',buttons:type==='mouseReleased'?0:1,clickCount:1});
await send2('mousePressed',box.x,box.y); await send2('mouseReleased',box.x,box.y); await new Promise(r=>setTimeout(r,300));
console.log('shapeHidden',await ev("document.getElementById('shapePanel').hidden"));
console.log('shapeText',await ev("document.getElementById('shapePanel').innerText.slice(0,400)"));
console.log('labelInput',await ev("(()=>{const l=[...document.querySelectorAll('#shapePanelBody label')].find(x=>x.textContent==='Label');return l?{exists:true,value:l.querySelector('input').value}:{exists:false}})()"));
await ev("(()=>{const l=[...document.querySelectorAll('#shapePanelBody label')].find(x=>x.textContent==='Label');const i=l.querySelector('input');i.value='JS';i.dispatchEvent(new Event('input',{bubbles:true}));})()");
await new Promise(r=>setTimeout(r,300));
console.log('titleText',await ev("document.querySelector('.alur-module-title')&&document.querySelector('.alur-module-title').textContent"));
console.log('errs',errs);
ws.close();})();
