import io,json,re,subprocess
SITE="/home/moon/Projects/imoon07.github.io"
md=io.open("/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture/server-single-tier-stack-en.md",encoding="utf-8").read()
spec=re.findall(r"```topology\n(.*?)\n```",md,re.S)[0]
page=f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<script src="file:///home/moon/Projects/ai-tools/vendor/marked.min.js"></script>
<script src="file:///home/moon/Projects/ai-tools/vendor/purify.min.js"></script>
<script src="file://{SITE}/js/markdown.js"></script>
<script src="file://{SITE}/js/topology-icons.js"></script>
<script src="file://{SITE}/js/topology.js"></script>
<link rel="stylesheet" href="file://{SITE}/css/shell.css">
<link rel="stylesheet" href="file://{SITE}/css/article.css">
<link rel="stylesheet" href="file://{SITE}/css/topology.css">
<style>body{{margin:0;background:#111827}}</style></head><body class="article-page">
<div class="site"><main class="article-layout"><article class="article-column"><div class="prose" id="content"></div></article></article></main></div>
<pre id="report">pending</pre>
<script>
const MD="```topology\\n"+{json.dumps(spec)}+"\\n```\\n";
const parsed=marked.parse(MD,{{gfm:true}});
document.getElementById('content').innerHTML=DOMPurify.sanitize(parsed,{{ADD_TAGS:['figure','figcaption'],ADD_ATTR:['id','class','style','data-spec','aria-label','role'],ALLOW_DATA_ATTR:true}});
Topology.init();
setTimeout(()=>{{
 const r=document.querySelector('.topology');
 const ns=[...r.querySelectorAll('.topo-node')].map(n=>{{const b=n.getBoundingClientRect();return {{id:n.dataset.node,x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height)}};}});
 const ps=[...r.querySelectorAll('.topo-svg > g > path')].map(p=>p.getAttribute('d'));
 const out={{nodes:ns,paths:ps,canvas:r.querySelector('.topo-canvas').getBoundingClientRect().width}};
 document.getElementById('report').textContent=JSON.stringify(out);
}},900);
</script></body></html>"""
io.open("/home/moon/Projects/ai-tools/snapshots/design/flow.html","w",encoding="utf-8").write(page)
o=subprocess.run(["/usr/bin/chromium","--headless","--no-sandbox","--disable-gpu","--window-size=1280,900","--virtual-time-budget=6000","--dump-dom","file:///home/moon/Projects/ai-tools/snapshots/design/flow.html"],capture_output=True,text=True,timeout=90).stdout
m=re.search(r'<pre id="report">(.*?)</pre>',o,re.S)
d=json.loads(m.group(1))
print("canvas",round(d["canvas"]))
for n in d["nodes"]: print("node",n)
for p in d["paths"]: print("path",p)
