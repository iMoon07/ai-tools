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
<script src="https://cdn.jsdelivr.net/npm/marked@15.0.12/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/dompurify@3.2.4/dist/purify.min.js"></script>
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
const MD={json.dumps(md_block)};
const parsed=marked.parse(MD,{{gfm:true}});
document.getElementById('content').innerHTML=DOMPurify.sanitize(parsed,{{ADD_TAGS:['figure','figcaption'],ADD_ATTR:['id','class','style','href','data-spec'],ALLOW_DATA_ATTR:true}});
Topology.init();
setTimeout(()=>{{
  const r=document.querySelector('.topology');
  const out=[];
  r.querySelectorAll('path,circle,rect,text,use,ellipse,polygon,line').forEach(el=>{{
    const cs=getComputedStyle(el);
    const bb=el.getBBox?el.getBBox():null;
    out.push({{tag:el.tagName.toLowerCase(),cls:el.getAttribute('class')||'',id:el.id||'',
      fill:cs.fill,stroke:cs.stroke,filter:cs.filter,opacity:cs.opacity,
      sw:cs.strokeWidth,
      box:bb?[Math.round(bb.x),Math.round(bb.y),Math.round(bb.width),Math.round(bb.height)]:null,
      text:(el.textContent||'').slice(0,20)}});
  }});
  document.getElementById('report').textContent=JSON.stringify(out);
}},900);
</script></body></html>"""
io.open("/home/moon/Projects/ai-tools/layout/diag.html", "w", encoding="utf-8").write(html)

out = subprocess.run(["/usr/bin/chromium", "--headless", "--no-sandbox", "--disable-gpu",
                      "--window-size=1280,900", "--virtual-time-budget=8000",
                      "--dump-dom", "file:///home/moon/Projects/ai-tools/layout/diag.html"],
                     capture_output=True, text=True, timeout=90).stdout
m = re.search(r'<pre id="report">(.*?)</pre>', out, re.S)
for e in json.loads(m.group(1)):
    print(f"{e['tag']:<8} {e['cls'][:22]:<22} fill={e['fill'][:22]:<22} stroke={e['stroke'][:18]:<18} "
          f"filter={e['filter'][:24]:<24} op={e['opacity'][:4]:<4} box={e['box']} {e['text']}")