import re, os

BASE = "/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture"

INIT = (
    '%%{init: {"theme": "base", "flowchart": {"curve": "basis", "nodeSpacing": 45, '
    '"rankSpacing": 55, "padding": 12}, "themeVariables": {"fontFamily": "Inter, ui-sans-serif, '
    'system-ui, -apple-system, Segoe UI, sans-serif", "fontSize": "14px", "background": "#f8fafc", '
    '"primaryColor": "#eef2ff", "primaryTextColor": "#1e1b4b", "primaryBorderColor": "#6366f1", '
    '"lineColor": "#94a3b8", "textColor": "#1e293b", "mainBkg": "#eef2ff", "nodeBorder": "#6366f1", '
    '"clusterBkg": "#f1f5f9", "clusterBorder": "#cbd5e1", "edgeLabelBackground": "#f8fafc"}, '
    '"themeCSS": ".node rect, .node polygon, .node circle, .node ellipse { rx: 10px; ry: 10px; } '
    '.edgePath path { stroke-width: 1.6px; } .cluster rect { rx: 14px; ry: 14px; }"}}%%'
)

CLICK_DOC = {
    "C": "https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Web_standards/How_the_web_works",
    "P": "https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics/What_is_a_web_server",
    "K": "https://en.wikipedia.org/wiki/Runtime_system",
    "G": "https://en.wikipedia.org/wiki/Database",
}

TECH = {
    "C": ("🟨 JavaScript / TypeScript", "React · Node.js · MongoDB", "https://nodejs.org/"),
    "D": ("🐘 PHP", "Laravel · LAMP · LEMP", "https://www.php.net/"),
    "E": ("🐍 Python", "Django · FastAPI · Flask", "https://www.python.org/"),
    "F": ("🔷 .NET", "ASP.NET Core · Blazor", "https://dotnet.microsoft.com/"),
    "G": ("☕ Java", "Spring Boot · Jakarta EE", "https://dev.java/"),
    "H": ("💎 Ruby", "Ruby on Rails", "https://www.ruby-lang.org/"),
    "I": ("🐹 Go", "Gin · Echo · Fiber", "https://go.dev/"),
    "J": ("🦀 Rust", "Actix · Axum · Rocket", "https://www.rust-lang.org/"),
}

PLAT_URL = {
    "C": "https://www.ovhcloud.com/en/bare-metal/",
    "D": "https://www.virtualbox.org/",
    "E": "https://www.docker.com/",
    "F": "https://www.heroku.com/",
    "G": "https://aws.amazon.com/lambda/",
    "H": "https://workers.cloudflare.com/",
}

L = {
    "id": {
        "cust": "🧑‍🦱 Pelanggan<br/>Datang & memesan", "wait": "🧑‍🍳 Pelayan<br/>Terima pesanan",
        "cook": "👨‍🍳 Koki<br/>Masak pesanan", "pantry": "🥫 Gudang Bahan<br/>Simpan bahan",
        "e1": "1. HTTP Request", "e2": "2. Teruskan", "e3": "3. Ambil bahan",
        "e4": "4. Kirim bahan", "e5": "5. Sajikan", "e6": "6. HTTP Response",
        "sub": "🏠 Warung / Satu Lokasi",
        "tipC": "Pelanggan = web client", "tipP": "Pelayan = web server",
        "tipK": "Koki = runtime aplikasi", "tipG": "Gudang = database",
        "sA": "🍜 Technology Stack<br/>= Resep + bahan", "sB": "🧺 Pilih bahan<br/>sesuai menu",
        "sL": "🍽️ Aplikasi web / API<br/>sesuai kebutuhan proyek", "infra": "📊 Infrastruktur",
        "pA": "🍜 Stack siap<br/>resep + bahan + peralatan", "pB": "📍 Jalankan di mana?",
        "pC": "🏠 Bare Metal<br/>Bangun warung sendiri", "pD": "🛏️ Virtual Machine<br/>Sewa kamar kost",
        "pE": "🍱 Container<br/>Sewa gerai food court", "pF": "🏪 PaaS<br/>Ikut franchise siap pakai",
        "pG": "🛒 Serverless<br/>Buka gerai saat ada pesanan", "pH": "🛵 Edge Computing<br/>Gerobak dekat pelanggan",
        "pI": "🧩 Semua komponen stack<br/>berjalan di satu tempat",
    },
    "en": {
        "cust": "🧑‍🦱 Customer<br/>Places an order", "wait": "🧑‍🍳 Waiter<br/>Takes the order",
        "cook": "👨‍🍳 Chef<br/>Prepares the meal", "pantry": "🥫 Pantry<br/>Stores ingredients",
        "e1": "1. HTTP Request", "e2": "2. Forward", "e3": "3. Fetch ingredients",
        "e4": "4. Send ingredients", "e5": "5. Serve", "e6": "6. HTTP Response",
        "sub": "🏠 Eatery / Single Location",
        "tipC": "Customer = web client", "tipP": "Waiter = web server",
        "tipK": "Chef = application runtime", "tipG": "Pantry = database",
        "sA": "🍜 Technology Stack<br/>= Recipe + ingredients", "sB": "🧺 Choose ingredients<br/>based on the menu",
        "sL": "🍽️ Web application / API<br/>tailored to project needs", "infra": "📊 Infrastructure",
        "pA": "🍜 Stack is ready<br/>recipe + ingredients + tools", "pB": "📍 Where to run it?",
        "pC": "🏠 Bare Metal<br/>Build your own eatery", "pD": "🛏️ Virtual Machine<br/>Rent a private room",
        "pE": "🍱 Container<br/>Rent a food-court stall", "pF": "🏪 PaaS<br/>Join a ready-made franchise",
        "pG": "🛒 Serverless<br/>Open a stall only when orders come", "pH": "🛵 Edge Computing<br/>Food cart near customers",
        "pI": "🧩 All stack components<br/>run in one place",
    },
    "ms": {
        "cust": "🧑‍🦱 Pelanggan<br/>Membuat pesanan", "wait": "🧑‍🍳 Pelayan<br/>Menerima pesanan",
        "cook": "👨‍🍳 Tukang Masak<br/>Menyediakan pesanan", "pantry": "🥫 Pantri<br/>Menyimpan bahan",
        "e1": "1. Permintaan HTTP", "e2": "2. Hantar", "e3": "3. Ambil bahan",
        "e4": "4. Hantar bahan", "e5": "5. Hidang", "e6": "6. Respons HTTP",
        "sub": "🏠 Gerai Makan / Satu Lokasi",
        "tipC": "Pelanggan = web client", "tipP": "Pelayan = pelayan web",
        "tipK": "Tukang masak = runtime aplikasi", "tipG": "Pantri = pangkalan data",
        "sA": "🍜 Tindanan Teknologi<br/>= Resipi + bahan", "sB": "🧺 Pilih bahan<br/>mengikut menu",
        "sL": "🍽️ Aplikasi Web / API<br/>mengikut keperluan projek", "infra": "📊 Infrastruktur",
        "pA": "🍜 Tindanan sedia<br/>resipi + bahan + alatan", "pB": "📍 Di mana untuk dijalankan?",
        "pC": "🏠 Logam Kosong<br/>Bina gerai sendiri", "pD": "🛏️ Mesin Maya<br/>Sewa bilik persendirian",
        "pE": "🍱 Bekas<br/>Sewa gerai di medan selera", "pF": "🏪 PaaS<br/>Sertai francais sedia guna",
        "pG": "🛒 Tanpa Pelayan<br/>Buka gerai bila ada pesanan", "pH": "🛵 Pengkomputeran Tepi<br/>Gerai berhampiran pelanggan",
        "pI": "🧩 Semua komponen tindanan<br/>berjalan di satu tempat",
    },
    "tl": {
        "cust": "🧑‍🦱 Customer<br/>Nag-order ng pagkain", "wait": "🧑‍🍳 Waiter<br/>Tumatanggap ng order",
        "cook": "👨‍🍳 Kusinero<br/>Naghahanda ng pagkain", "pantry": "🥫 Bodega<br/>Nagtatago ng sangkap",
        "e1": "1. HTTP Request", "e2": "2. Ipinasa", "e3": "3. Kunin sangkap",
        "e4": "4. Ipadala sangkap", "e5": "5. Ihain", "e6": "6. HTTP Response",
        "sub": "🏠 Karinderya / Isang Lugar",
        "tipC": "Customer = web client", "tipP": "Waiter = web server",
        "tipK": "Kusinero = application runtime", "tipG": "Bodega = database",
        "sA": "🍜 Technology Stack<br/>= Resipe + mga sangkap", "sB": "🧺 Pumili ng sangkap<br/>batay sa menu",
        "sL": "🍽️ Web Application / API<br/>ayon sa pangangailangan ng proyekto", "infra": "📊 Infrastructure",
        "pA": "🍜 Handa na ang stack<br/>resipe + sangkap + kagamitan", "pB": "📍 Saan ito patatakbuhin?",
        "pC": "🏠 Bare Metal<br/>Bumuo ng sariling karinderya", "pD": "🛏️ Virtual Machine<br/>Umupa ng pribadong kwarto",
        "pE": "🍱 Container<br/>Umupa ng stall sa food court", "pF": "🏪 PaaS<br/>Sumali sa ready-to-use franchise",
        "pG": "🛒 Serverless<br/>Buksan ang stall kapag may order", "pH": "🛵 Edge Computing<br/>Food cart malapit sa customer",
        "pI": "🧩 Lahat ng bahagi ng stack<br/>tumatakbo sa iisang lugar",
    },
}

STYLE = """    classDef actor fill:#dbeafe,stroke:#2563eb,color:#0f172a,stroke-width:1.5px
    classDef role fill:#ffedd5,stroke:#ea580c,color:#431407,stroke-width:1.5px
    classDef store fill:#d1fae5,stroke:#059669,color:#064e3b,stroke-width:1.5px
    style W fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px,color:#64748b"""

STYLE_TECH = """    classDef entry fill:#dcfce7,stroke:#16a34a,color:#052e16,stroke-width:1.5px
    classDef pick fill:#fef3c7,stroke:#d97706,color:#451a03,stroke-width:1.5px
    classDef tech fill:#eef2ff,stroke:#6366f1,color:#1e1b4b,stroke-width:1.5px
    classDef out fill:#e0f2fe,stroke:#0284c7,color:#082f49,stroke-width:1.5px"""

STYLE_PLAT = """    classDef entry fill:#dcfce7,stroke:#16a34a,color:#052e16,stroke-width:1.5px
    classDef pick fill:#fef3c7,stroke:#d97706,color:#451a03,stroke-width:1.5px
    classDef plat fill:#eef2ff,stroke:#6366f1,color:#1e1b4b,stroke-width:1.5px
    classDef out fill:#e0f2fe,stroke:#0284c7,color:#082f49,stroke-width:1.5px"""


def block0(d):
    return f"""{INIT}
flowchart LR
    C(["{d['cust']}"])
    P["{d['wait']}"]
    K["{d['cook']}"]
    G[("{d['pantry']}")]

    C -->|"{d['e1']}"| P
    P -->|"{d['e2']}"| K
    K -->|"{d['e3']}"| G
    G -->|"{d['e4']}"| K
    K -->|"{d['e5']}"| P
    P -->|"{d['e6']}"| C

    subgraph W["{d['sub']}"]
        P
        K
        G
    end

    click C "{CLICK_DOC['C']}" "{d['tipC']}"
    click P "{CLICK_DOC['P']}" "{d['tipP']}"
    click K "{CLICK_DOC['K']}" "{d['tipK']}"
    click G "{CLICK_DOC['G']}" "{d['tipG']}"

{STYLE}

    class C actor
    class P,K role
    class G store"""


def block1(d):
    lines = [INIT, "flowchart LR", f'    A(["{d["sA"]}"])', f'    B{{"{d["sB"]}"}}', "", "    A --> B", ""]
    for key in ["C", "D", "E", "F", "G", "H", "I", "J"]:
        t, sub, url = TECH[key]
        lines.append(f'    B --> {key}["{t}<br/>{sub}"]')
    lines.append(f'    B --> K["{d["infra"]}<br/>ELK · Prometheus + Grafana"]')
    lines.append("")
    for key in ["C", "D", "E", "F", "G", "H", "I", "J", "K"]:
        lines.append(f"    {key} --> L")
    lines.append(f'    L(["{d["sL"]}"])')
    lines.append("")
    for key in ["C", "D", "E", "F", "G", "H", "I", "J"]:
        lines.append(f'    click {key} "{TECH[key][2]}" "{TECH[key][0]}"')
    lines.append('    click K "https://prometheus.io/" "' + d["infra"] + '"')
    lines.append("")
    lines.append(STYLE_TECH)
    lines.append("")
    lines.append("    class A entry")
    lines.append("    class B pick")
    lines.append("    class C,D,E,F,G,H,I,J,K tech")
    lines.append("    class L out")
    return "\n".join(lines)


def block2(d):
    labels = {"C": d["pC"], "D": d["pD"], "E": d["pE"], "F": d["pF"], "G": d["pG"], "H": d["pH"]}
    lines = [INIT, "flowchart LR", f'    A(["{d["pA"]}"])', f'    B{{"{d["pB"]}"}}', "", "    A --> B", ""]
    for k, lab in labels.items():
        lines.append(f'    B --> {k}["{lab}"]')
    lines.append("")
    lines.append(f'    C --> I(["{d["pI"]}"])')
    for k in ["D", "E", "F", "G", "H"]:
        lines.append(f"    {k} --> I")
    lines.append("")
    for k, url in PLAT_URL.items():
        tip = labels[k].replace("<br/>", " — ")
        lines.append(f'    click {k} "{url}" "{tip}"')
    lines.append("")
    lines.append(STYLE_PLAT)
    lines.append("")
    lines.append("    class A entry")
    lines.append("    class B pick")
    lines.append("    class C,D,E,F,G,H plat")
    lines.append("    class I out")
    return "\n".join(lines)


for lang, d in L.items():
    path = os.path.join(BASE, "server-single-tier-stack-%s.md" % lang)
    text = open(path, encoding="utf-8", newline="").read()
    blocks = list(re.finditer(r"^```mermaid[ \t]*\n.*?^```", text, re.S | re.M))
    if len(blocks) != 3:
        print("!! %s: %d blok mermaid" % (lang, len(blocks)))
        continue
    new = [block0(d), block1(d), block2(d)]
    out, last = [], 0
    for m, nb in zip(blocks, new):
        out.append(text[last:m.start()])
        out.append("```mermaid\n" + nb + "\n```")
        last = m.end()
    out.append(text[last:])
    open(path, "w", encoding="utf-8", newline="").write("".join(out))
    print("%s: tema + warna + style diterapkan" % lang)