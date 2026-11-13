import io, json, re

BASE = "/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture"
LANGS = ["en", "id", "ms", "tl"]

HREF = {
    "si-javascript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
    "si-typescript": "https://www.typescriptlang.org/",
    "si-nodejs": "https://nodejs.org/",
    "si-bun": "https://bun.sh/",
    "si-express": "https://expressjs.com/",
    "si-mongodb": "https://www.mongodb.com/",
    "si-angular": "https://angular.dev/",
    "si-react": "https://react.dev/",
    "si-vue": "https://vuejs.org/",
    "si-postgresql": "https://www.postgresql.org/",
    "si-mysql": "https://www.mysql.com/",
    "si-mariadb": "https://mariadb.org/",
    "si-sqlite": "https://www.sqlite.org/",
    "si-prisma": "https://www.prisma.io/",
    "si-tailwindcss": "https://tailwindcss.com/",
    "si-nextdotjs": "https://nextjs.org/",
    "si-jamstack": "https://jamstack.org/",
    "si-php": "https://www.php.net/",
    "si-laravel": "https://laravel.com/",
    "si-symfony": "https://symfony.com/",
    "si-linux": "https://www.kernel.org/",
    "si-apache": "https://httpd.apache.org/",
    "si-nginx": "https://nginx.org/",
    "si-windows": "https://www.microsoft.com/windows",
    "si-freebsd": "https://www.freebsd.org/",
    "si-perl": "https://www.perl.org/",
    "si-python": "https://www.python.org/",
    "si-django": "https://www.djangoproject.com/",
    "si-fastapi": "https://fastapi.tiangolo.com/",
    "si-flask": "https://flask.palletsprojects.com/",
    "si-dotnet": "https://dotnet.microsoft.com/",
    "si-openjdk": "https://openjdk.org/",
    "si-spring": "https://spring.io/projects/spring-boot",
    "si-quarkus": "https://quarkus.io/",
    "si-ruby": "https://www.ruby-lang.org/",
    "si-rubyonrails": "https://rubyonrails.org/",
    "si-go": "https://go.dev/",
    "si-rust": "https://www.rust-lang.org/",
    "si-wazuh": "https://wazuh.com/",
    "si-elasticsearch": "https://www.elastic.co/elasticsearch",
    "si-logstash": "https://www.elastic.co/logstash",
    "si-kibana": "https://www.elastic.co/kibana",
    "si-prometheus": "https://prometheus.io/",
    "si-grafana": "https://grafana.com/",
    "si-influxdb": "https://www.influxdata.com/",
}

def dump(obj, indent=0):
    pad = "  " * indent
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        items = []
        for k, v in obj.items():
            items.append(pad + "  " + json.dumps(k) + ": " + dump(v, indent + 1))
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(obj, list):
        if not obj:
            return "[]"
        inline = json.dumps(obj, ensure_ascii=False)
        if len(inline) <= 110:
            return inline
        items = [pad + "  " + dump(v, indent + 1) for v in obj]
        return "[\n" + ",\n".join(items) + "\n" + pad + "]"
    return json.dumps(obj, ensure_ascii=False)

def transform(block):
    if not block.get("dense"):
        return block
    block.pop("caption", None)
    block.pop("captionHref", None)
    block["root"] = ["Solution Stack", "", "layers", "out",
                     "https://en.wikipedia.org/wiki/Solution_stack"]
    nodes = block["nodes"]
    for nid, n in nodes.items():
        icons = n.get("icons") if isinstance(n, dict) else (n[2] if len(n) > 2 and isinstance(n[2], list) else None)
        if isinstance(icons, list):
            out = []
            for it in icons:
                if isinstance(it, str):
                    out.append([it, HREF.get(it, "")] if HREF.get(it) else it)
                else:
                    out.append(it)
            if isinstance(n, dict):
                n["icons"] = out
            else:
                n[2] = out
    # JS/TS leader gets both logos.
    nodes["js"] = ["JS / TS", "", ["si-javascript", "si-typescript"], "out",
                   "https://en.wikipedia.org/wiki/JavaScript"]
    # Infra points at computer/IT infrastructure, not a building.
    nodes["infra"] = ["Infra", "", "server", "out",
                      "https://en.wikipedia.org/wiki/IT_infrastructure"]
    return block

for lang in LANGS:
    path = f"{BASE}/server-single-tier-stack-{lang}.md"
    text = io.open(path, encoding="utf-8").read()
    blocks = list(re.finditer(r"```topology\n(.*?)\n```", text, re.S))
    out = text
    for m in reversed(blocks):
        block = json.loads(m.group(1))
        new = transform(block)
        body = dump(new)
        out = out[:m.start(1)] + body + out[m.end(1):]
    io.open(path, "w", encoding="utf-8").write(out)
    print("updated", lang)
