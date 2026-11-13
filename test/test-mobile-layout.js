(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();const errs=[];ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}else if(m.method==='Runtime.exceptionThrown'){errs.push(m.params.exceptionDetails.text)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,900));return r.result&&r.result.result&&r.result.result.value};
await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
await send('Page.navigate',{url:'http://localhost:8000/imoon07.github.io/preview.html'});await new Promise(r=>setTimeout(r,5000));
const rect=async sel=>ev("(()=>{const e=document.querySelector('"+sel+"');if(!e)return null;const r=e.getBoundingClientRect();return {x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height),display:getComputedStyle(e).display,vis:getComputedStyle(e).visibility}})()");
console.log('rail',await rect('#editorBar'));
// open assets
await ev("document.querySelector('[data-panel=assets]').click()");await new Promise(r=>setTimeout(r,300));
console.log('assets',await rect('#panelAssets'));
await ev("document.querySelector('[data-close=assets]').click()");await new Promise(r=>setTimeout(r,300));
// select node
await ev("(()=>{const n=document.querySelector('.alur-canvas-node');const r=n.getBoundingClientRect();n.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,clientX:r.x+r.width/2,clientY:r.y+r.height/2}));n.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,clientX:r.x+r.width/2,clientY:r.y+r.height/2}));})()");await new Promise(r=>setTimeout(r,400));
console.log('shape',await rect('#shapePanel'));
console.log('overflow',await ev("({doc:[document.documentElement.scrollWidth,document.documentElement.clientWidth],errs:0})"),errs);ws.close();})();
