import re, io

BASE = "/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture"
LANGS = ["en", "id", "ms", "tl"]

INIT = ('%%{init: {"theme": "base", "flowchart": {"curve": "basis", "nodeSpacing": 45, '
        '"rankSpacing": 55, "padding": 12}, "themeVariables": {"fontFamily": "Inter, '
        'ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif", "fontSize": "14px", '
        '"background": "transparent", "primaryColor": "#eef2ff", "primaryTextColor": "#1e1b4b", '
        '"primaryBorderColor": "#6366f1", "lineColor": "#94a3b8", "textColor": "#1e293b", '
        '"mainBkg": "#eef2ff", "nodeBorder": "#6366f1", "clusterBkg": "transparent", '
        '"clusterBorder": "#cbd5e1", "edgeLabelBackground": "transparent"}, "themeCSS": '
        '".node rect, .node polygon, .node circle, .node ellipse { rx: 10px; ry: 10px; } '
        '.cluster rect { rx: 14px; ry: 14px; }"}}%%')

SUF0 = """    classDef actor fill:#dbeafe,stroke:#2563eb,color:#0f172a,stroke-width:1.5px
    classDef role fill:#ffedd5,stroke:#ea580c,color:#431407,stroke-width:1.5px
    classDef store fill:#d1fae5,stroke:#059669,color:#064e3b,stroke-width:1.5px

    class C actor
    class P,K role
    class G store
    style W fill:transparent,stroke:#cbd5e1,stroke-width:1px,color:#64748b"""

SUF1 = """    classDef root fill:#eef2ff,stroke:#6366f1,color:#1e1b4b,stroke-width:1.5px
    classDef choice fill:#fef3c7,stroke:#d97706,color:#451a03,stroke-width:1.5px
    classDef tech fill:#ffedd5,stroke:#ea580c,color:#431407,stroke-width:1.5px
    classDef out fill:#e0f2fe,stroke:#0284c7,color:#082f49,stroke-width:1.5px

    class A root
    class B choice
    class C,D,E,F,G,H,I,J,K tech
    class L out"""

SUF2 = """    classDef root fill:#eef2ff,stroke:#6366f1,color:#1e1b4b,stroke-width:1.5px
    classDef choice fill:#fef3c7,stroke:#d97706,color:#451a03,stroke-width:1.5px
    classDef host fill:#ffedd5,stroke:#ea580c,color:#431407,stroke-width:1.5px
    classDef out fill:#e0f2fe,stroke:#0284c7,color:#082f49,stroke-width:1.5px

    class A root
    class B choice
    class C,D,E,F,G,H host
    class I out"""


def transform(block, idx):
    if idx == 0:
        block = re.sub(r'C\["([^"]*)"\]', r'C(["\1"])', block)
        block = re.sub(r'G\["([^"]*)"\]', r'G[("\1")]', block)
        suf = SUF0
    elif idx == 1:
        block = re.sub(r'A\["([^"]*)"\]', r'A(["\1"])', block)
        block = re.sub(r'L\["([^"]*)"\]', r'L(["\1"])', block)
        suf = SUF1
    else:
        block = re.sub(r'A\["([^"]*)"\]', r'A(["\1"])', block)
        block = re.sub(r'I\["([^"]*)"\]', r'I(["\1"])', block)
        suf = SUF2
    lines = block.split("\n")
    lines.insert(0, INIT)
    while lines and lines[-1].strip() == "":
        lines.pop()
    lines.append("")
    lines.append(suf)
    return "\n".join(lines)


pat = re.compile(r"```mermaid\n(.*?)```", re.S)

for lang in LANGS:
    path = f"{BASE}/server-single-tier-stack-{lang}.md"
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        txt = f.read()
    ms = list(pat.finditer(txt))
    assert len(ms) == 3, (lang, len(ms))
    out = []
    last = 0
    for i, m in enumerate(ms):
        out.append(txt[last:m.start()])
        out.append("```mermaid\n")
        out.append(transform(m.group(1), i))
        out.append("\n```")
        last = m.end()
    out.append(txt[last:])
    new = "".join(out)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(new)
    print("wrote", lang, len(new))
