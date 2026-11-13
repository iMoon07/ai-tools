import io, json, re, sys

BASE = "/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture"

CATS = [
    ["mean", "mern", "mevn", "pern", "nextjs", "t3", "jamstack", "bun"],
    ["laravel", "symfony", "lamp", "lemp", "wamp", "wimp", "famp", "xampp"],
    ["django", "fastapi", "flask", "pyramid"],
    ["aspnet", "blazor"],
    ["spring", "jakarta", "quarkus"],
    ["rails", "sinatra"],
    ["gin", "echo", "fiber", "gostd"],
    ["actix", "axum", "rocket"],
    ["wazuh", "elk", "promgraf", "tick"],
]

ROOT_ICON = ["si-javascript", "si-php", "si-python", "si-dotnet", "si-openjdk",
             "si-ruby", "si-go", "si-rust", "server"]

ROOT_SUB = {
    "en": "= This category",
    "id": "= Kategori ini",
    "ms": "= Kategori ini",
    "tl": "= Kategoryang ito",
}

GRID = {8: 2, 4: 2, 3: 3, 2: 2}


def clean_title(heading):
    t = heading.split(". ", 1)[1].strip()
    for suf in (" Stack", " Tindanan", " Tumpukan"):
        if t.endswith(suf):
            t = t[: -len(suf)]
    for pre in ("Tindanan ", "Tumpukan "):
        if t.startswith(pre):
            t = t[len(pre):]
    return t


def block_for(nodes, ids, title, sub, icon, app_node):
    stacks = [i for i in ids if i in nodes]
    spec = {
        "title": title,
        "columns": [
            {"nodes": ["root"]},
            {"nodes": stacks, "grid": GRID.get(len(stacks), 2)},
            {"nodes": ["app"]},
        ],
        "nodes": {
            "root": {
                "label": title,
                "sub": sub,
                "icon": icon,
                "kind": "out",
            },
            "app": app_node,
        },
        "edges": [],
    }
    for sid in stacks:
        spec["nodes"][sid] = nodes[sid]
        spec["edges"].append({"from": "root", "to": sid})
    for sid in stacks:
        spec["edges"].append({"from": sid, "to": "app"})
    return spec


def fix_icons(nodes):
    nodes["bun"]["icon"] = "si-bun"
    nodes["famp"]["icon"] = "si-freebsd"
    nodes["wazuh"]["icon"] = "si-wazuh"
    return nodes


def process(lang):
    path = f"{BASE}/server-single-tier-stack-{lang}.md"
    text = io.open(path, encoding="utf-8").read()

    blocks = list(re.finditer(r"```topology\n(.*?)\n```", text, re.S))
    if len(blocks) != 3:
        print(lang, "unexpected block count", len(blocks))
        return
    big = blocks[1]
    spec = json.loads(big.group(1))
    nodes = fix_icons(spec["nodes"])

    # remove the old mega block plus one trailing blank line
    start, end = big.start(), big.end()
    while end < len(text) and text[end] == "\n":
        end += 1
    text = text[:start] + text[end:]

    lines = text.split("\n")
    heads = [i for i, l in enumerate(lines) if l.startswith("### ")]
    first9 = heads[:9]
    assert len(first9) == 9, (lang, len(first9))

    inserts = []
    for n, hi in enumerate(first9):
        heading = lines[hi]
        title = clean_title(heading)
        # first table row after the heading
        ti = hi + 1
        while ti < len(lines) and not lines[ti].startswith("|"):
            ti += 1
        spec_n = block_for(nodes, CATS[n], title, ROOT_SUB[lang], ROOT_ICON[n], spec["nodes"]["app"])
        js = json.dumps(spec_n, indent=2, ensure_ascii=False)
        inserts.append((ti, js))

    # apply from bottom to top so indices stay valid
    for ti, js in sorted(inserts, reverse=True):
        lines[ti:ti] = ["```topology", js, "```", ""]

    out = "\n".join(lines)
    out = re.sub(r"\n{3,}", "\n\n", out)
    io.open(path, "w", encoding="utf-8").write(out)
    print(lang, "split ok; blocks now", len(re.findall(r"```topology", out)))


for lang in sys.argv[1:] or ["en"]:
    process(lang)