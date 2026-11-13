import io,json,re,subprocess
SITE="/home/moon/Projects/imoon07.github.io"
md=io.open("/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture/server-single-tier-stack-en.md",encoding="utf-8").read()
specs=re.findall(r"```topology\n(.*?)\n```",md,re.S)
md_join="\n\n".join("```topology\n"+s+"\n```" for s in specs)
JS = r"""
const MD=__MD__;
document.getElementById('content').innerHTML=DOMPurify.sanitize(marked.parse(MD,{gfm:true}),{ADD_TAGS:['figure','figcaption'],ADD_ATTR:['id','class','style','data-spec','aria-label','role','fill','r','href','target','rel','title'],ALLOW_DATA_ATTR:true});
Topology.init();
setTimeout(function(){
 try{
  const out={blocks:[],images:[]};
  document.querySelectorAll('.topology').forEach((r,bi)=>{
    const b={i:bi,nodes:[],links:0};
    r.querySelectorAll('.topo-node').forEach(n=>{
      const icons=n.querySelectorAll('.topo-node-icon > svg, .topo-node-icon > a > svg');
      const links=[...n.querySelectorAll('.topo-node-icon-link')];
      const row=n.querySelector('.topo-node-icon');
      const nr=n.getBoundingClientRect(), rr=row?row.getBoundingClientRect():null;
      b.nodes.push({id:n.dataset.node,icons:icons.length,links:links.map(a=>a.getAttribute('href')),target:links[0]?links[0].getAttribute('target'):null,rel:links[0]?links[0].getAttribute('rel'):null,rowW:rr?Math.round(rr.width):0,nodeW:Math.round(nr.width),overflow:rr?rr.width>nr.width+1:false});
    });
    b.links=r.querySelectorAll('.topo-node-icon-link').length;
    out.blocks.push(b);
  });
  document.getElementById('report').textContent=JSON.stringify(out);
 }catch(e){document.getElementById('report').textContent='ERR '+e.stack;}
},900);
"""
page = """<!DOCTYPE html><html><head><meta charset="utf-8">
<script src="file:///home/moon/Projects/ai-tools/vendor/marked.min.js"></script><script src="file:///home/moon/Projects/ai-tools/vendor/purify.min.js"></script>
<script src="file://__SITE__/js/markdown.js"></script><script src="file://__SITE__/js/topology-icons.js"></script><script src="file://__SITE__/js/topology.js"></script>
<link rel="stylesheet" href="file://__SITE__/css/shell.css"><link rel="stylesheet" href="file://__SITE__/css/article.css"><link rel="stylesheet" href="file://__SITE__/css/topology.css">
<style>body{margin:0;background:#111827}</style></head><body class="article-page"><div class="site"><main class="article-layout"><article class="article-column"><div class="prose" id="content"></div></article></article></main></div><pre id="report">pending</pre>
<script>__JS__</script></body></html>"""
page=page.replace("__SITE__",SITE).replace("__JS__",JS.replace("__MD__",json.dumps(md_join)))
io.open("/home/moon/Projects/ai-tools/verify/check_new_logos.html","w",encoding="utf-8").write(page)
o=subprocess.run(["/usr/bin/chromium","--headless","--no-sandbox","--disable-gpu","--window-size=1280,900","--virtual-time-budget=6000","--dump-dom","file:///home/moon/Projects/ai-tools/verify/check_new_logos.html"],capture_output=True,text=True,timeout=90).stdout
m=re.search(r'<pre id="report">(.*?)</pre>',o,re.S)
if not m:
    print("NO REPORT"); print(o[:1500]); raise SystemExit
d=json.loads(m.group(1))
for b in d["blocks"]:
    if b["i"]!=1: continue
    print("combined block: nodes",len(b["nodes"]),"per-logo links",b["links"])
    bad=[]
    for n in b["nodes"]:
        if n["icons"]>1:
            print(f'  {n["id"]:9} icons={n["icons"]} links={len(n["links"])} rowW={n["rowW"]} nodeW={n["nodeW"]} overflow={n["overflow"]} target={n["target"]} rel={n["rel"]}')
            if n["icons"]!=len(n["links"]): bad.append(n["id"])
    print("  nodes where icons != links:",bad)
