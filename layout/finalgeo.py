import io,json,re,subprocess,sys
SITE="/home/moon/Projects/imoon07.github.io"
lang=sys.argv[1] if len(sys.argv)>1 else "en"
md=io.open(f"/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture/server-single-tier-stack-{lang}.md",encoding="utf-8").read()
specs=re.findall(r"```topology\n(.*?)\n```",md,re.S)
md_join="\n\n".join("```topology\n"+s+"\n```" for s in specs)
JS = r"""
document.getElementById('content').innerHTML=DOMPurify.sanitize(marked.parse(MD,{gfm:true}),{ADD_TAGS:['figure','figcaption'],ADD_ATTR:['id','class','style','data-spec','aria-label','role','fill','r','href','target','rel','title'],ALLOW_DATA_ATTR:true});
Topology.init();
setTimeout(function(){
var out=[];
document.querySelectorAll('.topology').forEach(function(r,bi){
  var c=r.querySelector('.topo-canvas'), cr=c.getBoundingClientRect();
  var ns=[].slice.call(r.querySelectorAll('.topo-node[data-node]')).map(function(n){var b=n.getBoundingClientRect();return [n.dataset.node,Math.round(b.left-cr.left),Math.round(b.top-cr.top),Math.round(b.width),Math.round(b.height)];});
  var ps=[].slice.call(r.querySelectorAll('.topo-svg path')).filter(function(p){return p.getAttribute('class');}).map(function(p){return [p.getAttribute('class'),p.getAttribute('d')];});
  out.push({bi:bi,canvas:[Math.round(c.offsetWidth),Math.round(c.offsetHeight)],zoom:c.style.zoom,root:!!r.querySelector('.topo-root-node'),iconLinks:r.querySelectorAll('.topo-node-icon-link').length,nodes:ns,paths:ps});
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
page = page.replace("__SITE__", SITE).replace("__MD__", json.dumps(md_join)).replace("__JS__", JS)
io.open("/home/moon/Projects/ai-tools/layout/finalgeo.html","w",encoding="utf-8").write(page)
for w,h in [(1280,900),(390,844)]:
    o=subprocess.run(["/usr/bin/chromium","--headless","--no-sandbox","--disable-gpu",f"--window-size={w},{h}","--virtual-time-budget=5000","--dump-dom","file:///home/moon/Projects/ai-tools/layout/finalgeo.html"],capture_output=True,text=True,timeout=90).stdout
    m=re.search(r'<pre id="report">(.*?)</pre>',o,re.S)
    d=json.loads(m.group(1))
    print(f"## {lang} {w}x{h}")
    for b in d:
        xs=[n[1] for n in b['nodes']]; xe=[n[1]+n[3] for n in b['nodes']]
        print(f" block{b['bi']} canvas={b['canvas']} zoom={b['zoom']} root={b['root']} iconLinks={b['iconLinks']} nodeSpan={min(xs) if xs else '-'}..{max(xe) if xe else '-'}")
        if b['bi']==0:
            fwd=[p[1] for p in b['paths'] if p[0]=='topo-edge--flow']
            back=[p[1] for p in b['paths'] if p[0]=='topo-edge--back']
            print("   flow paths",len(fwd),"back",len(back))
            for p in back: print("    ",p[:80])
        if b['bi']==2:
            for p in b['paths'][:4]: print("    ",p[0],(p[1] or '')[:70])
