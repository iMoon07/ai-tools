import re, io, html, subprocess, json

p = "Experiments/foundations/server-architecture/server-single-tier-stack-id.md"
t = io.open(p, encoding="utf-8", newline="").read()
blocks = re.findall(r"```mermaid\n(.*?)```", t, re.S)

variants = []
for i, b in enumerate(blocks):
    for d in ("TD", "LR"):
        bb = re.sub(r"^flowchart (TD|TB|LR|RL|BT)$", f"flowchart {d}", b, count=1, flags=re.M)
        variants.append((i, d, bb))

parts = []
for k, (i, d, b) in enumerate(variants):
    parts.append(f'<div class="diagram mermaid" data-k="{k}">{html.escape(b.strip())}</div>')

page = f'''<!DOCTYPE html><html><head><meta charset="utf-8">
<script src="file:///home/moon/Projects/ai-tools/vendor/mermaid.min.js"></script></head><body>
{''.join(parts)}
<pre id="report">pending</pre>
<script>
mermaid.initialize({{startOnLoad:false,theme:'dark',securityLevel:'loose',fontFamily:'Inter, sans-serif'}});
mermaid.run({{querySelector:'.mermaid'}}).then(()=>{{
  const rows=[];
  document.querySelectorAll('.diagram').forEach(d=>{{
    const svg=d.querySelector('svg'); const b=svg.getBBox();
    const links=svg.querySelectorAll('a').length;
    const urls=[...svg.querySelectorAll('a')].map(a=>a.getAttribute('href')||a.getAttribute('xlink:href')).filter(Boolean);
    rows.push(`k=${{d.dataset.k}} ${{Math.round(b.width)}}x${{Math.round(b.height)}} links=${{links}} hasMultiTier=${{urls.some(u=>u.includes('Multitier'))}}`);
  }});
  document.getElementById('report').textContent=rows.join('\\n');
}}).catch(e=>{{document.getElementById('report').textContent='ERR '+e.message;}});
</script></body></html>'''
io.open("/home/moon/Projects/ai-tools/generators/variants.html","w",encoding="utf-8").write(page)
print("variants", len(variants))
