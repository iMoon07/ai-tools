import io,json,re,subprocess
SITE="/home/moon/Projects/imoon07.github.io"
md=io.open("/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture/server-single-tier-stack-en.md",encoding="utf-8").read()
specs=re.findall(r"```topology\n(.*?)\n```",md,re.S)
md_join="\n\n".join("```topology\n"+s+"\n```" for s in specs)
JS = r"""
document.getElementById('content').innerHTML=DOMPurify.sanitize(marked.parse(MD,{gfm:true}),{ADD_TAGS:['figure','figcaption'],ADD_ATTR:['id','class','style','data-spec','aria-label','role','fill','r','href','target','rel','title'],ALLOW_DATA_ATTR:true});
Topology.init();
setTimeout(function(){
var out=[];
document.querySelectorAll('.topology').forEach(function(r,bi){
  var dots=r.querySelectorAll('.topo-dot').length, anims=r.querySelectorAll('animateMotion').length;
  var icons={};
  ['js','mean','lamp','elk','pyramid','aspnet','gostd','tick','infra','promgraf'].forEach(function(id){
    var n=r.querySelector('[data-node="'+id+'"]'); if(!n)return;
    var ic=n.querySelector('.topo-node-icon'); var cs=ic?getComputedStyle(ic):null;
    icons[id]=ic?[cs.display,Math.round(ic.getBoundingClientRect().width),Math.round(ic.getBoundingClientRect().height),n.querySelectorAll('.topo-icon').length]:null;
  });
  out.push({bi:bi,dots:dots,anims:anims,icons:icons});
});
document.getElementById('report').textContent=JSON.stringify(out);
},900);
"""
page = """<!DOCTYPE html><html><head><meta charset="utf-8">
<script src="file:///home/moon/Projects/ai-tools/vendor/marked.min.js"></script><script src="file:///home/moon/Projects/ai-tools/vendor/purify.min.js"></script>
<script src="file://__SITE__/js/markdown.js"></script><script src="file://__SITE__/js/topology-icons.js"></script><script src="file://__SITE__/js/topology.js"></script>
<link rel="stylesheet" href="file://__SITE__/css/shell.css"><link rel="stylesheet" href="file://__SITE__/css/article.css"><link rel="stylesheet" href="file://__SITE__/css/topology.css">
<style>body{margin:0;background:#111827}</style></head><body class="article-page"><div class="site"><main class="article-layout"><article class="article-column"><div class="prose" id="content"></div></article></article></main></div><pre id="report">pending</pre>
<script>const MD=__MD__;</script><script>__JS__</script></body></html>"""
page = (page.replace("__SITE__", SITE).replace("__MD__", json.dumps(md_join)).replace("__JS__", JS))
io.open("/home/moon/Projects/ai-tools/verify/checkicons.html","w",encoding="utf-8").write(page)
o=subprocess.run(["/usr/bin/chromium","--headless","--no-sandbox","--disable-gpu","--window-size=1280,900","--virtual-time-budget=5000","--dump-dom","file:///home/moon/Projects/ai-tools/verify/checkicons.html"],capture_output=True,text=True,timeout=90).stdout
m=re.search(r'<pre id="report">(.*?)</pre>',o,re.S)
d=json.loads(m.group(1))
for b in d:
    print("block",b['bi'],"dots",b['dots'],"anims",b['anims'])
    if b['bi']==1:
        for k,v in b['icons'].items(): print("  ",k,v)
