(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});return r.result&&r.result.result&&r.result.result.value};
await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});await send('Page.navigate',{url:'http://localhost:8000/imoon07.github.io/preview.html'});await new Promise(r=>setTimeout(r,5000));
await ev("window.__log=[];['pointerdown','pointermove','pointerup','pointercancel','touchstart','touchmove','touchend','touchcancel'].forEach(t=>document.addEventListener(t,e=>{window.__log.push([t,Math.round(e.clientX||0),Math.round(e.clientY||0)])},true));");
const pt={x:200,y:400,id:1,radiusX:2,radiusY:2,force:1};
await send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[pt]});await new Promise(r=>setTimeout(r,100));
await send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{...pt,x:250,y:430}]});await new Promise(r=>setTimeout(r,100));
await send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await new Promise(r=>setTimeout(r,300));
console.log(JSON.stringify(await ev("window.__log")));ws.close();})();
