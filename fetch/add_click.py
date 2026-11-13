import re, io

BASE = "Experiments/foundations/server-architecture"
LANGS = ["en", "id", "ms", "tl"]
W = "https://en.wikipedia.org/wiki/"

MAP = [
    [  # block 0: warung / single tier
        ("C", W+"Web_browser", "Web browser"),
        ("P", W+"Web_server", "Web server"),
        ("K", W+"Runtime_system", "Runtime system"),
        ("G", W+"Database", "Database"),
        ("W", W+"Multitier_architecture", "Single-tier architecture"),
    ],
    [  # block 1: technology stack
        ("A", W+"Solution_stack", "Solution stack"),
        ("B", W+"Software_requirements", "Software requirements"),
        ("C", W+"JavaScript", "JavaScript"),
        ("D", W+"PHP", "PHP"),
        ("E", W+"Python_(programming_language)", "Python"),
        ("F", W+".NET", ".NET"),
        ("G", W+"Java_(programming_language)", "Java"),
        ("H", W+"Ruby_(programming_language)", "Ruby"),
        ("I", W+"Go_(programming_language)", "Go"),
        ("J", W+"Rust_(programming_language)", "Rust"),
        ("K", W+"Observability_(software)", "Observability"),
        ("L", W+"Web_application", "Web application"),
    ],
    [  # block 2: platform
        ("A", W+"Software_deployment", "Software deployment"),
        ("B", W+"Deployment_environment", "Deployment environment"),
        ("C", W+"Bare-metal_server", "Bare-metal server"),
        ("D", W+"Virtual_machine", "Virtual machine"),
        ("E", W+"Operating-system-level_virtualization", "OS-level virtualization"),
        ("F", W+"Platform_as_a_service", "Platform as a service"),
        ("G", W+"Serverless_computing", "Serverless computing"),
        ("H", W+"Edge_computing", "Edge computing"),
        ("I", W+"Multitier_architecture", "Single-tier architecture"),
    ],
]

pat = re.compile(r"```mermaid\n(.*?)```", re.S)

for lang in LANGS:
    path = f"{BASE}/server-single-tier-stack-{lang}.md"
    txt = io.open(path, encoding="utf-8", newline="").read()
    ms = list(pat.finditer(txt))
    assert len(ms) == 3, (lang, len(ms))
    out, last = [], 0
    for i, m in enumerate(ms):
        out.append(txt[last:m.start()])
        lines = m.group(1).split("\n")
        cut = next(j for j, ln in enumerate(lines) if ln.startswith("    classDef "))
        head = lines[:cut]
        while head and head[-1].strip() == "":
            head.pop()
        clicks = [f'    click {nid} "{url}" "{tip}" _blank' for nid, url, tip in MAP[i]]
        out.append("```mermaid\n")
        out.append("\n".join(head + [""] + clicks + [""] + lines[cut:]))
        out.append("\n```")
        last = m.end()
    out.append(txt[last:])
    new = "".join(out)
    io.open(path, "w", encoding="utf-8", newline="").write(new)
    print("wrote", lang, len(new))
