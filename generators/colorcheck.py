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
document.getElementById('content').innerHTML=DOMPurify.sanitize(parsed,{{ADD_TAGS:['figure','figcaption'],ADD_ATTR:['id','class','style','data-spec','aria-label','role','fill','r'],ALLOW_DATA_ATTR:true}});
Topology.init();
setTimeout(function(){{
 var r=document.querySelector('.topology');
 var dots=[];
 var nodes=r.querySelectorAll('.topo-dot');
 for(var i=0;i<nodes.length;i++){{var c=getComputedStyle(nodes[i]);dots.push({{cls:nodes[i].getAttribute('class'),fill:c.fill,stroke:c.stroke,op:c.opacity,filter:c.filter,r:nodes[i].getAttribute('r')}});}}
 var blacks=[];
 var all=r.querySelectorAll('*');
 for(var j=0;j<all.length;j++){{var el=all[j];var c=getComputedStyle(el);
   if(c.fill==='rgb(0, 0, 0)'||c.stroke==='rgb(0, 0, 0)'||c.backgroundColor==='rgb(0, 0, 0)'){{blacks.push({{tag:el.tagName,cls:el.getAttribute('class')||'',fill:c.fill,stroke:c.stroke,bg:c.backgroundColor}});}}
 }}
 document.getElementById('report').textContent=JSON.stringify({{dots:dots,blacks:blacks}});
}},900);
</script></body></html>"""
io.open("/home/moon/Projects/ai-tools/snapshots/design/color.html","w",encoding="utf-8").write(page)
o=subprocess.run(["/usr/bin/chromium","--headless","--no-sandbox","--disable-gpu","--window-size=1280,900","--virtual-time-budget=6000","--dump-dom","file:///home/moon/Projects/ai-tools/snapshots/design/color.html"],capture_output=True,text=True,timeout=90).stdout
m=re.search(r'<pre id="report">(.*?)</pre>',o,re.S)
d=json.loads(m.group(1))
print("DOTS")
for x in d["dots"]: print(" ",x)
print("BLACKS",len(d["blacks"]))
for x in d["blacks"][:20]: print(" ",x)
