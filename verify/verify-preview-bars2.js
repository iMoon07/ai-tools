(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();const errs=[];ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}else if(m.method==='Runtime.exceptionThrown'){errs.push(m.params.exceptionDetails.text)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,500));return r.result&&r.result.result&&r.result.result.value};
await send('Runtime.enable');await send('Page.enable');
const scene={module:'canvas',title:'Bars',grid:true,width:900,height:520,nodes:{n1:{id:'n1',x:120,y:90,w:460,h:300,shape:'module',module:'chart',moduleSpec:{module:'chart',type:'bar',labels:['Jan','Feb','Mar','Apr'],data:[12,18,15,22],color:'blue'},label:'',color:'blue'}},edges:[]};
const src="try{localStorage.setItem('ruang.scene.v1',"+JSON.stringify(JSON.stringify(scene))+")}catch(e){}";
await send('Page.addScriptToEvaluateOnNewDocument',{source:src});
await send('Page.navigate',{url:'file:///home/moon/Projects/imoon07.github.io/preview.html'});await new Promise(r=>setTimeout(r,1800));
await ev("document.getElementById('shapePanel').hidden=true");
console.log('counts',await ev("({bars:document.querySelectorAll('.alur-module-embed[data-module=\\\"chart\\\"] .alur-bar').length,embeds:document.querySelectorAll('.alur-module-embed[data-module=\\\"chart\\\"]').length})"));
const info=await ev("(()=>{const b=document.querySelector('.alur-module-embed[data-module=\\\"chart\\\"] .alur-bar');if(!b)return null;const r=b.getBoundingClientRect();const els=document.elementsFromPoint(r.left+r.width/2,r.top+r.height/2);return {rect:[r.left,r.top,r.width,r.height],els:els.slice(0,6).map(e=>({tag:e.tagName,cls:e.getAttribute('class')}))}})()");
console.log('info',info);
if(info){const pt={x:info.rect[0]+info.rect[2]/2,y:info.rect[1]+info.rect[3]/2};await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:pt.x,y:pt.y,buttons:0});await new Promise(r=>setTimeout(r,350));}
console.log('hover',await ev("(()=>{const t=document.querySelector('.alur-chart-tip');const h=document.querySelector('.alur-bar.is-hover');return {hidden:t&&t.hidden,text:t&&t.textContent,hovered:!!h}})()"));
console.log('errs',errs);
ws.close();})();
