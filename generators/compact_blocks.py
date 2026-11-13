#!/usr/bin/env python3
"""Rewrite topology fences into the compact syntax.

- category blocks (1..9): drop root/app/edges/legend, keep one grid of stacks,
  add a group label + multi-logo `icons` arrays.
- flow (0) and platform (10): compact arrays, keep edges/legend/facilities.
"""
import json
import pathlib
import re
import sys

BASE = pathlib.Path('/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture')
LANGS = ['en', 'id', 'ms', 'tl']

# id -> list of component logos shown inside the node
ICONS = {
    'mean': ['si-mongodb', 'si-express', 'si-angular', 'si-nodejs'],
    'mern': ['si-mongodb', 'si-express', 'si-react', 'si-nodejs'],
    'mevn': ['si-mongodb', 'si-express', 'si-vue', 'si-nodejs'],
    'pern': ['si-postgresql', 'si-express', 'si-react', 'si-nodejs'],
    'nextjs': ['si-react', 'si-nextdotjs', 'si-nodejs'],
    't3': ['si-typescript', 'si-prisma', 'si-nextdotjs', 'si-tailwindcss'],
    'jamstack': ['si-jamstack'],
    'bun': ['si-bun', 'si-sqlite'],
    'laravel': ['si-php', 'si-laravel'],
    'symfony': ['si-php', 'si-symfony'],
    'lamp': ['si-linux', 'si-apache', 'si-mysql', 'si-php'],
    'lemp': ['si-linux', 'si-nginx', 'si-mysql', 'si-php'],
    'wamp': ['si-windows', 'si-apache', 'si-mysql', 'si-php'],
    'wimp': ['si-windows', 'si-mysql', 'si-php'],
    'famp': ['si-freebsd', 'si-apache', 'si-mysql', 'si-php'],
    'xampp': ['si-apache', 'si-mariadb', 'si-php', 'si-perl'],
    'django': ['si-python', 'si-django'],
    'fastapi': ['si-python', 'si-fastapi'],
    'flask': ['si-python', 'si-flask'],
    'pyramid': ['si-python'],
    'aspnet': ['si-dotnet'],
    'blazor': ['si-dotnet'],
    'spring': ['si-openjdk', 'si-spring'],
    'jakarta': ['si-openjdk'],
    'quarkus': ['si-openjdk', 'si-quarkus'],
    'rails': ['si-ruby', 'si-rubyonrails'],
    'sinatra': ['si-ruby'],
    'gin': ['si-go'],
    'echo': ['si-go'],
    'fiber': ['si-go'],
    'gostd': ['si-go'],
    'actix': ['si-rust'],
    'axum': ['si-rust'],
    'rocket': ['si-rust'],
    'wazuh': ['si-wazuh'],
    'elk': ['si-elasticsearch', 'si-logstash', 'si-kibana'],
    'promgraf': ['si-prometheus', 'si-grafana'],
    'tick': ['si-influxdb'],
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


def compact_node(n):
    out = [n.get('label', ''), n.get('sub', '')]
    if n.get('icons'):
        out.append(n['icons'])
    else:
        out.append(n.get('icon', 'circle-dot'))
    out.append(n.get('kind', 'process'))
    if n.get('href'):
        out.append(n['href'])
    if n.get('live'):
        out.append(n['live'])
    return out


def compact_edge(e):
    out = [e['from'], e['to']]
    if e.get('badge'):
        out.append(e['badge'])
    if e.get('back') or e.get('style') == 'back':
        out.append(True)
    return out


def flow_block(s):
    return {
        'vertical': True,
        'title': s.get('title', ''),
        'columns': [[nid] for col in s['columns'] for nid in col['nodes']],
        'nodes': {nid: compact_node(n) for nid, n in s['nodes'].items()},
        'edges': [compact_edge(e) for e in s.get('edges', [])],
        'groups': [[g['label'], g['nodes'], g.get('icon')] for g in s.get('groups', []) if g.get('icon')],
        'legend': {item['type']: item['label'] for item in s.get('legend', [])},
        'facilities': [s.get('facilitiesLabel', 'In this place')] + [[f['icon'], f['label']] for f in s.get('facilities', [])],
    }


def category_block(s):
    root_icon = None
    for nid, n in s['nodes'].items():
        if n.get('kind') == 'out' and nid == 'root':
            root_icon = n.get('icon')
    grid_col = next((c for c in s['columns'] if c.get('grid')), None)
    ids = [nid for col in s['columns'] for nid in col['nodes'] if nid not in ('root', 'app')]
    grid = 4 if len(ids) >= 4 else max(2, len(ids))
    nodes = {}
    for nid in ids:
        node = compact_node(s['nodes'][nid])
        if nid in ICONS:
            node[2] = ICONS[nid]
        nodes[nid] = node
    return {
        'title': s.get('title', ''),
        'grid': grid,
        'columns': [ids],
        'nodes': nodes,
        'groups': [[s.get('title', ''), ids, root_icon]],
    }


def platform_block(s):
    # A ("stack is ready") is implied by the section prose; drop it so the
    # diagram stays narrow enough to read without scaling.
    nodes = {k: v for k, v in s['nodes'].items() if k != 'A'}
    grid_ids = [nid for col in s['columns'] if col.get('grid') for nid in col['nodes']]
    edges = [e for e in s.get('edges', []) if e['from'] != 'A' and e['to'] != 'A']
    return {
        'vertical': True,
        'title': s.get('title', ''),
        'legend': {item['type']: item['label'] for item in s.get('legend', [])},
        'facilities': [s.get('facilitiesLabel', 'Roles')] +
                      [['git-branch', 'Choice'], ['server', 'Platform'], ['layers', 'Application']],
        'columns': [['B'], {'nodes': grid_ids, 'grid': 3}, ['I']],
        'nodes': {nid: compact_node(n) for nid, n in nodes.items()},
        'edges': [compact_edge(e) for e in edges],
    }


def convert(text):
    blocks = list(re.finditer(r'```topology\n(.*?)\n```', text, re.S))
    if len(blocks) != 11:
        raise SystemExit('expected 11 topology blocks, got %d' % len(blocks))
    out = []
    last = 0
    for bi, m in enumerate(blocks):
        s = json.loads(m.group(1))
        if bi == 0:
            new = flow_block(s)
        elif bi == 10:
            new = platform_block(s)
        else:
            new = category_block(s)
        out.append(text[last:m.start()])
        out.append('```topology\n' + dump(new) + '\n```')
        last = m.end()
    out.append(text[last:])
    return ''.join(out)


def main():
    for lang in LANGS:
        p = BASE / ('server-single-tier-stack-%s.md' % lang)
        if not p.exists():
            print('skip', p)
            continue
        text = p.read_text()
        p.write_text(convert(text))
        print('rewrote', p.name)


if __name__ == '__main__':
    main()