import json
import re
import subprocess
import sys

SITE = "/home/moon/Projects/imoon07.github.io"

spec = json.load(open(sys.argv[1], encoding="utf-8"))
md_block = "```topology\n" + json.dumps(spec, ensure_ascii=False, separators=(",", ":")) + "\n```\n"

html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<script src="file:///home/moon/Projects/ai-tools/vendor/marked.min.js"></script><script src="file:///home/moon/Projects/ai-tools/vendor/purify.min.js"></script>
<script src="file://{SITE}/js/markdown.js"></script><script src="file://{SITE}/js/topology-icons.js"></script><script src="file://{SITE}/js/topology.js"></script>
<link rel="stylesheet" href="file://{SITE}/css/shell.css"><link rel="stylesheet" href="file://{SITE}/css/article.css"><link rel="stylesheet" href="file://{SITE}/css/topology.css">
<style>body{{margin:0;background:#111827}}</style></head><body class="article-page">
<div class="site"><main class="article-layout" id="article-layout"><article class="article-column"><div class="prose" id="content"></div></article></article></main></div>
<pre id="report">pending</pre>
<script>
const MD={json.dumps(md_block)};
const sanitized=DOMPurify.sanitize(marked.parse(MD,{{gfm:true}}),{{ADD_TAGS:['figure','figcaption'],ADD_ATTR:['id','class','style','href','data-spec'],ALLOW_DATA_ATTR:true}});
document.getElementById('content').innerHTML=sanitized; Topology.init();
setTimeout(()=>{{const r=document.querySelector('.topology'),c=r.querySelector('.topo-canvas'),cr=c.getBoundingClientRect();
const nodes=[...r.querySelectorAll('.topo-node')].map(n=>{{const b=n.getBoundingClientRect();return {{id:n.dataset.node,x:Math.round(b.left-cr.left),y:Math.round(b.top-cr.top),right:Math.round(b.left-cr.left+b.width),bottom:Math.round(b.top-cr.top+b.height),cx:Math.round(b.left-cr.left+b.width/2),cy:Math.round(b.top-cr.top+b.height/2)}};}});
const paths=[...r.querySelectorAll('.topo-svg > g > path')].map(p=>{{const bb=p.getBBox();return {{cls:p.getAttribute('class'),x1:Math.round(bb.x),y1:Math.round(bb.y),x2:Math.round(bb.x+bb.width),y2:Math.round(bb.y+bb.height)}};}});
const edges=[];for(const n of nodes)for(const m of nodes){{if(n===m)continue;if(n.x<m.x&&n.right>m.x&&n.y<m.bottom&&n.bottom>m.y)edges.push([n.id,m.id]);}}
document.getElementById('report').textContent=JSON.stringify({{canvas:[Math.round(cr.width),Math.round(cr.height)],zoom:c.style.zoom,nodes,paths,edges}});}},900);
</script></body></html>"""
io = open("/home/moon/Projects/ai-tools/test/spec_test.html", "w", encoding="utf-8")
io.write(html)
io.close()

out = subprocess.run(["/usr/bin/chromium", "--headless", "--no-sandbox", "--disable-gpu",
                      "--window-size=1280,900", "--virtual-time-budget=7000",
                      "--dump-dom", "file:///home/moon/Projects/ai-tools/test/spec_test.html"],
                     capture_output=True, text=True, timeout=90).stdout
m = re.search(r'<pre id="report">(.*?)</pre>', out, re.S)
d = json.loads(m.group(1))
print("canvas", d["canvas"], "zoom", d["zoom"], "nodes", len(d["nodes"]), "paths", len(d["paths"]))
print("overlaps:", d["edges"])
# orphan / dangling check from the spec
ids = {n.get("id") for n in d["nodes"] if n.get("id")}
bad = [e for e in spec["edges"] if e["from"] not in ids or e["to"] not in ids]
print("dangling edges:", bad)
used = set()
for e in spec["edges"]:
    used.add(e["from"]); used.add(e["to"])
print("orphan nodes:", sorted(ids - used))
if len(sys.argv) > 2:
    for n in d["nodes"]:
        print(f"  {n['id']:>3} x={n['x']}..{n['right']} y={n['y']}..{n['bottom']}")