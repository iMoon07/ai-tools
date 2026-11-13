import io, json, re
from pathlib import Path

BASE = Path("/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture")
LANGS = ["en", "id", "ms", "tl"]

LABELS = {
 "si-javascript": ("JavaScript", "https://developer.mozilla.org/en-US/docs/Web/JavaScript"),
 "si-typescript": ("TypeScript", "https://www.typescriptlang.org/"),
 "si-nodejs": ("Node.js", "https://nodejs.org/"),
 "si-bun": ("Bun", "https://bun.sh/"),
 "si-express": ("Express", "https://expressjs.com/"),
 "si-mongodb": ("MongoDB", "https://www.mongodb.com/"),
 "si-angular": ("Angular", "https://angular.dev/"),
 "si-react": ("React", "https://react.dev/"),
 "si-vue": ("Vue.js", "https://vuejs.org/"),
 "si-postgresql": ("PostgreSQL", "https://www.postgresql.org/"),
 "si-mysql": ("MySQL", "https://www.mysql.com/"),
 "si-mariadb": ("MariaDB", "https://mariadb.org/"),
 "si-sqlite": ("SQLite", "https://www.sqlite.org/"),
 "si-prisma": ("Prisma", "https://www.prisma.io/"),
 "si-tailwindcss": ("Tailwind CSS", "https://tailwindcss.com/"),
 "si-trpc": ("tRPC", "https://trpc.io/"),
 "si-nextdotjs": ("Next.js", "https://nextjs.org/"),
 "si-jamstack": ("JAMstack", "https://jamstack.org/"),
 "si-php": ("PHP", "https://www.php.net/"),
 "si-laravel": ("Laravel", "https://laravel.com/"),
 "si-symfony": ("Symfony", "https://symfony.com/"),
 "si-linux": ("Linux", "https://www.kernel.org/"),
 "si-apache": ("Apache", "https://httpd.apache.org/"),
 "si-nginx": ("Nginx", "https://nginx.org/"),
 "si-windows": ("Windows", "https://www.microsoft.com/windows"),
 "si-freebsd": ("FreeBSD", "https://www.freebsd.org/"),
 "si-perl": ("Perl", "https://www.perl.org/"),
 "si-python": ("Python", "https://www.python.org/"),
 "si-django": ("Django", "https://www.djangoproject.com/"),
 "si-fastapi": ("FastAPI", "https://fastapi.tiangolo.com/"),
 "si-flask": ("Flask", "https://flask.palletsprojects.com/"),
 "si-pyramid": ("Pyramid", "https://trypyramid.com/"),
 "si-dotnet": (".NET", "https://dotnet.microsoft.com/"),
 "si-blazor": ("Blazor", "https://dotnet.microsoft.com/apps/aspnet/web-apps/blazor"),
 "si-openjdk": ("Java", "https://openjdk.org/"),
 "si-spring": ("Spring", "https://spring.io/projects/spring-boot"),
 "si-jakartaee": ("Jakarta EE", "https://jakarta.ee/"),
 "si-quarkus": ("Quarkus", "https://quarkus.io/"),
 "si-ruby": ("Ruby", "https://www.ruby-lang.org/"),
 "si-rubyonrails": ("Ruby on Rails", "https://rubyonrails.org/"),
 "si-sinatra": ("Sinatra", "https://sinatrarb.com/"),
 "si-go": ("Go", "https://go.dev/"),
 "si-gin": ("Gin", "https://gin-gonic.com/"),
 "si-echo": ("Echo", "https://echo.labstack.com/"),
 "si-fiber": ("Fiber", "https://gofiber.io/"),
 "si-rust": ("Rust", "https://www.rust-lang.org/"),
 "si-actix": ("Actix Web", "https://actix.rs/"),
 "si-axum": ("Axum", "https://github.com/tokio-rs/axum"),
 "si-rocket": ("Rocket", "https://rocket.rs/"),
 "si-iis": ("IIS", "https://www.iis.net/"),
 "si-elasticsearch": ("Elasticsearch", "https://www.elastic.co/elasticsearch"),
 "si-logstash": ("Logstash", "https://www.elastic.co/logstash"),
 "si-kibana": ("Kibana", "https://www.elastic.co/kibana"),
 "si-prometheus": ("Prometheus", "https://prometheus.io/"),
 "si-grafana": ("Grafana", "https://grafana.com/"),
 "si-telegraf": ("Telegraf", "https://www.influxdata.com/telegraf/"),
 "si-influxdb": ("InfluxDB", "https://www.influxdata.com/"),
 "si-chronograf": ("Chronograf", "https://www.influxdata.com/chronograf/"),
 "si-kapacitor": ("Kapacitor", "https://www.influxdata.com/kapacitor/"),
}
NEW_COMPS = {
 "wazuh-manager": ["Manager", "si-wazuh", "https://documentation.wazuh.com/current/user-manual/manager/index.html"],
 "wazuh-indexer": ["Indexer", "si-opensearch", "https://documentation.wazuh.com/current/user-manual/wazuh-indexer/index.html"],
 "wazuh-dashboard": ["Dashboard", "layout-dashboard", "https://documentation.wazuh.com/current/user-manual/wazuh-dashboard/index.html"],
}

def parse_icons(icon):
    if isinstance(icon, list):
        keys = []
        for it in icon:
            if isinstance(it, list):
                keys.append(it[0][3:] if it[0].startswith("si-") else it[0])
            elif isinstance(it, str):
                keys.append(it[3:] if it.startswith("si-") else it)
        return keys
    if isinstance(icon, str) and icon.startswith("si-"):
        return [icon[3:]]
    return None

text = (BASE / "server-single-tier-stack-en.md").read_text(encoding="utf-8")
old = json.loads(re.findall(r"```topology\n(.*?)\n```", text, re.S)[1])

nodes = {}
order = []
for nid, n in old["nodes"].items():
    label, sub, icon, kind = n[0], n[1], n[2], n[3]
    href = n[4] if len(n) > 4 else None
    keys = parse_icons(icon)
    if nid == "wazuh":
        keys = ["wazuh-manager", "wazuh-indexer", "wazuh-dashboard"]
    if nid == "lamp":
        href = "https://en.wikipedia.org/wiki/LAMP_(software_bundle)"
    if keys:
        nodes[nid] = [label, sub, keys, kind, href]
    else:
        nodes[nid] = [label, sub, icon, kind, href]
    order.append(nid)

used = []
for nid in order:
    v = nodes[nid]
    if isinstance(v[2], list):
        for k in v[2]:
            if k not in used:
                used.append(k)

comps = {}
for k in used:
    if k in NEW_COMPS:
        comps[k] = NEW_COMPS[k]
        continue
    sid = "si-" + k
    if sid in LABELS:
        label, href = LABELS[sid]
        comps[k] = [label, sid, href]
    else:
        raise SystemExit("no label for " + k)

def dump(block):
    L = ["{"]
    L.append('  "title": "Solution Stack",')
    L.append('  "dense": true,')
    L.append('  "components": {')
    L.append(",\n".join("    %s: [%s, %s, %s]" % (json.dumps(k), json.dumps(comps[k][0]), json.dumps(comps[k][1]), json.dumps(comps[k][2])) for k in sorted(comps)))
    L.append("  },")
    L.append('  "columns": [')
    L.append(",\n".join("    %s" % json.dumps(col) for col in block["columns"]))
    L.append("  ],")
    L.append('  "nodes": {')
    L.append(",\n".join("    %s: %s" % (json.dumps(k), json.dumps(nodes[k], ensure_ascii=False)) for k in order))
    L.append("  },")
    L.append('  "root": %s' % json.dumps(block["root"], ensure_ascii=False))
    L.append("}")
    return "\n".join(L)

body = dump(old)
# sanity: valid json
json.loads(body)
print(body[:3000])
print("...")
print("components:", len(comps), "nodes:", len(nodes), "lines:", body.count("\n") + 1)
Path("/home/moon/Projects/ai-tools/snapshots/notes/new_block.json").write_text(body, encoding="utf-8")
