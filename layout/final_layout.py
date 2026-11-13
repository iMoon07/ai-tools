import re, io, json

BASE = "Experiments/foundations/server-architecture"
LANGS = ["en", "id", "ms", "tl"]

def init(fs=12, ns=10, rs=14, pad=4):
    tv = {"fontFamily":"Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif",
          "fontSize":f"{fs}px","background":"transparent","primaryColor":"#1f2937",
          "primaryTextColor":"#e6edf3","primaryBorderColor":"#30363d","lineColor":"#4b5563",
          "textColor":"#cbd5e1","mainBkg":"#1f2937","nodeBorder":"#30363d",
          "clusterBkg":"transparent","clusterBorder":"#30363d","edgeLabelBackground":"#111827"}
    cfg = {"theme":"base","flowchart":{"curve":"basis","nodeSpacing":ns,"rankSpacing":rs,"padding":pad},
           "themeVariables":tv,
           "themeCSS":".node rect, .node polygon, .node circle, .node ellipse { rx: 8px; ry: 8px; } .cluster rect { rx: 12px; ry: 12px; } .edgeLabel rect { fill: #111827; } .edgeLabel span { color: #cbd5e1; }"}
    return "%%{init: " + json.dumps(cfg) + "}%%"

pat = re.compile(r"```mermaid\n(.*?)```", re.S)

for lang in LANGS:
    path = f"{BASE}/server-single-tier-stack-{lang}.md"
    txt = io.open(path, encoding="utf-8", newline="").read()
    ms = list(pat.finditer(txt))
    out, last = [], 0
    for i, m in enumerate(ms):
        out.append(txt[last:m.start()])
        lines = m.group(1).split("\n")
        for j, ln in enumerate(lines):
            if ln.startswith("%%{init"):
                lines[j] = init()
            if re.match(r"^flowchart (TD|TB|LR|RL|BT)$", ln.strip()):
                lines[j] = "flowchart TD"
        lines = [ln for ln in lines if not ln.startswith('    click W ')]
        out.append("```mermaid\n" + "\n".join(lines) + "\n```")
        last = m.end()
    out.append(txt[last:])
    io.open(path, "w", encoding="utf-8", newline="").write("".join(out))
    print("ok", lang)
