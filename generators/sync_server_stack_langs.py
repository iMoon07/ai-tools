#!/usr/bin/env python3
"""Keep the "Core and Supporting Components" topology in sync across languages.

Sama seperti sync_topology_templates.py, tetapi untuk artikel
server-single-tier-stack. Empat file bahasa memegang JSON yang sama; menyunting
keempatnya dengan tangan adalah cara tercepat membuat satu bahasa tertinggal.
Skrip ini memiliki spec kanonik + prosa per bahasa, lalu hanya menyisipkan atau
mengganti blok berpenanda, sehingga prosa terjemahan lain tidak tersentuh.

Usage:
    python3 ai-tools/generators/sync_server_stack_langs.py [--check]

Blok berada di antara penanda HTML (tidak terlihat saat render), jadi
penyisipan ulang bersifat idempoten. Blok disisipkan tepat sebelum heading
`##` berikutnya setelah bagian Komponen Pelengkap.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

BASE = Path("/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture")
LANGS = ("en", "id", "ms", "tl")

BEGIN = "<!-- topology:core-components -->"
END = "<!-- /topology:core-components -->"

# Bagian "Supporting Components" tiap bahasa: anchor untuk mencari titik sisip.
ANCHOR = {
    "en": r"^## Supporting Components\s*$",
    "id": r"^## Komponen Pelengkap\s*$",
    "ms": r"^## Komponen Pelengkap\s*$",
    "tl": r"^## Mga Komponenteng Pantulong\s*$",
}

SPEC = {
    "en": {
        "title": "Core and Supporting Components",
        "legend": {"flow": "Request", "back": "Response"},
        "nodes": {
            "W": ["Web Client", "The customer", "customer", "client"],
            "T": ["TLS & Certificate", "Sealed packaging & license", "lock", "security"],
            "S": ["Web Server", "The waiter", "waiter", "server"],
            "A": ["Application Runtime", "The chef", "cook", "process"],
            "H": ["Cache", "Ready-to-serve items", "package", "store"],
            "D": ["Database", "The pantry", "warehouse", "database"],
        },
        "facilities": ["On one machine", ["server", "Core"],
                       ["security", "Transport"], ["package", "Optional"]],
        "prose": (
            "The OS is not drawn as a box of its own: it is the floor everything "
            "above stands on. Every component in the diagram runs on the same "
            "operating system, so the OS is the building, while the web server, "
            "runtime, and database are the rooms inside it."
        ),
    },
    "id": {
        "title": "Komponen Inti dan Pelengkap",
        "legend": {"flow": "Permintaan", "back": "Respons"},
        "nodes": {
            "W": ["Klien Web", "Sang pelanggan", "customer", "client"],
            "T": ["TLS & Sertifikat", "Kemasan tersegel & izin usaha", "lock", "security"],
            "S": ["Server Web", "Sang pelayan", "waiter", "server"],
            "A": ["Runtime Aplikasi", "Sang koki", "cook", "process"],
            "H": ["Cache", "Hidangan siap saji", "package", "store"],
            "D": ["Basis Data", "Gudang bahan", "warehouse", "database"],
        },
        "facilities": ["Dalam satu mesin", ["server", "Inti"],
                       ["security", "Transportasi"], ["package", "Opsional"]],
        "prose": (
            "OS tidak digambar sebagai kotak tersendiri: ia adalah lantai tempat "
            "semua yang di atasnya berdiri. Semua komponen pada diagram berjalan "
            "di atas sistem operasi yang sama, jadi OS adalah bangunannya, "
            "sedangkan server web, runtime, dan basis data adalah ruang-ruang di "
            "dalamnya."
        ),
    },
    "ms": {
        "title": "Komponen Teras dan Pelengkap",
        "legend": {"flow": "Permintaan", "back": "Respons"},
        "nodes": {
            "W": ["Klien Web", "Pelanggan", "customer", "client"],
            "T": ["TLS & Sijil", "Bungkusan dimeterai & lesen", "lock", "security"],
            "S": ["Pelayan Web", "Pelayan kedai", "waiter", "server"],
            "A": ["Runtime Aplikasi", "Tukang masak", "cook", "process"],
            "H": ["Cache", "Juadah siap hidang", "package", "store"],
            "D": ["Pangkalan Data", "Ruang simpanan", "warehouse", "database"],
        },
        "facilities": ["Dalam satu mesin", ["server", "Teras"],
                       ["security", "Pengangkutan"], ["package", "Pilihan"]],
        "prose": (
            "OS tidak dilukis sebagai kotak berasingan: ia ialah lantai yang "
            "menjadi tempat semua di atasnya berdiri. Setiap komponen dalam rajah "
            "berjalan pada sistem pengendalian yang sama, maka OS ialah "
            "bangunannya, manakala pelayan web, runtime, dan pangkalan data ialah "
            "bilik-bilik di dalamnya."
        ),
    },
    "tl": {
        "title": "Pangunahing Bahagi at mga Pantulong",
        "legend": {"flow": "Request", "back": "Response"},
        "nodes": {
            "W": ["Web Client", "Ang customer", "customer", "client"],
            "T": ["TLS at Certificate", "Selyadong pakete at lisensya", "lock", "security"],
            "S": ["Web Server", "Ang waiter", "waiter", "server"],
            "A": ["Application Runtime", "Ang chef", "cook", "process"],
            "H": ["Cache", "Mga pagkaing nakahanda", "package", "store"],
            "D": ["Database", "Ang pantry", "warehouse", "database"],
        },
        "facilities": ["Isang machine", ["server", "Pangunahing"],
                       ["security", "Transport"], ["package", "Opsyonal"]],
        "prose": (
            "Hindi iginuhit ang OS bilang sariling kahon: ito ang sahig na "
            "kinatatayuan ng lahat ng nasa itaas. Lahat ng komponente sa diyagram "
            "ay tumatakbo sa iisang operating system, kaya ang OS ang gusali, at "
            "ang web server, runtime, at database ang mga kuwarto sa loob nito."
        ),
    },
}

HREF = {
    "W": "https://en.wikipedia.org/wiki/Web_browser",
    "T": "https://en.wikipedia.org/wiki/Transport_Layer_Security",
    "S": "https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics/What_is_a_web_server",
    "A": "https://en.wikipedia.org/wiki/Runtime_system",
    "H": "https://en.wikipedia.org/wiki/Cache_(computing)",
    "D": "https://en.wikipedia.org/wiki/Database",
}


def build(lang: str) -> dict:
    s = SPEC[lang]
    nodes = {}
    for key, (label, sub, icon, kind) in s["nodes"].items():
        nodes[key] = [label, sub, icon, kind, HREF[key]]
    return {
        "vertical": True,
        "title": s["title"],
        "legend": s["legend"],
        # Cache dan Database harus sejajar: .topo-col itu flex-direction column,
        # jadi ["H","D"] akan menumpuk dan kabel A->D menembus Cache.
        # Cache and Database must sit side by side: .topo-col is a flex column,
        # so ["H","D"] stacks and the A->D cable would cut through Cache.
        "columns": [["W"], ["T"], ["S"], ["A"], {"nodes": ["H", "D"], "grid": 2}],
        "nodes": nodes,
        "edges": [
            ["W", "T"],
            ["T", "S"],
            ["S", "A"],
            ["A", "H"],
            ["A", "D"],
            ["D", "A", "", True],
            ["A", "S", "", True],
            ["S", "T", "", True],
            ["T", "W", "", True],
        ],
        "badges": False,
        "facilities": s["facilities"],
    }


def block(lang: str) -> str:
    spec = json.dumps(build(lang), ensure_ascii=False, indent=2)
    return f"{BEGIN}\n\n```topology\n{spec}\n```\n\n{SPEC[lang]['prose']}\n\n{END}\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report drift, do not write")
    args = ap.parse_args()

    drift = []
    for lang in LANGS:
        path = BASE / f"server-single-tier-stack-{lang}.md"
        if not path.exists():
            print("missing", path)
            continue
        text = path.read_text(encoding="utf-8")
        new_text = block(lang)

        if BEGIN in text:
            if END not in text:
                raise SystemExit(f"{path.name}: {BEGIN} tanpa {END}")
            pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", re.S)
            out, n = pattern.subn(lambda _m: new_text, text, count=1)
            if n != 1:
                raise SystemExit(f"{path.name}: blok berpenanda tidak lengkap")
            how = "replaced"
        else:
            anchor = re.compile(ANCHOR[lang], re.M)
            m = anchor.search(text)
            if not m:
                raise SystemExit(f"{path.name}: heading anchor tidak ditemukan")
            nxt = re.compile(r"^## ", re.M).search(text, m.end())
            if not nxt:
                raise SystemExit(f"{path.name}: tidak ada heading ## setelah anchor")
            out = text[:nxt.start()] + new_text + text[nxt.start():]
            how = "inserted"

        for fence in re.finditer(r"```topology\n(.*?)\n```", out, re.S):
            json.loads(fence.group(1))

        if out != text:
            drift.append(path.name)
            if not args.check:
                path.write_text(out, encoding="utf-8")
        print(f"{lang}: {how}" + ("" if out != text else " (unchanged)"))

    if args.check and drift:
        print("drift:", ", ".join(drift))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())