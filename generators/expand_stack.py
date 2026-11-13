import json
import re

BASE = ("/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/"
        "server-architecture/server-single-tier-stack-%s.md")

STACKS = [
    ["MEAN", "MERN"],
    ["Laravel", "LAMP"],
    ["Django", "FastAPI"],
    ["ASP.NET Core", "Blazor"],
    ["Spring Boot", "Quarkus"],
    ["Rails", "Sinatra"],
    ["Gin", "Fiber"],
    ["Actix", "Axum"],
    ["ELK", "Prometheus + Grafana"],
]

PAT = re.compile(r"```topology\n(.*?)\n```", re.S)


def slug(text):
    return re.sub(r"[^A-Za-z0-9]", "", text)


for lang in ("en", "id", "ms", "tl"):
    path = BASE % lang
    src = open(path, encoding="utf-8").read()
    blocks = list(PAT.finditer(src))
    old = json.loads(blocks[1].group(1))

    A, B, L = old["nodes"]["A"], old["nodes"]["B"], old["nodes"]["L"]
    fam_ids = [k for k, n in old["nodes"].items() if n.get("kind") == "tech"]

    nodes = {"A": A, "B": B, "L": L}
    edges = [{"from": "A", "to": "B"}]
    stack_ids = []
    for fid, stacks in zip(fam_ids, STACKS):
        nodes[fid] = old["nodes"][fid]
        edges.append({"from": "B", "to": fid})
        for s in stacks:
            sid = fid + "x" + slug(s)
            nodes[sid] = {"label": s, "kind": "tech"}
            edges.append({"from": fid, "to": sid})
            edges.append({"from": sid, "to": "L"})
            stack_ids.append(sid)

    spec = {
        "title": old["title"],
        "columns": [
            {"nodes": ["A"]},
            {"nodes": ["B"]},
            {"nodes": fam_ids},
            {"nodes": stack_ids, "grid": 2},
            {"nodes": ["L"]},
        ],
        "nodes": nodes,
        "edges": edges,
    }
    new = "```topology\n" + json.dumps(spec, ensure_ascii=False, separators=(",", ":")) + "\n```"
    b = blocks[1]
    src = src[:b.start()] + new + src[b.end():]
    open(path, "w", encoding="utf-8").write(src)
    print(lang, "stacks", len(stack_ids), "edges", len(edges))