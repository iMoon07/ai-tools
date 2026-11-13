(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();const page=targets.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const p=new Map();const errs=[];ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id)}else if(m.method==='Runtime.exceptionThrown'){errs.push(m.params.exceptionDetails.text)}};await new Promise(r=>ws.onopen=r);const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,900));return r.result&&r.result.result&&r.result.result.value};
await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
await send('Page.navigate',{url:'http://localhost:8000/imoon07.github.io/preview.html'});await new Promise(r=>setTimeout(r,2500));
await ev("localStorage.clear()");
await send('Page.reload',{ignoreCache:true});await new Promise(r=>setTimeout(r,5000));
console.log(await ev(`(async()=>{
  const out=[];
  const openAssets=document.querySelector('[data-panel=assets]'); if(openAssets) openAssets.click();
  const snap=()=>{
    const st=window.state && window.state.spec;
    return {specNodes:st&&st.nodes?Object.keys(st.nodes).length:0,specEdges:st&&st.edges?st.edges.length:0,domNodes:document.querySelectorAll('.alur-canvas-node').length,domEdges:document.querySelectorAll('.alur-canvas-edge').length};
  };
  out.push({after:'start',...snap()});
  for (const mod of ['flow','reverse-proxy','pipeline','graph']) {
    document.querySelector('[data-insert-module="'+mod+'"]').click();
    await new Promise(r=>setTimeout(r,500));
    out.push({after:mod,...snap()});
  }
  return out;
})()`));
console.log('errs',errs);
ws.close();})();
