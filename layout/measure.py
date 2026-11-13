import io
import json
import re
import subprocess
import sys

SITE = "/home/moon/Projects/imoon07.github.io"
ARTICLE = ("/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/"
           "server-architecture/server-single-tier-stack-en.md")
BLOCK = int(sys.argv[1]) if len(sys.argv) > 1 else 0

md = io.open(ARTICLE, encoding="utf-8").read()
specs = re.findall(r"```topology\n(.*?)\n```", md, re.S)
md_block = "```topology\n" + specs[BLOCK] + "\n```\n"

html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<script src="file:///home/moon/Projects/ai-tools/vendor/marked.min.js"></script><script src="file:///home/moon/Projects/ai-tools/vendor/purify.min.js"></script>
<script src="file://{SITE}/js/markdown.js"></script><script src="file://{SITE}/js/topology-icons.js"></script><script src="file://{SITE}/js/topology.js"></script>
<link rel="stylesheet" href="file://{SITE}/css/shell.css"><link rel="stylesheet" href="file://{SITE}/css/article.css"><link rel="stylesheet" href="file://{SITE}/css/topology.css">
<style>body{{margin:0;background:#111827}}</style></head><body class="article-page">
<div class="site"><main class="article-layout" id="article-layout"><article class="article-column"><div class="prose" id="content"></div></article></article></main></div>
<pre id="report">pending</pre>
<script>
const MD={json.dumps(md_block)};
const sanitized=DOMPurify.sanitize(marked.parse(MD,{{gfm:true}}),{{ADD_TAGS:['figure','figcaption','details','summary','mark','kbd','sub','sup','dl','dt','dd','iframe','section','video','source'],ADD_ATTR:['target','rel','align','id','loading','decoding','start','style','class','width','height','frameborder','allowfullscreen','allow','controls','poster','preload','muted','playsinline','loop','autoplay','colspan','rowspan','open','role','title','dir','lang','tabindex','name','value','type','checked','disabled','readonly','selected','multiple','spellcheck','referrerpolicy','sandbox','srcset','sizes','data-math'],ALLOW_DATA_ATTR:true}});
document.getElementById('content').innerHTML=sanitized; Topology.init();
setTimeout(()=>{{const r=document.querySelector('.topology'),c=r.querySelector('.topo-canvas'),cr=c.getBoundingClientRect();
const nodes=[...r.querySelectorAll('.topo-node')].map(n=>{{const b=n.getBoundingClientRect();return {{id:n.dataset.node,x:Math.round(b.left-cr.left),y:Math.round(b.top-cr.top),w:Math.round(b.width),h:Math.round(b.height),right:Math.round(b.left-cr.left+b.width),bottom:Math.round(b.top-cr.top+b.height),cx:Math.round(b.left-cr.left+b.width/2),cy:Math.round(b.top-cr.top+b.height/2)}};}});
const paths=[...r.querySelectorAll('.topo-svg path')].map(p=>{{let bb;try{{bb=p.getBBox()}}catch(e){{return null}}return {{cls:p.getAttribute('class'),d:p.getAttribute('d'),x1:Math.round(bb.x),y1:Math.round(bb.y),x2:Math.round(bb.x+bb.width),y2:Math.round(bb.y+bb.height)}};}}).filter(Boolean);
const badges=[...r.querySelectorAll('.topo-svg g')].map(g=>g.textContent).filter(Boolean);
document.getElementById('report').textContent=JSON.stringify({{canvas:[cr.width,cr.height],zoom:r.querySelector('.topo-canvas').style.zoom,nodes,paths,badges}});}},900);
</script></body></html>"""
io.open("/home/moon/Projects/ai-tools/layout/measure.html", "w", encoding="utf-8").write(html)

out = subprocess.run(["/usr/bin/chromium", "--headless", "--no-sandbox", "--disable-gpu",
                      "--window-size=1280,900", "--virtual-time-budget=7000",
                      "--dump-dom", "file:///home/moon/Projects/ai-tools/layout/measure.html"],
                     capture_output=True, text=True, timeout=90).stdout
m = re.search(r'<pre id="report">(.*?)</pre>', out, re.S)
d = json.loads(m.group(1))
print("canvas", d["canvas"], "zoom", d["zoom"], "badges", d["badges"])
print("NODES:")
for n in d["nodes"]:
    print(f"  {n['id']:>3} x={n['x']}..{n['right']} y={n['y']}..{n['bottom']} c=({n['cx']},{n['cy']})")
print("PATHS:")
for p in d["paths"]:
    print(f"  {str(p['cls']):<18} bbox=({p['x1']},{p['y1']})..({p['x2']},{p['y2']}) d={p['d']}")