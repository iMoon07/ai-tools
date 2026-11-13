import subprocess,re
js = """
<script>
setTimeout(()=>{
 const r=[...document.querySelectorAll('.topology')][1];
 const cols=[...r.querySelectorAll('.topo-col')];
 const out=cols.map((c,i)=>({i,n:c.children.length,h:Math.round(c.getBoundingClientRect().height),w:Math.round(c.getBoundingClientRect().width),grid:c.dataset.grid||''}));
 const nodes=[...r.querySelectorAll('.topo-node')].slice(0,40).map(n=>({t:n.dataset.node,h:Math.round(n.getBoundingClientRect().height)}));
 document.getElementById('report').textContent=JSON.stringify({cols,nodes});
},900);
</script>
"""
page=open('/home/moon/Projects/ai-tools/snapshots/pages/harness-en.html').read()
page=page.replace('setTimeout(()=>{document.getElementById(\'report\').textContent=JSON.stringify(measure());},700);', js)
open('/home/moon/Projects/ai-tools/layout/cols.html','w').write(page)
out=subprocess.run(["/usr/bin/chromium","--headless","--no-sandbox","--disable-gpu","--window-size=1280,900","--virtual-time-budget=4000","--dump-dom","file:///home/moon/Projects/ai-tools/layout/cols.html"],capture_output=True,text=True,timeout=90).stdout
m=re.search(r'<pre id="report">(.*?)</pre>',out,re.S)
print(m.group(1)[:2000])
