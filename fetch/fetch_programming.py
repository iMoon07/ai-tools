#!/usr/bin/env python3
import urllib.request
from pathlib import Path

OUT = Path("/home/moon/Projects/logo/programming")
OUT.mkdir(parents=True, exist_ok=True)

# filename -> simpleicons slug
ITEMS = {
    "typescript.svg": "typescript",
    "java.svg": "openjdk",
    "kotlin.svg": "kotlin",
    "swift.svg": "swift",
    "php.svg": "php",
    "ruby.svg": "ruby",
    "perl.svg": "perl",
    "lua.svg": "lua",
    "dart.svg": "dart",
    "r.svg": "r",
    "scala.svg": "scala",
    "haskell.svg": "haskell",
    "elixir.svg": "elixir",
    "erlang.svg": "erlang",
    "clojure.svg": "clojure",
    "cplusplus.svg": "cplusplus",
    "csharp.svg": "csharp",
    "dotnet.svg": "dotnet",
    "nodejs.svg": "nodedotjs",
    "deno.svg": "deno",
    "bun.svg": "bun",
    "zig.svg": "zig",
    "nim.svg": "nim",
    "julia.svg": "julia",
    "ocaml.svg": "ocaml",
    "fortran.svg": "fortran",
    "solidity.svg": "solidity",
    "webassembly.svg": "webassembly",
    "crystal.svg": "crystal",
    "v.svg": "v",
    "groovy.svg": "apachegroovy",
    "objective-c.svg": "objectivec",
    "shell.svg": "gnubash",
    "matlab.svg": "mathworks",
}

def valid_svg(data: bytes) -> bool:
    if len(data) < 50:
        return False
    head = data[:512].lstrip().lower()
    return b"<svg" in head or b"<?xml" in head

results = []
for name, slug in sorted(ITEMS.items()):
    dest = OUT / name
    if dest.exists():
        results.append((name, "EXISTS", "already present"))
        continue
    url = f"https://cdn.simpleicons.org/{slug}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "logo-fetcher/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        if not valid_svg(data):
            results.append((name, "FAIL", "invalid svg"))
            continue
        dest.write_bytes(data)
        results.append((name, "DOWNLOADED", f"ok {len(data)}b"))
    except Exception as e:
        results.append((name, "FAIL", str(e)))

ok = sum(1 for r in results if r[1] in ("OK","DOWNLOADED","EXISTS"))
print(f"OK={ok}")
for r in results:
    print("|".join(r))
