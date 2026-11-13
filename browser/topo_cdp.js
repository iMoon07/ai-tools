const fs=require('fs');
const md=process.argv[2]||'http://127.0.0.1:8000/Penjelajah-CyberSecurity/blog-post-template/template-for-you-id.md';
const lang=process.argv[3]||'id';
const tag=process.argv[4]||'id';
(async()=>{
const url='http://127.0.0.1:8000/imoon07.github.io/read.html?url='+encodeURIComponent(md)+'&lang='+lang;
const t=await (await fetch('http://127.0.0.1:9224/json/new?'+encodeURIComponent(url),{method:'PUT'})).json();
const ws=new WebSocket(t.webSocketDebuggerUrl);let id=0;const p=new Map();const errs=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}else if(m.method==='Runtime.exceptionThrown'){errs.push(m.params.exceptionDetails.text)}};
await new Promise(r=>ws.onopen=r);
const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});
const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,600));return r.result&&r.result.result&&r.result.result.value};
await send('Page.enable');await send('Runtime.enable');
async function run(label,w,h){
 await send('Emulation.setDeviceMetricsOverride',{width:w,height:h,deviceScaleFactor:1,mobile:w<600});
 await send('Page.navigate',{url});await new Promise(r=>setTimeout(r,4500));
 for(let i=0;i<30;i++){const ok=await ev("!!document.querySelector('.topology .topo-node')");if(ok)break;await new Promise(r=>setTimeout(r,400));}
 const data=await ev(`(()=>{
  const hs=[...document.querySelectorAll('h2,h3')];const out={prose:document.querySelector('.prose')?Math.round(document.querySelector('.prose').getBoundingClientRect().width):0,blocks:{}};
  ['18.8','19.1','19.2'].forEach(n=>{const h=hs.find(x=>x.textContent.includes(n));if(!h)return;let el=h.nextElementSibling;while(el&&!el.classList.contains('topology'))el=el.nextElementSibling;if(!el)return;
   const r=el.getBoundingClientRect();
   const nodes=[...el.querySelectorAll('.topo-node')].map(n=>{const q=n.getBoundingClientRect();return {id:n.dataset.node,label:n.querySelector('.topo-node-label')?.textContent,x:Math.round(q.x-r.x),y:Math.round(q.y-r.y),w:Math.round(q.width),h:Math.round(q.height)}});
   const paths=[...el.querySelectorAll('.topo-svg path')].map(p=>{let bb;try{bb=p.getBBox()}catch(e){return null}return {cls:p.getAttribute('class'),x:Math.round(bb.x),y:Math.round(bb.y),w:Math.round(bb.width),h:Math.round(bb.height)}}).filter(Boolean);
   const labels=[...el.querySelectorAll('.topo-group-label')].map(l=>({text:l.textContent,x:l.getAttribute('x'),y:l.getAttribute('y')}));
   const canvas=el.querySelector('.topo-canvas');const ov=[];
   for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++){const A=nodes[i],B=nodes[j];if(A.x<B.x+B.w&&B.x<A.x+A.w&&A.y<B.y+B.h&&B.y<A.y+A.h)ov.push(A.id+'/'+B.id)}
   out.blocks[n]={rect:{w:Math.round(r.width),h:Math.round(r.height)},canvas:{w:canvas.offsetWidth,h:canvas.offsetHeight,zoom:canvas.style.zoom},narrow:el.classList.contains('topo--narrow'),nodes,labels,paths,overlaps:ov};
  });return out})()`);
 console.log('====',label,w,h,'prose',data.prose,'errs',errs.slice(-3));
 for(const [k,b] of Object.entries(data.blocks)){
  console.log('--',k,'rect',b.rect,'canvas',b.canvas,'narrow',b.narrow,'overlaps',b.overlaps.slice(0,8));
  console.log('   labels',b.labels);
  console.log('   nodes',b.nodes.slice(0,10).map(n=>[n.id,n.x,n.y,n.w,n.h]));
  console.log('   paths',b.paths.slice(0,8).map(p=>[p.cls,p.x,p.y,p.w,p.h]));
  await ev(`(()=>{const h=[...document.querySelectorAll('h2,h3')].find(x=>x.textContent.includes('${k}'));if(h)h.scrollIntoView({block:'start'});})()`);
  await new Promise(r=>setTimeout(r,500));
  const s=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync('/home/moon/Projects/ai-tools/renders/topo-'+tag+'-'+label+'-'+k.replace('.','_')+'.png',Buffer.from(s.result.data,'base64'));
 }
}
await run('desktop',1440,1000);await run('mobile',390,844);
await fetch('http://127.0.0.1:9224/json/close/'+t.id);ws.close();
})();
