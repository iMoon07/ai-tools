#!/usr/bin/env python3
"""Move rendered Lottie clips into logo/motion and record who made them.

Names come from the IconScout slug: free-security-research-animation becomes
security-research. Every asset gets a credits.json entry (author, licence,
source page) so the manifest can carry attribution and the panel can show it.

  python3 ai-tools/generators/import_motion_webp.py \
      --in assets/lottie/webp-out --out /home/moon/Projects/logo/motion
"""
import argparse
import json
import re
from pathlib import Path

STRIP = re.compile(r"^free-", re.I)
TAIL = re.compile(r"-(lottie-animation|animation|animated)$", re.I)


def clean(slug):
    s = STRIP.sub("", slug)
    s = TAIL.sub("", s)
    s = re.sub(r"-(gif|png|svg|json)-download.*$", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "motion"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", default=str(Path(__file__).resolve().parents[1] / "assets" / "motion" / "webp"))
    ap.add_argument("--out", default="/home/moon/Projects/logo/motion")
    ap.add_argument("--max-bytes", type=int, default=160 * 1024)
    ap.add_argument("--meta", default="", help="credits meta.json (default: <in>/meta.json)")
    args = ap.parse_args()

    src = Path(args.src)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = {}
    meta_path = Path(args.meta) if args.meta else (src / "meta.json")
    if meta_path.is_file():
        for row in json.loads(meta_path.read_text(encoding="utf-8")):
            meta[Path(row.get("file", "")).stem] = row

    from PIL import Image

    taken = {p.stem for p in out.glob("*.webp")}
    credits = []
    kept = dropped = 0
    for path in sorted(src.glob("*.webp")):
        im = Image.open(path)
        frames = getattr(im, "n_frames", 1)
        if frames < 2:
            print("  - not animated:", path.name)
            dropped += 1
            continue
        if path.stat().st_size > args.max_bytes:
            print("  - too big (%d B): %s" % (path.stat().st_size, path.name))
            dropped += 1
            continue

        name = clean(path.stem)
        base, n = name, 2
        while name in taken:
            name = "%s-%d" % (base, n)
            n += 1
        taken.add(name)

        target = out / ("%s.webp" % name)
        target.write_bytes(path.read_bytes())

        row = meta.get(path.stem, {})
        credits.append({
            "file": target.name,
            "name": name,
            "author": row.get("author", ""),
            "license": row.get("license", "https://iconscout.com/licenses#iconscout"),
            "license_name": "IconScout Free License (attribution)",
            "source": row.get("source", ""),
            "credit": row.get("credit", ""),
            "origin": "iconscout",
            "frames": frames,
            "bytes": target.stat().st_size,
        })
        kept += 1
        print("  + %-34s %4d frames %6d B  by %s" % (target.name, frames, target.stat().st_size, row.get("author") or "?"))

    print("kept %d, dropped %d -> %s" % (kept, dropped, out))
    if credits:
        credits.sort(key=lambda c: c["name"])
        print("credits rows: %d (write them with sync_motion_manifest.py)" % len(credits))


if __name__ == "__main__":
    main()