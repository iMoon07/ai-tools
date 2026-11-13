#!/usr/bin/env python3
import urllib.request
from pathlib import Path

OUT = Path('/home/moon/Projects/logo/stack')
BASE_KALI = 'https://raw.githubusercontent.com/l0gicx/kali-flat-icons/main/'

ITEMS = [
    # qemu already attempted, vmware exists
    ('kvm.svg', 'https://upload.wikimedia.org/wikipedia/commons/8/8f/Kvm_logo.svg', 'Wikimedia Commons'),
    ('kvm.svg', 'https://upload.wikimedia.org/wikipedia/commons/7/70/Kvmbanner-logo2_1.png', 'Wikimedia Commons (png fallback)'),
    ('kvm.png', 'https://upload.wikimedia.org/wikipedia/commons/7/70/Kvmbanner-logo2_1.png', 'Wikimedia Commons'),
    ('kvm.svg', 'https://raw.githubusercontent.com/virt-manager/virt-manager/main/data/icons/hicolor/scalable/apps/virt-manager.svg', 'virt-manager repo (alt?)'),
    ('libvirt.svg', 'https://raw.githubusercontent.com/libvirt/libvirt/master/docs/logos/logo-square.svg', 'libvirt GitHub'),
    ('vmware-workstation.svg', BASE_KALI + 'V/vmware-workstation.svg', 'kali-flat-icons'),
    ('vmware-player.svg', BASE_KALI + 'V/vmware-player.svg', 'kali-flat-icons'),
    ('vmware-netcfg.svg', BASE_KALI + 'V/vmware-netcfg.svg', 'kali-flat-icons'),
    ('gnome-boxes.svg', BASE_KALI + 'G/gnome-boxes.svg', 'kali-flat-icons'),
]

def valid_file(path: Path):
    data = path.read_bytes()
    if len(data) < 80: return False, f'too small {len(data)}b'
    h = data[:512].lstrip().lower()
    if path.suffix == '.svg':
        if b'<svg' not in h and b'<?xml' not in h: return False, 'not svg'
        if b'<html' in h or b'<!doctype html' in h: return False, 'html'
    elif path.suffix == '.png':
        if not data.startswith(b'\x89PNG\r\n\x1a\n'): return False, 'not png'
    return True, f'ok {len(data)}b'

results=[]
for name,url,note in ITEMS:
    dest = OUT/name
    if dest.exists():
        ok,msg = valid_file(dest)
        if ok:
            results.append((name,'EXISTS',msg,url,note))
            continue
        dest.unlink(missing_ok=True)
    prev = [r for r in results if r[0]==name and r[1] in ('DOWNLOADED','EXISTS')]
    if prev:
        continue
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'logo-fetcher/1.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        dest.write_bytes(data)
        ok,msg = valid_file(dest)
        if not ok:
            dest.unlink(missing_ok=True)
            results.append((name,'FAIL',f'invalid: {msg}',url,note))
        else:
            results.append((name,'DOWNLOADED',msg,url,note))
    except Exception as e:
        results.append((name,'FAIL',str(e),url,note))

from collections import OrderedDict
summary=OrderedDict()
for r in results:
    name=r[0]
    if r[1] in ('DOWNLOADED','EXISTS'):
        summary[name]=r
    elif name not in summary:
        summary.setdefault(name,r)
print('==SUMMARY==')
for n,r in summary.items():
    print('|'.join(r))
print('==ALL==')
for r in results:
    print('|'.join(r))
