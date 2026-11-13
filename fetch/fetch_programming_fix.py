#!/usr/bin/env python3
import urllib.request
from pathlib import Path
OUT = Path('/home/moon/Projects/logo/programming')

ITEMS = [
  ('csharp.svg','https://cdn.simpleicons.org/sharp','Simple Icons CDN (sharp)'),
  ('objective-c.svg','https://cdn.simpleicons.org/apple','Simple Icons CDN (apple placeholder?) nope'),
]
# better targeted retries
RETRIES = [
  ('csharp.svg','https://cdn.simpleicons.org/csharp','Simple Icons'),
  ('csharp.svg','https://cdn.simpleicons.org/dotnet','Simple Icons (dotnet alt)?'),
]
# proper list
ITEMS = [
  ('assemblyscript.svg','https://cdn.simpleicons.org/assemblyscript','Simple Icons'),
  ('coffeescript.svg','https://cdn.simpleicons.org/coffeescript','Simple Icons'),
  ('markdown.svg','https://cdn.simpleicons.org/markdown','Simple Icons'),
  ('yaml.svg','https://cdn.simpleicons.org/yaml','Simple Icons'),
  ('json.svg','https://cdn.simpleicons.org/json','Simple Icons'),
  ('html5.svg','https://cdn.simpleicons.org/html5','Simple Icons'),
  ('css.svg','https://cdn.simpleicons.org/css','Simple Icons'),
  ('sass.svg','https://cdn.simpleicons.org/sass','Simple Icons'),
  ('matlab.svg','https://cdn.simpleicons.org/gnuoctave','Simple Icons (GNU Octave alt)'),
]

def valid_svg(data):
    if len(data)<50: return False
    h=data[:512].lstrip().lower()
    return b'<svg' in h or b'<?xml' in h

results=[]
for name,url,note in ITEMS:
    dest=OUT/name
    if dest.exists():
        results.append((name,'EXISTS','already present',url))
        continue
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'logo-fetcher/1.0'})
        with urllib.request.urlopen(req,timeout=20) as r:
            data=r.read()
        if not valid_svg(data):
            results.append((name,'FAIL','invalid',url))
            continue
        dest.write_bytes(data)
        results.append((name,'DOWNLOADED',f'ok {len(data)}b',url))
    except Exception as e:
        results.append((name,'FAIL',str(e),url))
for r in results:
    print('|'.join(r))
