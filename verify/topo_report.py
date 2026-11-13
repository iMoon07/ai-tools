import sys, json, re, os
from playwright.sync_api import sync_playwright
md=sys.argv[1]
lang=sys.argv[2] if len(sys.argv)>2 else 'id'
url='http://127.0.0.1:8000/imoon07.github.io/read.html?url='+md+'&lang='+lang
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for label,w,h in [('desktop',1440,1000),('mobile',390,844)]:
  pg=b.new_page(viewport={'width':w,'height':h})
  errs=[]; pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
  pg.goto(url,wait_until='load',timeout=60000)
  try: pg.wait_for_selector('.topology .topo-node',timeout=30000)
  except Exception as e: print('NO NODES',label,e)
  pg.wait_for_timeout(2000)
  data=pg.evaluate("""()=>{
   const hs=[...document.querySelectorAll('h2,h3')];
   const out={prose:document.querySelector('.prose')?Math.round(document.querySelector('.prose').getBoundingClientRect().width):0,blocks:{}};
   ['18.8','19.1','19.2'].forEach(n=>{
    const h=hs.find(x=>x.textContent.includes(n)); if(!h)return;
    let el=h.nextElementSibling;
    while(el && !el.classList.contains('topology')) el=el.nextElementSibling;
    if(!el)return;
    const r=el.getBoundingClientRect();
    const nodes=[...el.querySelectorAll('.topo-node')].map(n=>{const q=n.getBoundingClientRect();return {id:n.dataset.node,label:n.querySelector('.topo-node-label')?.textContent,x:Math.round(q.x-r.x),y:Math.round(q.y-r.y),w:Math.round(q.width),h:Math.round(q.height)}});
    const paths=[...el.querySelectorAll('.topo-svg path')].map(p=>{let bb;try{bb=p.getBBox()}catch(e){return null}return {cls:p.getAttribute('class'),x:Math.round(bb.x),y:Math.round(bb.y),w:Math.round(bb.width),h:Math.round(bb.height),d:p.getAttribute('d')}}).filter(Boolean);
    const labels=[...el.querySelectorAll('.topo-group-label')].map(l=>({text:l.textContent,x:l.getAttribute('x'),y:l.getAttribute('y')}));
    const canvas=el.querySelector('.topo-canvas');
    const ov=[];for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++){const A=nodes[i],B=nodes[j];if(A.x<B.x+B.w&&B.x<A.x+A.w&&A.y<B.y+B.h&&B.y<A.y+A.h)ov.push(A.id+'/'+B.id)}
    out.blocks[n]={rect:{w:Math.round(r.width),h:Math.round(r.height)},canvas:{w:canvas.offsetWidth,h:canvas.offsetHeight,zoom:canvas.style.zoom},narrow:el.classList.contains('topo--narrow'),nodes,labels,paths,overlaps:ov};
   });
   return out;
  }""")
  print('====',label,w,h,'prose',data['prose'],'errs',errs[-3:])
  for k,b in data['blocks'].items():
   print('--',k,'rect',b['rect'],'canvas',b['canvas'],'narrow',b['narrow'],'overlaps',b['overlaps'][:8])
   print('   labels',b['labels'])
   print('   nodes',[(n['id'],n['x'],n['y'],n['w'],n['h']) for n in b['nodes']][:12])
   print('   paths',[(p['cls'],p['x'],p['y'],p['w'],p['h']) for p in b['paths'][:10]])
  for k in data['blocks']:
   try:
    el=pg.locator('.topology').filter(has=pg.locator('.topo-node')).nth(list(data['blocks']).index(k))
   except Exception: pass
  pg.screenshot(path=f'/home/moon/Projects/ai-tools/renders/topo-{label}.png',full_page=False)
  pg.close()
 b.close()
