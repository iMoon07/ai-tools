import io,json,re,subprocess
SITE="/home/moon/Projects/imoon07.github.io"
md=io.open("/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture/server-single-tier-stack-en.md",encoding="utf-8").read()
md_join="\n\n".join("```topology\n"+s+"\n```" for s in re.findall(r"```topology\n(.*?)\n```",md,re.S))
JS=r"""
const MD=__MD__;
document.getElementById('content').innerHTML=DOMPurify.sanitize(marked.parse(MD,{gfm:true}),{ADD_TAGS:['figure','figcaption'],ADD_ATTR:['id','class','style','data-spec','aria-label','role','fill','r','href','target','rel','title'],ALLOW_DATA_ATTR:true});
Topology.init();
setTimeout(function(){
 const out={parts:[],bad:[]};
 const r=document.querySelectorAll('.topology')[1];
 r.querySelectorAll('.topo-node').forEach(n=>{
   const row=n.querySelector('.topo-parts');
   if(row){
     const links=[...row.querySelectorAll('a')].map(a=>[a.textContent,a.getAttribute('href'),a.getAttribute('target')]);
     out.parts.push([n.dataset.node,links]);
   }
 });
 // flow block edge paths
 const f=document.querySelectorAll('.topology')[0];
 out.flow=[...f.querySelectorAll('.topo-svg path')].filter(p=>p.getAttribute('class')).map(p=>[p.getAttribute('class'),p.getAttribute('d')]);
 // platform I node link
 const p=document.querySelectorAll('.topology')[2];
 const i=p.querySelector('.topo-node[data-node="I"]');
 const a=i&&(i.tagName==='A'?i:i.querySelector('a'));
 out.platformI=a?{tag:i.tagName,href:a.getAttribute('href'),target:a.getAttribute('target')}:null;
 document.getElementById('report').textContent=JSON.stringify(out);
},900);
"""
page="""<!DOCTYPE html><html><head><meta charset="utf-8">
<script src="file:///home/moon/Projects/ai-tools/vendor/marked.min.js"></script><script src="file:///home/moon/Projects/ai-tools/vendor/purify.min.js"></script>
<script src="file://__SITE__/js/markdown.js"></script><script src="file://__SITE__/js/topology-icons.js"></script><script src="file://__SITE__/js/topology.js"></script>
<link rel="stylesheet" href="file://__SITE__/css/shell.css"><link rel="stylesheet" href="file://__SITE__/css/article.css"><link rel="stylesheet" href="file://__SITE__/css/topology.css">
<style>body{margin:0;background:#111827}</style></head><body class="article-page"><div class="site"><main class="article-layout"><article class="article-column"><div class="prose" id="content"></div></article></article></main></div><pre id="report">pending</pre><script>__JS__</script></body></html>"""
page=page.replace("__SITE__",SITE).replace("__JS__",JS.replace("__MD__",json.dumps(md_join)))
io.open("/home/moon/Projects/ai-tools/verify/check_parts.html","w",encoding="utf-8").write(page)
o=subprocess.run(["/usr/bin/chromium","--headless","--no-sandbox","--disable-gpu","--window-size=1280,900","--virtual-time-budget=6000","--dump-dom","file:///home/moon/Projects/ai-tools/verify/check_parts.html"],capture_output=True,text=True,timeout=90).stdout
m=re.search(r'<pre id="report">(.*?)</pre>',o,re.S)
d=json.loads(m.group(1))
print("platform I:",d["platformI"])
print("parts nodes:",len(d["parts"]))
for n,links in d["parts"]:
    print(f'  {n:10}', " | ".join(f"{t}->{h}" for t,h,_ in links))
print("flow paths:")
for c,dd in d["flow"]: print("  ",c,dd[:90])
