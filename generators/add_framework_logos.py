import io, json, re
from pathlib import Path

BASE = Path("/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture")
LANGS = ["en", "id", "ms", "tl"]

UPD = {
    "pyramid": [("si-python", "https://www.python.org/"), ("si-pyramid", "https://trypyramid.com/")],
    "blazor": [("si-dotnet", "https://dotnet.microsoft.com/"), ("si-blazor", "https://dotnet.microsoft.com/apps/aspnet/web-apps/blazor")],
    "jakarta": [("si-openjdk", "https://openjdk.org/"), ("si-jakartaee", "https://jakarta.ee/")],
    "sinatra": [("si-ruby", "https://www.ruby-lang.org/"), ("si-sinatra", "https://sinatrarb.com/")],
    "gin": [("si-go", "https://go.dev/"), ("si-gin", "https://gin-gonic.com/")],
    "echo": [("si-go", "https://go.dev/"), ("si-echo", "https://echo.labstack.com/")],
    "fiber": [("si-go", "https://go.dev/"), ("si-fiber", "https://gofiber.io/")],
    "actix": [("si-rust", "https://www.rust-lang.org/"), ("si-actix", "https://actix.rs/")],
    "axum": [("si-rust", "https://www.rust-lang.org/"), ("si-axum", "https://github.com/tokio-rs/axum")],
    "rocket": [("si-rust", "https://www.rust-lang.org/"), ("si-rocket", "https://rocket.rs/")],
    "wimp": [("si-windows", "https://www.microsoft.com/windows"), ("si-iis", "https://www.iis.net/"),
             ("si-mysql", "https://www.mysql.com/"), ("si-php", "https://www.php.net/")],
    "tick": [("si-telegraf", "https://www.influxdata.com/telegraf/"), ("si-influxdb", "https://www.influxdata.com/"),
             ("si-chronograf", "https://www.influxdata.com/chronograf/"), ("si-kapacitor", "https://www.influxdata.com/kapacitor/")],
    "t3": [("si-typescript", "https://www.typescriptlang.org/"), ("si-trpc", "https://trpc.io/"),
           ("si-prisma", "https://www.prisma.io/"), ("si-nextdotjs", "https://nextjs.org/"),
           ("si-tailwindcss", "https://tailwindcss.com/")],
}

def fmt(label, icons, kind, href):
    out = ["[", '      %s,' % json.dumps(label, ensure_ascii=False), '      "",', "      ["]
    for i, (ic, url) in enumerate(icons):
        out.append('        [%s, %s]%s' % (json.dumps(ic), json.dumps(url), "," if i < len(icons) - 1 else ""))
    out += ["      ],", '      %s,' % json.dumps(kind), '      %s' % json.dumps(href), "    ]"]
    return "\n".join(out)

def value_end(block, start):
    depth, in_str, esc, j = 0, False, False, start
    while j < len(block):
        c = block[j]
        if in_str:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': in_str = False
        else:
            if c == '"': in_str = True
            elif c in "[{": depth += 1
            elif c in "]}":
                depth -= 1
                if depth == 0: return j + 1
            elif c == "," and depth == 0: return j
        j += 1
    raise ValueError("unterminated value")

for lang in LANGS:
    p = BASE / ("server-single-tier-stack-%s.md" % lang)
    text = p.read_text(encoding="utf-8")
    blocks = list(re.finditer(r"```topology\n(.*?)\n```", text, re.S))
    assert len(blocks) == 3, (lang, len(blocks))
    m = blocks[1]
    block = m.group(1)
    old = json.loads(block)
    replacements = []
    for nid, icons in UPD.items():
        key = '    "%s": ' % nid
        i = block.index(key) + len(key)
        j = value_end(block, i)
        node = old["nodes"][nid]
        label, kind, href = node[0], node[3], node[4]
        replacements.append((i, j, fmt(label, icons, kind, href)))
    # apply from the end so spans stay valid
    new_block = block
    for i, j, txt in sorted(replacements, reverse=True):
        new_block = new_block[:i] + txt + new_block[j:]
    json.loads(new_block)  # sanity
    new_text = text[:m.start(1)] + new_block + text[m.end(1):]
    p.write_text(new_text, encoding="utf-8")
    print("updated", lang, "nodes", len(replacements))
