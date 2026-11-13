import io, json, sys

SITE = "/home/moon/Projects/imoon07.github.io"
BASE = "/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture"

SANITIZE = """DOMPurify.sanitize(parsed, {
  ADD_TAGS: ['figure','figcaption','details','summary','mark','kbd','sub','sup','dl','dt','dd','iframe','section','video','source'],
  ADD_ATTR: ['target','rel','align','id','loading','decoding','start','style','class','width','height','frameborder','allowfullscreen','allow','controls','poster','preload','muted','playsinline','loop','autoplay','colspan','rowspan','open','role','title','dir','lang','tabindex','name','value','type','checked','disabled','readonly','selected','multiple','spellcheck','referrerpolicy','sandbox','srcset','sizes','data-math'],
  ALLOW_DATA_ATTR: true,
  ALLOWED_URI_REGEXP: /^(?:(?:https?|mailto|tel|callto|sms|ftp):|[^a-z]|[a-z+.\\-]+(?:[^a-z+.\\-:]|$))/i
})"""

MEASURE = r"""
function measure(){
  const out={topo:0,mermaid:0,proseW:0,nodeCount:0,idAttrs:[],blocks:[]};
  const prose=document.querySelector('.prose');
  out.proseW=prose?Math.round(prose.getBoundingClientRect().width):0;
  out.topo=document.querySelectorAll('.topology').length;
  out.mermaid=document.querySelectorAll('.mermaid').length;
  out.nodeCount=document.querySelectorAll('.topo-node').length;
  out.dots=document.querySelectorAll('.topo-dot').length;
  out.anims=document.querySelectorAll('animateMotion').length;
  out.cook=document.querySelectorAll('.topo-node--cook').length;
  out.live=document.querySelectorAll('.topo-node--live').length;
  document.querySelectorAll('#content [id]').forEach(el=>out.idAttrs.push(el.tagName.toLowerCase()+'#'+el.id));
  document.querySelectorAll('.topology').forEach((r,i)=>{
    const c=r.querySelector('.topo-canvas'), st=r.querySelector('.topo-stage'), cols=r.querySelector('.topo-columns');
    const cr=r.getBoundingClientRect();
    const paths=[...r.querySelectorAll('.topo-svg path')];
    let minX=1e9,maxX=-1e9,minY=1e9,maxY=-1e9;
    paths.forEach(p=>{try{const bb=p.getBBox();minX=Math.min(minX,bb.x);maxX=Math.max(maxX,bb.x+bb.width);minY=Math.min(minY,bb.y);maxY=Math.max(maxY,bb.y+bb.height);}catch(e){}});
    const ns=[...r.querySelectorAll('.topo-node')].map(n=>({id:n.dataset.node,rc:n.getBoundingClientRect()}));
    const ov=[];
    for(let a=0;a<ns.length;a++)for(let b=a+1;b<ns.length;b++){
      const A=ns[a].rc,B=ns[b].rc;
      if(A.left<B.right-1&&B.left<A.right-1&&A.top<B.bottom-1&&B.top<A.bottom-1)ov.push(ns[a].id+'/'+ns[b].id);
    }
    out.blocks.push({i,nodes:r.querySelectorAll('.topo-node').length,paths:paths.length,
      canvas:c?Math.round(c.offsetWidth)+'x'+Math.round(c.offsetHeight):'-',
      zoom:c?c.style.zoom:'-',
      stage:st?Math.round(st.clientWidth)+'x'+Math.round(st.clientHeight):'-',
      cols:cols?Math.round(cols.offsetWidth)+'x'+Math.round(cols.offsetHeight):'-',
      rootW:Math.round(cr.width),rootH:Math.round(cr.height),
      narrow:r.classList.contains('topo--narrow'),
      pathBox:isFinite(minX)?[Math.round(minX),Math.round(minY),Math.round(maxX),Math.round(maxY)]:null,
      overlaps:ov, dots:r.querySelectorAll('.topo-dot').length, anims:r.querySelectorAll('animateMotion').length});
  });
  return out;
}
setTimeout(()=>{document.getElementById('report').textContent=JSON.stringify(measure());},700);
"""

TPL = """<!DOCTYPE html><html><head><meta charset="utf-8">
<script src="file:///home/moon/Projects/ai-tools/vendor/marked.min.js"></script>
<script src="file:///home/moon/Projects/ai-tools/vendor/purify.min.js"></script>
<script src="file://__SITE__/js/markdown.js"></script>
<script src="file://__SITE__/js/topology-icons.js"></script>
<script src="file://__SITE__/js/topology.js"></script>
<link rel="stylesheet" href="file://__SITE__/css/shell.css">
<link rel="stylesheet" href="file://__SITE__/css/article.css">
<link rel="stylesheet" href="file://__SITE__/css/topology.css">
<style>body{margin:0;background:#111827}</style></head><body class="article-page">
<div class="site"><main class="article-layout" id="article-layout"><article class="article-column">
<div class="prose" id="content"></div>
</article></article></main></div>
<pre id="report">pending</pre>
<script>
const MD=__MD__;
const parsed=marked.parse(MD,{gfm:true,breaks:false});
const sanitized=__SAN__;
document.getElementById('content').innerHTML=sanitized;
Topology.init();
__MEASURE__
</script></body></html>"""

lang = sys.argv[1] if len(sys.argv) > 1 else "en"
md = io.open(f"{BASE}/server-single-tier-stack-{lang}.md", encoding="utf-8").read()
page = (TPL.replace("__SITE__", SITE)
           .replace("__MD__", json.dumps(md))
           .replace("__SAN__", SANITIZE)
           .replace("__MEASURE__", MEASURE))
io.open(f"/home/moon/Projects/ai-tools/snapshots/pages/harness-{lang}.html", "w", encoding="utf-8").write(page)
print("wrote", f"/home/moon/Projects/ai-tools/snapshots/pages/harness-{lang}.html", len(page))