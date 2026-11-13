import re, io, html

p = "Experiments/foundations/server-architecture/server-single-tier-stack-id.md"
t = io.open(p, encoding="utf-8", newline="").read()
blocks = re.findall(r"```mermaid\n(.*?)```", t, re.S)

parts = []
for i, b in enumerate(blocks):
    parts.append(f'''
    <div class="viewer">
      <div class="stage"><div class="canvas"><div class="diagram mermaid">{html.escape(b.strip())}</div></div></div>
      <div class="cap">block {i}</div>
    </div>''')

page = f'''<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  body {{ margin:0; background:#111827; font-family: Inter, system-ui, sans-serif; padding:24px; }}
  .viewer {{ margin:0 0 28px; border:1px solid #30363d; border-radius:8px; background:#111827; overflow:hidden; }}
  .stage {{ position:relative; height:420px; overflow:hidden; background:
      radial-gradient(circle at 1px 1px, rgba(255,255,255,0.04) 1px, transparent 0) 0 0 / 20px 20px, #111827; }}
  .canvas {{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center; }}
  .diagram svg {{ max-width:none; height:auto; }}
  .cap {{ padding:6px 10px; border-top:1px solid #30363d; color:#8b949e; font-size:12px; }}
  #report {{ color:#3fb950; font:12px monospace; white-space:pre; }}
</style>
<script src="file:///home/moon/Projects/ai-tools/vendor/mermaid.min.js"></script>
</head><body>
{''.join(parts)}
<pre id="report">pending</pre>
<script>
  mermaid.initialize({{ startOnLoad:false, theme:'dark', securityLevel:'strict',
    fontFamily:'Inter, Segoe UI, system-ui, sans-serif' }});
  mermaid.run({{ querySelector: '.mermaid' }}).then(() => {{
    const rows = [];
    document.querySelectorAll('.diagram').forEach((d, i) => {{
      const svg = d.querySelector('svg');
      const b = svg.getBBox();
      const links = svg.querySelectorAll('a').length;
      const fills = [...new Set([...svg.querySelectorAll('.node rect, .node polygon, .node path')].map(n => getComputedStyle(n).fill))].slice(0,6);
      rows.push(`block ${{i}}: bbox=${{Math.round(b.width)}}x${{Math.round(b.height)}} links=${{links}} fills=${{fills.join(',')}}`);
    }});
    document.getElementById('report').textContent = rows.join('\\n');
  }}).catch(e => {{ document.getElementById('report').textContent = 'ERR ' + e.message; }});
</script>
</body></html>'''

io.open("/home/moon/Projects/ai-tools/js-extracts/preview.html","w",encoding="utf-8").write(page)
print("blocks", len(blocks))
