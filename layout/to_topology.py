import re, io, json

BASE = "Experiments/foundations/server-architecture"
LANGS = ["en", "id", "ms", "tl"]
W = "https://en.wikipedia.org/wiki/"

HREF0 = {"C":"Web_browser","P":"Web_server","K":"Runtime_system","G":"Database"}
ICON0 = {"C":("user","actor"),"P":("server","process"),"K":("cpu","process"),"G":("database","store")}
HREF1 = {"A":"Solution_stack","B":"Software_requirements","C":"JavaScript","D":"PHP",
         "E":"Python_(programming_language)","F":".NET","G":"Java_(programming_language)",
         "H":"Ruby_(programming_language)","I":"Go_(programming_language)","J":"Rust_(programming_language)",
         "K":"Observability_(software)","L":"Web_application"}
ICON1 = {"A":("layers","out"),"B":("git-branch","choice"),"C":("si-javascript","tech"),
         "D":("si-php","tech"),"E":("si-python","tech"),"F":("si-dotnet","tech"),
         "G":("si-openjdk","tech"),"H":("si-ruby","tech"),"I":("si-go","tech"),
         "J":("si-rust","tech"),"K":("si-prometheus","tech"),"L":("app-window","out")}
HREF2 = {"A":"Software_deployment","B":"Deployment_environment","C":"Bare-metal_server",
         "D":"Virtual_machine","E":"Operating-system-level_virtualization",
         "F":"Platform_as_a_service","G":"Serverless_computing","H":"Edge_computing",
         "I":"Multitier_architecture"}
ICON2 = {"A":("package","out"),"B":("git-branch","choice"),"C":("hard-drive","host"),
         "D":("monitor","host"),"E":("box","host"),"F":("cloud","host"),
         "G":("zap","host"),"H":("radio","host"),"I":("layers","out")}

def clean_label(raw):
    parts = raw.split("<br/>")
    head = parts[0]
    # buang emoji/ikon di depan: ambil setelah spasi pertama
    if " " in head:
        head = head.split(" ", 1)[1]
    label = head.strip()
    sub = parts[1].strip() if len(parts) > 1 else ""
    return label, sub

def parse_block(src):
    nodes = {}
    for line in src.split("\n"):
        if line.strip().startswith("subgraph"):
            continue
        for m in re.finditer(r'\b([A-Z])(?:\(\[|\(\(|\[\(|\[|\{)\s*"([^"]*)"', line):
            nid, raw = m.group(1), m.group(2)
            label, sub = clean_label(raw)
            nodes[nid] = (label, sub)
    edges = []
    for line in src.split("\n"):
        if "-->" not in line:
            continue
        left, right = line.split("-->", 1)
        m = re.match(r'\s*([A-Z])\b', left)
        a = m.group(1) if m else None
        if not a:
            m = re.search(r'([A-Z])\s*$', left)
            a = m.group(1) if m else None
        lm = re.search(r'\|"([^"]*)"\|', right)
        elabel = lm.group(1) if lm else ""
        r2 = re.sub(r'^\s*\|"[^"]*"\|\s*', '', right)
        m = re.search(r'([A-Z])\b', r2)
        b = m.group(1) if m else None
        if not a or not b:
            continue
        badge = ""
        mm = re.match(r'\s*(\d+)\.', elabel)
        if mm:
            badge = mm.group(1)
        edges.append((a, b, badge))
    group = None
    gm = re.search(r'subgraph\s+([A-Z])\["([^"]*)"\]', src)
    if gm:
        group = gm.group(2)
    return nodes, edges, group

def build(idx, src, title):
    nodes, edges, group = parse_block(src)
    if idx == 0:
        hrefs, icons = HREF0, ICON0
        order = ["C","P","K","G"]
        cols = [[c] for c in order]
        colidx = {c:i for i,c in enumerate(order)}
    elif idx == 1:
        hrefs, icons = HREF1, ICON1
        order = ["A","B"] + [c for c in "CDEFGHIJK"] + ["L"]
        cols = [["A"],["B"],["C","D","E","F","G","H","I","J","K"],[ "L"]]
        colidx = {n:i for i,col in enumerate(cols) for n in col}
    else:
        hrefs, icons = HREF2, ICON2
        order = ["A","B","C","D","E","F","G","H","I"]
        cols = [["A"],["B"],["C","D","E","F","G","H"],["I"]]
        colidx = {n:i for i,col in enumerate(cols) for n in col}

    spec_nodes = {}
    for nid, (label, sub) in nodes.items():
        if nid not in hrefs:
            continue
        icon, kind = icons[nid]
        spec_nodes[nid] = {"label": label, "sub": sub, "icon": icon, "kind": kind,
                           "href": W + hrefs[nid]}
    # pastikan urutan kolom sesuai yang didefinisikan
    spec_nodes = {nid: spec_nodes[nid] for col in cols for nid in col if nid in spec_nodes}

    spec_edges = []
    for a, b, badge in edges:
        if a not in spec_nodes or b not in spec_nodes:
            continue
        e = {"from": a, "to": b}
        if badge:
            e["badge"] = badge
        if colidx.get(b, 0) < colidx.get(a, 0):
            e["back"] = True
        spec_edges.append(e)

    spec = {"title": title, "columns": [{"nodes": col, **({"grid": 3} if len(col) > 2 else {})} for col in cols],
            "nodes": spec_nodes, "edges": spec_edges}
    if group and idx == 0:
        spec["groups"] = [{"label": group, "nodes": ["P","K","G"]}]
    return spec

pat = re.compile(r"```mermaid\n(.*?)```", re.S)

for lang in LANGS:
    path = f"{BASE}/server-single-tier-stack-{lang}.md"
    txt = io.open(path, encoding="utf-8", newline="").read()
    ms = list(pat.finditer(txt))
    assert len(ms) == 3, (lang, len(ms))
    out, last = [], 0
    for i, m in enumerate(ms):
        out.append(txt[last:m.start()])
        head = txt[:m.start()]
        hm = list(re.finditer(r'^## (.+)$', head, re.M))
        title = hm[-1].group(1).strip() if hm else "Topologi"
        spec = build(i, m.group(1), title)
        out.append("```topology\n" + json.dumps(spec, ensure_ascii=False, separators=(",", ":")) + "\n```")
        last = m.end()
    out.append(txt[last:])
    new = "".join(out)
    io.open(path, "w", encoding="utf-8", newline="").write(new)
    print("ok", lang, "topology blocks", new.count("```topology"))
