#!/usr/bin/env python3
"""Merge the nine per-language stack diagrams into one leader-first diagram.

Each category becomes a column: the language leader on top, its stack members
below. The single block is inserted at the start of the stack-combination
section, and the nine old blocks are removed.
"""
import json
import pathlib
import re

BASE = pathlib.Path('/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture')

TITLES = {
    'en': 'Technology Stack Combinations',
    'id': 'Kombinasi Stack',
    'ms': 'Gabungan Tindanan Teknologi',
    'tl': 'Mga Kombinasyon ng Technology Stack',
}

READ = {
    'en': ['How to read', ['layers', 'Leader = language'], ['package', 'Member = stack']],
    'id': ['Cara membaca', ['layers', 'Ketua = bahasa'], ['package', 'Anggota = stack']],
    'ms': ['Cara membaca', ['layers', 'Ketua = bahasa'], ['package', 'Anggota = tindanan']],
    'tl': ['Paano basahin', ['layers', 'Pinuno = wika'], ['package', 'Miembro = stack']],
}

LEADERS = [
    ('js', 'JS / TS', 'si-javascript', ['mean', 'mern', 'mevn', 'pern', 'nextjs', 't3', 'jamstack', 'bun']),
    ('php', 'PHP', 'si-php', ['laravel', 'symfony', 'lamp', 'lemp', 'wamp', 'wimp', 'famp', 'xampp']),
    ('python', 'Python', 'si-python', ['django', 'fastapi', 'flask', 'pyramid']),
    ('dotnet', '.NET', 'si-dotnet', ['aspnet', 'blazor']),
    ('java', 'Java', 'si-openjdk', ['spring', 'jakarta', 'quarkus']),
    ('ruby', 'Ruby', 'si-ruby', ['rails', 'sinatra']),
    ('go', 'Go', 'si-go', ['gin', 'echo', 'fiber', 'gostd']),
    ('rust', 'Rust', 'si-rust', ['actix', 'axum', 'rocket']),
    ('infra', 'Infra', 'server', ['wazuh', 'elk', 'promgraf', 'tick']),
]

ICONS = {
    'mean': 'si-mongodb', 'mern': 'si-mongodb', 'mevn': 'si-mongodb',
    'pern': 'si-postgresql', 'nextjs': 'si-nextdotjs', 't3': 'si-typescript',
    'jamstack': 'si-jamstack', 'bun': 'si-bun',
    'laravel': 'si-laravel', 'symfony': 'si-symfony', 'lamp': 'si-apache',
    'lemp': 'si-nginx', 'wamp': 'si-windows', 'wimp': 'si-windows',
    'famp': 'si-freebsd', 'xampp': 'si-apache',
    'django': 'si-django', 'fastapi': 'si-fastapi', 'flask': 'si-flask',
    'pyramid': 'si-python',
    'aspnet': 'si-dotnet', 'blazor': 'si-dotnet',
    'spring': 'si-spring', 'jakarta': 'si-openjdk', 'quarkus': 'si-quarkus',
    'rails': 'si-rubyonrails', 'sinatra': 'si-ruby',
    'gin': 'si-go', 'echo': 'si-go', 'fiber': 'si-go', 'gostd': 'si-go',
    'actix': 'si-rust', 'axum': 'si-rust', 'rocket': 'si-rust',
    'wazuh': 'si-wazuh', 'elk': 'si-elasticsearch', 'promgraf': 'si-prometheus',
    'tick': 'si-influxdb',
}


def dump(v, ind=0):
    sp = '  ' * ind
    if isinstance(v, dict):
        if not v:
            return '{}'
        parts = [sp + '  ' + json.dumps(k, ensure_ascii=False) + ': ' + dump(val, ind + 1)
                 for k, val in v.items()]
        return '{\n' + ',\n'.join(parts) + '\n' + sp + '}'
    if isinstance(v, list):
        if not v:
            return '[]'
        if not any(isinstance(x, dict) for x in v):
            flat = json.dumps(v, ensure_ascii=False)
            if len(flat) <= 150:
                return flat
        parts = [sp + '  ' + dump(x, ind + 1) for x in v]
        return '[\n' + ',\n'.join(parts) + '\n' + sp + ']'
    return json.dumps(v, ensure_ascii=False)


def build(lang, old_blocks):
    by_id = {}
    for b in old_blocks:
        for nid, n in b.get('nodes', {}).items():
            by_id[nid] = n

    columns = []
    nodes = {}
    for lead_id, lead_label, lead_icon, members in LEADERS:
        col = [lead_id]
        nodes[lead_id] = [lead_label, '', lead_icon, 'out']
        for mid in members:
            src = by_id.get(mid, {})
            label = src.get('label') if isinstance(src, dict) else src[0]
            href = src.get('href') if isinstance(src, dict) else (src[4] if isinstance(src, list) and len(src) > 4 else None)
            col.append(mid)
            item = [label, '', ICONS.get(mid, 'package'), 'tech']
            if href:
                item.append(href)
            nodes[mid] = item
        columns.append(col)

    return {
        'title': TITLES[lang],
        'dense': True,
        'facilities': READ[lang],
        'columns': columns,
        'nodes': nodes,
    }


def convert(text, lang):
    blocks = list(re.finditer(r'```topology\n(.*?)\n```', text, re.S))
    if len(blocks) != 11:
        raise SystemExit('expected 11 topology blocks, got %d' % len(blocks))
    specs = [json.loads(m.group(1)) for m in blocks]

    combined = build(lang, specs[1:10])

    out = []
    last = 0
    for bi, m in enumerate(blocks):
        if 1 <= bi <= 9:
            out.append(text[last:m.start()])
            last = m.end()
    out.append(text[last:])
    text = ''.join(out)

    # place the combined block at the start of the stack section
    start = text.index('## ' + TITLES[lang])
    head = text.index('\n### ', start)
    block = '```topology\n' + dump(combined) + '\n```\n\n'
    text = text[:head + 1] + block + text[head + 1:]
    return text


def main():
    for lang in ['en', 'id', 'ms', 'tl']:
        p = BASE / ('server-single-tier-stack-%s.md' % lang)
        text = p.read_text()
        p.write_text(convert(text, lang))
        print('rewrote', p.name)


if __name__ == '__main__':
    main()