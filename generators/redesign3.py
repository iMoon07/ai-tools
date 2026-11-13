import re, os, json

BASE = "/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture"

CFG = {
    "theme": "base",
    "flowchart": {"curve": "basis", "nodeSpacing": 45, "rankSpacing": 55, "padding": 12},
    "themeVariables": {
        "fontFamily": "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif",
        "fontSize": "14px",
        "background": "transparent",
        "primaryColor": "#eef2ff",
        "primaryTextColor": "#1e1b4b",
        "primaryBorderColor": "#6366f1",
        "lineColor": "#94a3b8",
        "textColor": "#1e293b",
        "mainBkg": "#eef2ff",
        "nodeBorder": "#6366f1",
        "clusterBkg": "transparent",
        "clusterBorder": "#cbd5e1",
        "edgeLabelBackground": "transparent",
    },
    "themeCSS": ".node rect, .node polygon, .node circle, .node ellipse { rx: 10px; ry: 10px; } .cluster rect { rx: 14px; ry: 14px; }",
}
INIT = "%%{init: " + json.dumps(CFG, ensure_ascii=False, separators=(", ", ": ")) + "}%%"

MDN_WEB = "https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics/What_is_a_web_server"
MDN_HOW = "https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Web_standards/How_the_web_works"
W_RUNTIME = "https://en.wikipedia.org/wiki/Runtime_system"
W_DB = "https://en.wikipedia.org/wiki/Database"
W_OS = "https://en.wikipedia.org/wiki/Operating_system"

L = {
    "id": {
        "u": "🌐 Browser / Pengguna", "ws": "🌐 Web Server<br/>menerima HTTP request",
        "rt": "⚙️ Runtime Aplikasi<br/>menjalankan logika aplikasi", "db": "🗄️ Database<br/>menyimpan & mengambil data",
        "e1": "1. HTTP Request", "e2": "2. Teruskan", "e3": "3. Query",
        "e4": "4. Data", "e5": "5. Hasil (HTML/JSON)", "e6": "6. HTTP Response",
        "one": "🧩 Satu Mesin (Single Tier)",
        "tipU": "Browser = web client", "tipWS": "Web Server = pintu HTTP",
        "tipRT": "Runtime = logika aplikasi", "tipDB": "Database = penyimpanan data",
        "os": "🐧 Sistem Operasi<br/>Linux · Windows", "ws2": "🌐 Web Server<br/>Apache · Nginx · IIS",
        "rt2": "⚙️ Runtime<br/>Node.js · PHP · Python · .NET · Java · Go · Rust",
        "db2": "🗄️ Database<br/>MySQL · PostgreSQL · MongoDB", "app": "📦 Aplikasi / API",
        "p1": "🧱 Bare Metal<br/>dikelola sendiri", "p2": "📦 Virtual Machine<br/>satu OS per VM",
        "p3": "📦 Container<br/>berbagi kernel host", "p4": "🏪 PaaS<br/>fokus ke kode",
        "p5": "⚡ Serverless<br/>jalan saat dipanggil", "p6": "🛵 Edge<br/>dekat pengguna",
        "tipP1": "Bare Metal", "tipP2": "Virtual Machine", "tipP3": "Container (OS-level virtualization)",
        "tipP4": "Platform as a Service", "tipP5": "Serverless computing", "tipP6": "Edge computing",
    },
    "en": {
        "u": "🌐 Browser / User", "ws": "🌐 Web Server<br/>receives HTTP request",
        "rt": "⚙️ Application Runtime<br/>runs application logic", "db": "🗄️ Database<br/>stores & retrieves data",
        "e1": "1. HTTP Request", "e2": "2. Forward", "e3": "3. Query",
        "e4": "4. Data", "e5": "5. Result (HTML/JSON)", "e6": "6. HTTP Response",
        "one": "🧩 One Machine (Single Tier)",
        "tipU": "Browser = web client", "tipWS": "Web Server = HTTP entry point",
        "tipRT": "Runtime = application logic", "tipDB": "Database = persistent storage",
        "os": "🐧 Operating System<br/>Linux · Windows", "ws2": "🌐 Web Server<br/>Apache · Nginx · IIS",
        "rt2": "⚙️ Runtime<br/>Node.js · PHP · Python · .NET · Java · Go · Rust",
        "db2": "🗄️ Database<br/>MySQL · PostgreSQL · MongoDB", "app": "📦 Application / API",
        "p1": "🧱 Bare Metal<br/>self-managed", "p2": "📦 Virtual Machine<br/>one OS per VM",
        "p3": "📦 Container<br/>shares host kernel", "p4": "🏪 PaaS<br/>focus on code",
        "p5": "⚡ Serverless<br/>runs when invoked", "p6": "🛵 Edge<br/>near the user",
        "tipP1": "Bare Metal", "tipP2": "Virtual Machine", "tipP3": "Container (OS-level virtualization)",
        "tipP4": "Platform as a Service", "tipP5": "Serverless computing", "tipP6": "Edge computing",
    },
    "ms": {
        "u": "🌐 Pelayar / Pengguna", "ws": "🌐 Pelayan Web<br/>menerima permintaan HTTP",
        "rt": "⚙️ Runtime Aplikasi<br/>menjalankan logik aplikasi", "db": "🗄️ Pangkalan Data<br/>menyimpan & mencapai data",
        "e1": "1. Permintaan HTTP", "e2": "2. Hantar", "e3": "3. Pertanyaan",
        "e4": "4. Data", "e5": "5. Hasil (HTML/JSON)", "e6": "6. Respons HTTP",
        "one": "🧩 Satu Mesin (Tahap Tunggal)",
        "tipU": "Pelayar = web client", "tipWS": "Pelayan Web = pintu HTTP",
        "tipRT": "Runtime = logik aplikasi", "tipDB": "Pangkalan Data = storan data",
        "os": "🐧 Sistem Pengendalian<br/>Linux · Windows", "ws2": "🌐 Pelayan Web<br/>Apache · Nginx · IIS",
        "rt2": "⚙️ Runtime<br/>Node.js · PHP · Python · .NET · Java · Go · Rust",
        "db2": "🗄️ Pangkalan Data<br/>MySQL · PostgreSQL · MongoDB", "app": "📦 Aplikasi / API",
        "p1": "🧱 Logam Kosong<br/>diurus sendiri", "p2": "📦 Mesin Maya<br/>satu OS setiap VM",
        "p3": "📦 Bekas<br/>kongsi kernel hos", "p4": "🏪 PaaS<br/>fokus pada kod",
        "p5": "⚡ Tanpa Pelayan<br/>berjalan apabila dipanggil", "p6": "🛵 Tepi<br/>hampir pengguna",
        "tipP1": "Logam Kosong", "tipP2": "Mesin Maya", "tipP3": "Bekas (virtualisasi tahap OS)",
        "tipP4": "Platform sebagai Perkhidmatan", "tipP5": "Pengkomputeran tanpa pelayan", "tipP6": "Pengkomputeran tepi",
    },
    "tl": {
        "u": "🌐 Browser / User", "ws": "🌐 Web Server<br/>tumanggap ng HTTP request",
        "rt": "⚙️ Application Runtime<br/>nagpapatakbo ng logic", "db": "🗄️ Database<br/>nag-iimbak at kumukuha ng data",
        "e1": "1. HTTP Request", "e2": "2. Ipinasa", "e3": "3. Query",
        "e4": "4. Data", "e5": "5. Resulta (HTML/JSON)", "e6": "6. HTTP Response",
        "one": "🧩 Isang Makina (Single Tier)",
        "tipU": "Browser = web client", "tipWS": "Web Server = pintuan ng HTTP",
        "tipRT": "Runtime = logic ng aplikasyon", "tipDB": "Database = imbakan ng data",
        "os": "🐧 Operating System<br/>Linux · Windows", "ws2": "🌐 Web Server<br/>Apache · Nginx · IIS",
        "rt2": "⚙️ Runtime<br/>Node.js · PHP · Python · .NET · Java · Go · Rust",
        "db2": "🗄️ Database<br/>MySQL · PostgreSQL · MongoDB", "app": "📦 Application / API",
        "p1": "🧱 Bare Metal<br/>sariling pamamahala", "p2": "📦 Virtual Machine<br/>isang OS bawat VM",
        "p3": "📦 Container<br/>share ng host kernel", "p4": "🏪 PaaS<br/>pokus sa code",
        "p5": "⚡ Serverless<br/>tumatakbo kapag tinawag", "p6": "🛵 Edge<br/>malapit sa user",
        "tipP1": "Bare Metal", "tipP2": "Virtual Machine", "tipP3": "Container (OS-level virtualization)",
        "tipP4": "Platform as a Service", "tipP5": "Serverless computing", "tipP6": "Edge computing",
    },
}

PLAT_URL = {
    "p1": "https://en.wikipedia.org/wiki/Bare-metal_server",
    "p2": "https://en.wikipedia.org/wiki/Virtual_machine",
    "p3": "https://en.wikipedia.org/wiki/Operating-system-level_virtualization",
    "p4": "https://en.wikipedia.org/wiki/Platform_as_a_service",
    "p5": "https://en.wikipedia.org/wiki/Serverless_computing",
    "p6": "https://en.wikipedia.org/wiki/Edge_computing",
}

STYLE = """    classDef actor fill:#dbeafe,stroke:#2563eb,color:#0f172a,stroke-width:1.5px
    classDef server fill:#ffedd5,stroke:#ea580c,color:#431407,stroke-width:1.5px
    classDef logic fill:#fef3c7,stroke:#d97706,color:#451a03,stroke-width:1.5px
    classDef store fill:#d1fae5,stroke:#059669,color:#064e3b,stroke-width:1.5px"""


def block1(d):
    return f"""{INIT}
flowchart LR
    U(["{d['u']}"])
    WS[["{d['ws']}"]]
    RT["{d['rt']}"]
    DB[("{d['db']}")]

    U -->|"{d['e1']}"| WS
    WS -->|"{d['e2']}"| RT
    RT -->|"{d['e3']}"| DB
    DB -->|"{d['e4']}"| RT
    RT -->|"{d['e5']}"| WS
    WS -->|"{d['e6']}"| U

    subgraph ONE["{d['one']}"]
        WS
        RT
        DB
    end

    click U "{MDN_HOW}" "{d['tipU']}"
    click WS "{MDN_WEB}" "{d['tipWS']}"
    click RT "{W_RUNTIME}" "{d['tipRT']}"
    click DB "{W_DB}" "{d['tipDB']}"

{STYLE}

    class U actor
    class WS server
    class RT logic
    class DB store
    style ONE fill:transparent,stroke:#cbd5e1,stroke-width:1px,color:#64748b"""


def block2(d):
    return f"""{INIT}
flowchart TB
    OS["{d['os']}"]
    WS["{d['ws2']}"]
    RT["{d['rt2']}"]
    DB[("{d['db2']}")]
    APP{{"{d['app']}"}}

    OS --> WS
    WS --> RT
    RT --> DB
    RT --> APP

    click OS "{W_OS}" "Operating System"
    click WS "{MDN_WEB}" "Web Server"
    click RT "{W_RUNTIME}" "Runtime"
    click DB "{W_DB}" "Database"
    click APP "{MDN_HOW}" "Application / API"

    classDef os fill:#e0e7ff,stroke:#4f46e5,color:#1e1b4b,stroke-width:1.5px
    classDef server fill:#ffedd5,stroke:#ea580c,color:#431407,stroke-width:1.5px
    classDef logic fill:#fef3c7,stroke:#d97706,color:#451a03,stroke-width:1.5px
    classDef store fill:#d1fae5,stroke:#059669,color:#064e3b,stroke-width:1.5px
    classDef app fill:#e0f2fe,stroke:#0284c7,color:#082f49,stroke-width:1.5px

    class OS os
    class WS server
    class RT logic
    class DB store
    class APP app"""


def block3(d):
    return f"""{INIT}
flowchart LR
    A(["{d['p1']}"])
    B["{d['p2']}"]
    C["{d['p3']}"]
    D["{d['p4']}"]
    E["{d['p5']}"]
    F(["{d['p6']}"])

    A --> B --> C --> D --> E --> F

    click A "{PLAT_URL['p1']}" "{d['tipP1']}"
    click B "{PLAT_URL['p2']}" "{d['tipP2']}"
    click C "{PLAT_URL['p3']}" "{d['tipP3']}"
    click D "{PLAT_URL['p4']}" "{d['tipP4']}"
    click E "{PLAT_URL['p5']}" "{d['tipP5']}"
    click F "{PLAT_URL['p6']}" "{d['tipP6']}"

    classDef self fill:#ffedd5,stroke:#ea580c,color:#431407,stroke-width:1.5px
    classDef mid fill:#fef3c7,stroke:#d97706,color:#451a03,stroke-width:1.5px
    classDef managed fill:#e0f2fe,stroke:#0284c7,color:#082f49,stroke-width:1.5px

    class A,B self
    class C mid
    class D,E,F managed"""


for lang, d in L.items():
    path = os.path.join(BASE, "server-single-tier-stack-%s.md" % lang)
    text = open(path, encoding="utf-8", newline="").read()
    blocks = list(re.finditer(r"^```mermaid[ \t]*\n.*?^```", text, re.S | re.M))
    if len(blocks) != 3:
        print("!! %s: %d blok mermaid" % (lang, len(blocks)))
        continue
    new = [block1(d), block2(d), block3(d)]
    out, last = [], 0
    for m, nb in zip(blocks, new):
        out.append(text[last:m.start()])
        out.append("```mermaid\n" + nb + "\n```")
        last = m.end()
    out.append(text[last:])
    open(path, "w", encoding="utf-8", newline="").write("".join(out))
    print("%s: 3 diagram baru (transparan, bentuk baru, referensi dasar)" % lang)