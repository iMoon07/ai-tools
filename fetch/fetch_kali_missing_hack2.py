#!/usr/bin/env python3
import urllib.request, urllib.parse
from pathlib import Path

SEC = Path('/home/moon/Projects/logo/security')
BASE = 'https://raw.githubusercontent.com/l0gicx/kali-flat-icons/main/'

ITEMS = [
 'A/asleap.svg',
 'C/chirp.svg',
 'C/chntpw.svg',
 'C/cutycapt.svg',
 'E/eyewitness.svg',
 'H/hping3.svg',
 'H/httrack.svg',
 'I/img_cat.svg',
 'I/img_stat.svg',
 'J/jboss-autopwn.svg',
 'L/laudanum.svg',
 'L/lbd.svg',
 'L/legion.svg',
 'M/metagoofil.svg',
 'O/oscanner.svg',
 'P/parsero.svg',
 'P/peass.svg',
 'P/pyrit.svg',
 'R/rekono.svg',
 'R/rsmangler.svg',
 'S/snmp-check.svg',
 'S/sparta.svg',
 'S/srch-string.svg',
 'U/unix-privesc-check.svg',
 'V/vfeed.svg',
 'W/watobo.svg',
 'W/weevely.svg',
 'T/thcping6.svg', # ensure (downloaded earlier? check)
]

def valid_svg(data):
    if len(data) < 60: return False
    h = data[:512].lstrip().lower()
    return b'<svg' in h or b'<?xml' in h

results = []
seen = set()
for p in ITEMS:
    name = p.split('/')[-1]
    base = p.rsplit('.',1)[0].split('/')[-1]
    out_name = base.lower().replace('_','-') + '.svg'
    if out_name in seen:
        continue
    seen.add(out_name)
    dest = SEC / out_name
    if dest.exists():
        results.append((out_name,'EXISTS',p))
        continue
    url = BASE + urllib.parse.quote(p)
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'logo-fetcher/1.0'})
        with urllib.request.urlopen(req, timeout=25) as r:
            data = r.read()
        if not valid_svg(data):
            results.append((out_name,'FAIL','invalid '+p))
            continue
        dest.write_bytes(data)
        results.append((out_name,'DOWNLOADED',f'{len(data)}b {p}'))
    except Exception as e:
        results.append((out_name,'FAIL',f'{e} {p}'))

ok = sum(1 for r in results if r[1] in ('DOWNLOADED','EXISTS'))
print(f'OK={ok}')
for r in results:
    print('|'.join(r))
