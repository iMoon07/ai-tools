#!/usr/bin/env python3
"""Import a third-party animated-SVG set into logo/motion (normalised).

svg-spinners (MIT) ships the same spinner twice: SMIL and CSS keyframes. SMIL
wins because it survives every renderer we use, including <image> on the
canvas. Files are re-titled, kept at their own viewBox, and stamped with a
comment block so the origin stays in the file.

  python3 ai-tools/generators/import_motion_svg.py --src assets/motion/svg-spinners \
      --out /home/moon/Projects/logo/motion --prefix spin --license MIT \
      --author n3r4zzurr0 --source https://github.com/n3r4zzurr0/svg-spinners
"""
import argparse
import re
from pathlib import Path

RE_NAME = re.compile(r"<svg\b[^>]*>", re.S)


def slug(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "motion"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", default="/home/moon/Projects/logo/motion")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--license", default="")
    ap.add_argument("--author", default="")
    ap.add_argument("--source", default="")
    ap.add_argument("--glob", default="*.svg")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src = Path(args.src)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    files = sorted(src.glob(args.glob))
    print("found %d svg in %s" % (len(files), src))

    taken, written, skipped = {}, 0, 0
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "<animate" not in text and "@keyframes" not in text:
            print("  - skip (static):", path.name)
            skipped += 1
            continue

        base = slug(path.stem)
        if args.prefix:
            base = "%s-%s" % (args.prefix, base)
        name = base
        n = 2
        while name in taken:
            name = "%s-%d" % (base, n)
            n += 1
        taken[name] = True

        # one comment line before <svg>, so the file still parses standalone
        stamp = "<!-- %s | %s | %s%s -->\n" % (
            name,
            args.author or "unknown",
            args.license or "see source",
            (" | " + args.source) if args.source else "",
        )
        body = text.lstrip()
        if body.startswith("<?xml"):
            body = body.split("?>", 1)[1].lstrip()
        if body.startswith("<!--"):
            body = body.split("-->", 1)[1].lstrip()
        body = RE_NAME.sub(lambda m: m.group(0), body, count=1)
        target = out / ("%s.svg" % name)
        if not args.dry_run:
            target.write_text(stamp + body, encoding="utf-8")
        written += 1
        print("  + %-34s %6d B" % (target.name, len(stamp) + len(body)))

    print("imported %d, skipped %d -> %s" % (written, skipped, out))


if __name__ == "__main__":
    main()