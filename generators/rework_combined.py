#!/usr/bin/env python3
"""Rework the combined stack diagram: component logos, solution-stack caption,
natural labels (no leader/member wording), links kept.
"""
import json
import pathlib
import re

BASE = pathlib.Path('/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture')

ICONS = {
    'mean': ['si-mongodb', 'si-express', 'si-angular', 'si-nodejs'],
    'mern': ['si-mongodb', 'si-express', 'si-react', 'si-nodejs'],
    'mevn': ['si-mongodb', 'si-express', 'si-vue', 'si-nodejs'],
    'pern': ['si-postgresql', 'si-express', 'si-react', 'si-nodejs'],
    'nextjs': ['si-react', 'si-nextdotjs', 'si-nodejs'],
    't3': ['si-typescript', 'si-prisma', 'si-nextdotjs', 'si-tailwindcss'],
    'jamstack': ['si-javascript', 'si-jamstack'],
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
    'gin': ['si-go'], 'echo': ['si-go'], 'fiber': ['si-go'], 'gostd': ['si-go'],
    'actix': ['si-rust'], 'axum': ['si-rust'], 'rocket': ['si-rust'],
    'wazuh': ['si-wazuh'],
    'elk': ['si-elasticsearch', 'si-logstash', 'si-kibana'],
    'promgraf': ['si-prometheus', 'si-grafana'],
    'tick': ['si-influxdb'],
}

LEADER_HREF = {
    'js': 'https://en.wikipedia.org/wiki/JavaScript',
    'php': 'https://en.wikipedia.org/wiki/PHP',
    'python': 'https://en.wikipedia.org/wiki/Python_(programming_language)',
    'dotnet': 'https://en.wikipedia.org/wiki/.NET',
    'java': 'https://en.wikipedia.org/wiki/Java_(programming_language)',
    'ruby': 'https://en.wikipedia.org/wiki/Ruby_(programming_language)',
    'go': 'https://en.wikipedia.org/wiki/Go_(programming_language)',
    'rust': 'https://en.wikipedia.org/wiki/Rust_(programming_language)',
    'infra': 'https://en.wikipedia.org/wiki/Infrastructure',
}

SOLUTION_HREF = 'https://en.wikipedia.org/wiki/Solution_stack'


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


def rework(spec):
    columns = []
    nodes = {}
    for col in spec['columns']:
        new_col = []
        for nid in col:
            old = spec['nodes'][nid]
            label = old[0]
            href = old[4] if len(old) > 4 else None
            if nid in LEADER_HREF:
                nodes[nid] = [label, '', old[2], 'out', LEADER_HREF[nid]]
            else:
                icons = ICONS.get(nid, [old[2]])
                item = [label, '', icons if len(icons) > 1 else icons[0], 'tech']
                if href:
                    item.append(href)
                nodes[nid] = item
            new_col.append(nid)
        columns.append(new_col)
    return {
        'caption': 'Solution Stack',
        'captionHref': SOLUTION_HREF,
        'title': 'Solution Stack',
        'dense': True,
        'columns': columns,
        'nodes': nodes,
    }


def main():
    for lang in ['en', 'id', 'ms', 'tl']:
        p = BASE / ('server-single-tier-stack-%s.md' % lang)
        text = p.read_text()
        blocks = list(re.finditer(r'```topology\n(.*?)\n```', text, re.S))
        if len(blocks) != 3:
            raise SystemExit('%s: expected 3 blocks, got %d' % (lang, len(blocks)))
        old = json.loads(blocks[1].group(1))
        new = rework(old)
        out = text[:blocks[1].start()] + '```topology\n' + dump(new) + '\n```' + text[blocks[1].end():]
        p.write_text(out)
        print('rewrote', p.name)


if __name__ == '__main__':
    main()