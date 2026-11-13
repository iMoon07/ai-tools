import re, io, html, json

p = "Experiments/foundations/server-architecture/server-single-tier-stack-id.md"
t = io.open(p, encoding="utf-8", newline="").read()
b1 = re.findall(r"```mermaid\n(.*?)```", t, re.S)[1]

def init(fs, ns, rs, pad):
    tv = {"fontFamily":"Inter, ui-sans-serif, system-ui, sans-serif","fontSize":f"{fs}px",
          "background":"transparent","primaryColor":"#1f2937","primaryTextColor":"#e6edf3",
          "primaryBorderColor":"#30363d","lineColor":"#4b5563","textColor":"#cbd5e1",
          "mainBkg":"#1f2937","nodeBorder":"#30363d","clusterBkg":"transparent",
          "clusterBorder":"#30363d","edgeLabelBackground":"#111827"}
    cfg = {"theme":"base","flowchart":{"curve":"basis","nodeSpacing":ns,"rankSpacing":rs,"padding":pad},
           "themeVariables":tv,"themeCSS":".node rect, .node polygon, .node circle, .node ellipse { rx: 8px; ry: 8px; }"}
    return "%%{init: " + json.dumps(cfg) + "}%%"

configs = [("A",14,40,50,10),("B",12,20,30,6),("C",13,25,35,8),("D",12,15,25,4)]
parts=[]
for name,fs,ns,rs,pad in configs:
    body = re.sub(r"^%%\{init.*\}%%$", init(fs,ns,rs,pad), b1, count=1, flags=re.M)
    body = re.sub(r"^flowchart (TD|TB|LR|RL|BT)$", "flowchart TD", body, count=1, flags=re.M)
    parts.append(f'<div class="diagram mermaid" data-k="{name}">{html.escape(body.strip())}</div>')

page=f'''<!DOCTYPE html><html><head><meta charset="utf-8"><script src="file:///home/moon/Projects/ai-tools/vendor/mermaid.min.js"></script></head><body>
{''.join(parts)}<pre id="report">pending</pre>
<script>
mermaid.initialize({{startOnLoad:false,theme:'dark',securityLevel:'loose'}});
mermaid.run({{querySelector:'.mermaid'}}).then(()=>{{
 const rows=[];document.querySelectorAll('.diagram').forEach(d=>{{const b=d.querySelector('svg').getBBox();
 rows.push(`k=${{d.dataset.k}} ${{Math.round(b.width)}}x${{Math.round(b.height)}} fit=${{Math.min(1,1076/${{Math.round(b.width)}},396/${{Math.round(b.height)}}).toFixed(2)}}`);}});
 document.getElementById('report').textContent=rows.join('\\n');
}}).catch(e=>{{document.getElementById('report').textContent='ERR '+e.message;}});
</script></body></html>'''
io.open("/home/moon/Projects/ai-tools/layout/tune.html","w",encoding="utf-8").write(page)
print("ok")
