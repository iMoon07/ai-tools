import re, io, json

BASE = "Experiments/foundations/server-architecture"
LANGS = ["en", "id", "ms", "tl"]

INIT = ('%%{init: {"theme": "base", "flowchart": {"curve": "basis", "nodeSpacing": 40, '
        '"rankSpacing": 50, "padding": 10}, "themeVariables": {"fontFamily": "Inter, '
        'ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif", "fontSize": "14px", '
        '"background": "transparent", "primaryColor": "#1f2937", "primaryTextColor": "#e6edf3", '
        '"primaryBorderColor": "#30363d", "lineColor": "#4b5563", "textColor": "#cbd5e1", '
        '"mainBkg": "#1f2937", "nodeBorder": "#30363d", "clusterBkg": "transparent", '
        '"clusterBorder": "#30363d", "edgeLabelBackground": "#111827"}, "themeCSS": '
        '".node rect, .node polygon, .node circle, .node ellipse { rx: 8px; ry: 8px; } '
        '.cluster rect { rx: 12px; ry: 12px; } .edgeLabel rect { fill: #111827; } '
        '.edgeLabel span { color: #cbd5e1; }"}}%%')

SUF0 = """    classDef actor fill:#1f2937,stroke:#58a6ff,color:#e6edf3,stroke-width:1.5px
    classDef role fill:#1f2937,stroke:#30363d,color:#e6edf3,stroke-width:1.5px
    classDef store fill:#1f2937,stroke:#3fb950,color:#e6edf3,stroke-width:1.5px

    class C actor
    class P,K role
    class G store
    style W fill:transparent,stroke:#30363d,stroke-width:1px,color:#8b949e"""

SUF1 = """    classDef root fill:#1f2937,stroke:#58a6ff,color:#e6edf3,stroke-width:1.5px
    classDef choice fill:#1f2937,stroke:#d29922,color:#e6edf3,stroke-width:1.5px
    classDef tech fill:#1f2937,stroke:#30363d,color:#e6edf3,stroke-width:1.5px
    classDef out fill:#1f2937,stroke:#58a6ff,color:#e6edf3,stroke-width:1.5px

    class A root
    class B choice
    class C,D,E,F,G,H,I,J,K tech
    class L out"""

SUF2 = """    classDef root fill:#1f2937,stroke:#58a6ff,color:#e6edf3,stroke-width:1.5px
    classDef choice fill:#1f2937,stroke:#d29922,color:#e6edf3,stroke-width:1.5px
    classDef host fill:#1f2937,stroke:#30363d,color:#e6edf3,stroke-width:1.5px
    classDef out fill:#1f2937,stroke:#58a6ff,color:#e6edf3,stroke-width:1.5px

    class A root
    class B choice
    class C,D,E,F,G,H host
    class I out"""

SUF = [SUF0, SUF1, SUF2]
pat = re.compile(r"```mermaid\n(.*?)```", re.S)

for lang in LANGS:
    path = f"{BASE}/server-single-tier-stack-{lang}.md"
    txt = io.open(path, encoding="utf-8", newline="").read()
    ms = list(pat.finditer(txt))
    assert len(ms) == 3, (lang, len(ms))
    out, last = [], 0
    for i, m in enumerate(ms):
        out.append(txt[last:m.start()])
        out.append("```mermaid\n")
        lines = m.group(1).split("\n")
        # replace init line
        for j, ln in enumerate(lines):
            if ln.startswith("%%{init"):
                lines[j] = INIT
                break
        # layout direction
        for j, ln in enumerate(lines):
            if re.match(r"^flowchart (TD|TB|LR|RL|BT)$", ln.strip()):
                lines[j] = "flowchart LR" if i in (1, 2) else "flowchart TD"
                break
        # cut old classDef/class/style tail
        cut = next((j for j, ln in enumerate(lines) if ln.startswith("    classDef ")), len(lines))
        lines = lines[:cut]
        while lines and lines[-1].strip() == "":
            lines.pop()
        lines.append("")
        lines.append(SUF[i])
        out.append("\n".join(lines))
        out.append("\n```")
        last = m.end()
    out.append(txt[last:])
    new = "".join(out)
    io.open(path, "w", encoding="utf-8", newline="").write(new)
    print("wrote", lang, len(new))
