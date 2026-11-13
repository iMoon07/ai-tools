import json

fams = [
    ("F1", "JavaScript / TypeScript", "si-javascript", ["MEAN", "MERN"]),
    ("F2", "PHP", "si-php", ["Laravel", "LAMP"]),
    ("F3", "Python", "si-python", ["Django", "FastAPI"]),
    ("F4", ".NET", "si-dotnet", ["ASP.NET Core", "Blazor"]),
    ("F5", "Java", "si-openjdk", ["Spring Boot", "Quarkus"]),
    ("F6", "Ruby", "si-ruby", ["Rails", "Sinatra"]),
    ("F7", "Go", "si-go", ["Gin", "Fiber"]),
    ("F8", "Rust", "si-rust", ["Actix", "Axum"]),
    ("F9", "Infrastructure", "si-prometheus", ["ELK", "Prometheus + Grafana"]),
]

nodes = {
    "A": {"label": "Technology Stack", "sub": "= Recipe and ingredients", "icon": "layers", "kind": "out"},
    "B": {"label": "ingredients based on the menu", "icon": "git-branch", "kind": "choice"},
    "Z": {"label": "Web Application / API", "sub": "tailored to project needs", "icon": "app-window", "kind": "out"},
}
edges = [{"from": "A", "to": "B"}]
fids, sids, ghost = [], [], 0
for fid, label, icon, stacks in fams:
    nodes[fid] = {"label": label, "icon": icon, "kind": "tech"}
    edges.append({"from": "B", "to": fid})
    fids.append(fid)
    for s in stacks:
        sid = fid + "x" + s.replace(" ", "").replace("+", "").replace(".", "")
        nodes[sid] = {"label": s, "kind": "tech"}
        edges.append({"from": fid, "to": sid})
        edges.append({"from": sid, "to": "Z"})
        sids.append(sid)
    while len(stacks) % 2:
        gid = "G%d" % ghost
        ghost += 1
        nodes[gid] = {"hidden": True}
        sids.append(gid)
        stacks.append("")

spec = {
    "title": "Technology Stack Combinations",
    "columns": [{"nodes": ["A"]}, {"nodes": ["B"]}, {"nodes": fids},
                {"nodes": sids, "grid": 2}, {"nodes": ["Z"]}],
    "nodes": nodes,
    "edges": edges,
}
json.dump(spec, open("/home/moon/Projects/ai-tools/snapshots/notes/spec3.json", "w"), ensure_ascii=False)
print("families", len(fids), "stack nodes", len(sids), "ghost", ghost, "edges", len(edges))