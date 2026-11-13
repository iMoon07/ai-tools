#!/usr/bin/env python3
"""Keep the topology sections of the four template languages in sync.

The article templates carry a lot of duplicated JSON. Editing four files by
hand is how the 18.8 catalogue and the hospital diagram drifted apart. This
script owns the canonical specs and rewrites only the topology fences, so the
prose and the rest of each language file stay untouched.

Usage:
    python3 tools/sync_topology_templates.py [--check]

The 18.8 section is replaced as a whole because its old catalogue was the
source of the "too long / too many requests" problem. 19.1 and 19.2 keep their
translated prose and only swap the JSON fence.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BASE = Path('/home/moon/Projects/Penjelajah-CyberSecurity/blog-post-template')
LANGS = ('en', 'id', 'ms', 'tl')

SECURITY_188 = {
    'title': 'Security toolchain',
    'uniform': True,
    'columns': [['recon'], ['exploit'], ['post'], ['forensics']],
    'nodes': {
        'recon': ['Recon', 'Nmap · Wireshark', ['security:nmap', 'security:wireshark'], 'tech'],
        'exploit': ['Exploit', 'Metasploit · Burp', ['security:metasploit', 'security:burp'], 'tech'],
        'post': ['Post-exploit', 'Mimikatz · Hashcat', ['security:mimikatz', 'security:hashcat'], 'tech'],
        'forensics': ['Forensics', 'Ghidra · Autopsy', ['security:ghidra', 'security:autopsy'], 'tech'],
    },
    'edges': [
        ['recon', 'exploit', '1'],
        ['exploit', 'post', '2'],
        ['post', 'forensics', '3'],
    ],
    'legend': {'flow': 'Attack phase'},
    'facilities': ['Security', ['shield', 'Hacking toolkit'], ['terminal', 'CLI first']],
}

RESTAURANT_191 = {
    'title': 'The Flow',
    'uniform': True,
    'columns': [['C'], ['P'], ['K'], ['G']],
    'nodes': {
        'C': ['Customer', 'Places an order', 'stack:github', 'actor'],
        'P': ['Waiter', 'Takes the order', 'stack:nginx', 'process'],
        'K': ['Chef', 'Prepares the order', 'programming:nodejs', 'process'],
        'G': ['Pantry', 'Stores ingredients', 'stack:postgresql', 'store'],
    },
    'edges': [
        ['C', 'P', '1'],
        ['P', 'K', '2'],
        ['K', 'G', '3'],
        ['G', 'K', '4', True],
    ],
    'legend': {'flow': 'Order / request', 'back': 'Return / response'},
    'facilities': ['In this place', ['store', 'Eatery'], ['wifi', 'Wi-Fi']],
}

HOSPITAL_192 = {
    'title': 'Hospital platform',
    'uniform': True,
    'root': ['Hospital', 'integrated platform', 'building-2', 'out'],
    'rootWires': False,
    'columns': [['edge'], ['runtime'], ['data'], ['soc']],
    'nodes': {
        'edge': ['Edge & WAF', 'Cloudflare · Nginx · TLS',
                 ['security:wafw00f', 'stack:cloudflare', 'stack:nginx'], 'network'],
        'runtime': ['Runtime stacks', 'LAMP · LEMP · WAMP · WIMP · FAMP · FIMP',
                    ['stack:linux', 'stack:apache', 'stack:mysql', 'programming:php'], 'tech'],
        'data': ['Patient data', 'MariaDB · MySQL · Redis · Postgres',
                 ['stack:mariadb', 'stack:mysql', 'stack:redis', 'stack:postgresql'], 'database'],
        'soc': ['SOC / ELK', 'Wazuh · Elasticsearch · Logstash · Kibana',
                ['security:wazuh', 'stack:elasticsearch', 'stack:logstash', 'stack:kibana'], 'process'],
    },
    'edges': [
        ['__root__', 'edge'],
        ['edge', 'runtime'],
        ['runtime', 'data'],
        ['data', 'soc'],
        ['data', 'runtime', '', True],
    ],
    'legend': {'flow': 'Request', 'back': 'Response'},
    'facilities': ['Hospital', ['building-2', 'Hospital'], ['shield', 'SOC'], ['cloud', 'Cloud']],
}

TEXT_188 = {
    'en': (
        '### 18.8 Logo library — security tools',
        'All 575 logos from `iMoon07/logo-svg` are available to every node '
        '(`"logo": "security:nmap"`). This compact chain shows four representative '
        'phases; every tool is a node, and its logo is the catalogue entry.',
        'How to read: Recon → Exploit → Post-exploit → Forensics. Each arrow is the '
        'next phase; the footer repeats the security context.',
    ),
    'id': (
        '### 18.8 Pustaka logo — tools keamanan',
        'Semua 575 logo dari `iMoon07/logo-svg` tersedia untuk setiap node '
        '(`"logo": "security:nmap"`). Diagram ringkas ini menampilkan empat fase '
        'perwakilan; setiap tool adalah node, dan logonya adalah entri katalog.',
        'Cara membaca: Recon → Exploit → Post-exploit → Forensik. Setiap panah adalah '
        'fase berikutnya; footer mengulang konteks keamanan.',
    ),
    'ms': (
        '### 18.8 Pustaka logo — alat keselamatan',
        'Semua 575 logo daripada `iMoon07/logo-svg` tersedia untuk setiap nod '
        '(`"logo": "security:nmap"`). Rajah ringkas ini menunjukkan empat fasa '
        'perwakilan; setiap alat ialah nod, dan logonya ialah entri katalog.',
        'Cara membaca: Recon → Exploit → Post-exploit → Forensik. Setiap anak panah '
        'ialah fasa seterusnya; footer mengulang konteks keselamatan.',
    ),
    'tl': (
        '### 18.8 Logo library — mga tool sa seguridad',
        'Lahat ng 575 logo mula sa `iMoon07/logo-svg` ay available sa bawat node '
        '(`"logo": "security:nmap"`). Ang compact chain na ito ay nagpapakita ng '
        'apat na representative phase; bawat tool ay isang node, at ang logo nito '
        'ay ang catalogue entry.',
        'Paano basahin: Recon → Exploit → Post-exploit → Forensics. Bawat arrow ay '
        'ang susunod na phase; inuulit ng footer ang security context.',
    ),
}


def fence(spec: dict) -> str:
    return '```topology\n' + json.dumps(spec, ensure_ascii=False, indent=2) + '\n```'


def section_188(lang: str) -> str:
    head, prose, read = TEXT_188[lang]
    return f'{head}\n\n{prose}\n\n{fence(SECURITY_188)}\n\n{read}\n\n'


def replace_section(text: str, pattern: str, new: str, label: str) -> str:
    out, n = re.subn(pattern, lambda _m: new, text, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f'{label}: expected one match, got {n}')
    return out


def replace_first_topology(text: str, heading_pattern: str, spec: dict, label: str) -> str:
    pattern = r'(' + heading_pattern + r'.*?)```topology\n.*?\n```'
    out, n = re.subn(pattern, lambda m: m.group(1) + fence(spec),
                     text, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f'{label}: expected one topology fence, got {n}')
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='report drift, do not write')
    args = ap.parse_args()
    drift = []
    for lang in LANGS:
        path = BASE / f'template-for-you-{lang}.md'
        if not path.exists():
            print('missing', path)
            continue
        old = path.read_text(encoding='utf-8')
        new = replace_section(old, r'### 18\.8[^\n]*\n.*?(?=## 19 —)', section_188(lang), '18.8')
        new = replace_first_topology(new, r'### 19\.1[^\n]*\n', RESTAURANT_191, '19.1')
        new = replace_first_topology(new, r'### 19\.2[^\n]*\n', HOSPITAL_192, '19.2')
        # Fail before writing if any topology fence is not valid JSON.
        for m in re.finditer(r'```topology\n(.*?)\n```', new, re.S):
            json.loads(m.group(1))
        if new != old:
            drift.append(path.name)
            if not args.check:
                path.write_text(new, encoding='utf-8')
                print('rewrote', path.name)
        else:
            print('unchanged', path.name)
    if args.check and drift:
        print('drift:', ', '.join(drift))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
