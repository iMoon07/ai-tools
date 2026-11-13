#!/usr/bin/env python3
"""Fetch Thridy 3D icons (hacking / crime / virus set) into logo/security-3d/.

For each page slug we read the embedded `contentUrl` (512px WebP with alpha),
download it, and write a manifest entry. Public preview assets only - no
account, no download credit is consumed.

Usage: python3 thridy_fetch.py [--group hack,crime] [--out DIR] [--limit N]
"""
import argparse
import concurrent.futures as cf
import json
import re
import subprocess
import sys
from pathlib import Path

UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/140.0 Safari/537.36')
BASE = 'https://thridy.com'
LICENSE = 'free, attribution required'
CANDIDATES = str(Path(__file__).with_name('thridy-candidates.json'))


def group_of(slug, cands):
    for g, slugs in cands['by_group'].items():
        if slug in slugs:
            return g
    return ''


def load_manifest(outdir):
    p = outdir / 'manifest.json'
    if not p.exists():
        return {}
    return {e['slug']: e for e in json.loads(p.read_text()) if e.get('slug')}


def sh(args):
    return subprocess.run(args, capture_output=True, text=True).stdout


def slug_from_url(url):
    return url.rstrip('/').split('/')[-1]


def resolve(slug):
    """Return (slug, page_url, asset_url, title) for a page slug."""
    page = f'{BASE}/{slug}'
    html = sh(['curl', '-sS', '--max-time', '40', '-A', UA, page])
    if not html:
        return None
    m = re.search(r'https://thridy\.com/i/dicons/([A-Za-z0-9._\-]+?\.webp)', html)
    if not m:
        m = re.search(r'https://cdn\.thridy\.com/icons/([A-Za-z0-9._\-]+?\.png)', html)
        asset = f'https://cdn.thridy.com/icons/{m.group(1)}' if m else None
    else:
        asset = f'https://thridy.com/i/dicons/{m.group(1)}'
    t = re.search(r'<title>(.*?)</title>', html, re.S)
    title = re.sub(r'\s+', ' ', t.group(1)).strip() if t else slug
    if not asset:
        return None
    return {'slug': slug, 'page': page, 'asset': asset, 'title': title}


def download(item, outdir):
    ext = '.png' if item['asset'].endswith('.png') else '.webp'
    dest = outdir / f"{item['slug']}{ext}"
    if dest.exists() and dest.stat().st_size > 1000:
        return 'cached', dest
    r = subprocess.run(['curl', '-sSL', '--max-time', '60', '-A', UA,
                        '-o', str(dest), '-w', '%{http_code}', item['asset']],
                       capture_output=True, text=True)
    if r.stdout.strip() != '200' or not dest.exists() or dest.stat().st_size < 1000:
        dest.unlink(missing_ok=True)
        return 'fail', item['asset']
    return 'ok', dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--group', default='hack,crime')
    ap.add_argument('--out', default='/home/moon/Projects/logo/security-3d/thridy')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--slugs', default='')
    a = ap.parse_args()

    cands = json.loads(Path(CANDIDATES).read_text())
    if a.slugs:
        slugs = [s for s in a.slugs.split(',') if s]
    else:
        slugs = []
        for g in a.group.split(','):
            slugs += cands['by_group'][g.strip()]
        slugs = sorted(set(slugs))
    if a.limit:
        slugs = slugs[:a.limit]

    outdir = Path(a.out)
    outdir.mkdir(parents=True, exist_ok=True)
    print(f'{len(slugs)} slugs -> {outdir}')

    items = []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for res in ex.map(resolve, slugs):
            if res:
                items.append(res)
            else:
                print('  no asset:', file=sys.stderr)
    print(f'resolved {len(items)}/{len(slugs)}')

    manifest = load_manifest(outdir)
    counts = {}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for item, (status, info) in zip(items, ex.map(lambda i: download(i, outdir), items)):
            counts[status] = counts.get(status, 0) + 1
            if status == 'fail':
                print('  fail:', info)
            entry = {**item, 'status': status,
                     'group': group_of(item['slug'], cands),
                     'file': Path(info).name if status != 'fail' else None}
            if status != 'fail':
                entry['license'] = LICENSE
                entry['format'] = Path(info).suffix.lstrip('.')
                entry['bytes'] = Path(info).stat().st_size
            manifest[item['slug']] = entry

    (outdir / 'manifest.json').write_text(
        json.dumps([manifest[k] for k in sorted(manifest)], indent=1))
    print(f'manifest entries: {len(manifest)}')
    print('downloads:', counts)


if __name__ == '__main__':
    main()