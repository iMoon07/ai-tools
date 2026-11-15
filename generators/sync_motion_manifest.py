#!/usr/bin/env python3
"""Rebuild the motion category of js/logo-manifest.js from logo/motion.

Every file in logo/motion becomes one manifest entry (id "motion:<name>").
Attribution comes from logo/motion/credits.json, which the importers fill; a
few prefix rules cover assets that were imported without a row. The same data
is written to logo/motion/CREDITS.md so the attribution ships with the library.

  python3 ai-tools/generators/sync_motion_manifest.py \
      --site /home/moon/Projects/imoon07.github.io --logo-dir /home/moon/Projects/logo
"""
import argparse
import json
import re
from pathlib import Path

CATEGORY = "motion"
EXTS = (".svg", ".webp", ".gif", ".png")
# prefix -> (author, licence, source)
RULES = {
    "spin-": ("n3r4zzurr0", "MIT", "https://github.com/n3r4zzurr0/svg-spinners"),
}
SELF = ("Alur", "MIT (this repository)", "")


def credits_for(name, rows):
    hit = rows.get(name)
    if hit:
        return hit
    for prefix, (author, lic, src) in RULES.items():
        if name.startswith(prefix):
            return {"author": author, "license": lic, "license_name": lic, "source": src,
                    "credit": "%s — %s" % (name, author), "origin": "third-party"}
    return {"author": SELF[0], "license": SELF[1], "license_name": SELF[1],
            "source": SELF[2], "credit": "%s (self-authored)" % name, "origin": "self"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="/home/moon/Projects/imoon07.github.io")
    ap.add_argument("--logo-dir", default="/home/moon/Projects/logo")
    args = ap.parse_args()

    motion = Path(args.logo_dir) / CATEGORY
    out_js = Path(args.site) / "js" / "logo-manifest.js"
    credits_path = motion / "credits.json"

    rows = {}
    if credits_path.is_file():
        for row in json.loads(credits_path.read_text(encoding="utf-8")):
            rows[row.get("name")] = row

    text = out_js.read_text(encoding="utf-8")
    m = re.match(r"^(/\*.*?\*/\nwindow\.ALUR_LOGO_MANIFEST = )(\{.*\});$", text, re.S)
    if not m:
        raise SystemExit("manifest format not recognised: %s" % out_js)
    data = json.loads(m.group(2))

    entries, missing = [], []
    for path in sorted(motion.iterdir()):
        if not path.is_file() or path.suffix.lower() not in EXTS:
            continue
        name = path.stem
        row = credits_for(name, rows)
        if not rows.get(name):
            missing.append(name)
        entries.append({
            "id": "%s:%s" % (CATEGORY, name),
            "name": name,
            "category": CATEGORY,
            "file": "%s/%s" % (CATEGORY, path.name),
            "ext": path.suffix.lower().lstrip("."),
            "dark": False,
            "motion": True,
            "author": row.get("author", ""),
            "license": row.get("license", ""),
            "source": row.get("source", ""),
            "search": ("%s %s animated motion %s" % (name, CATEGORY, row.get("author", ""))).lower(),
        })

    logos = [e for e in data["logos"] if e.get("category") != CATEGORY]
    logos.extend(entries)
    logos.sort(key=lambda e: (e["name"], e["category"]))
    data["logos"] = logos
    cats = [c for c in data.get("categories", []) if c != CATEGORY]
    if cats and cats[-1] == "brand":
        cats.insert(-1, CATEGORY)
    else:
        cats.append(CATEGORY)
    data["categories"] = cats

    out_js.write_text(m.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
                      encoding="utf-8")

    rows_out = []
    for e in entries:
        row = dict(credits_for(e["name"], rows))
        row["name"] = e["name"]
        row["file"] = e["file"]
        rows_out.append(row)
    credits_path.write_text(json.dumps(sorted(rows_out, key=lambda r: r["file"]),
                                       indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = ["# Motion credits", "",
             "Every file in this folder is animated and free to use in the Alur canvas.",
             "Third-party assets keep their author and licence below.", "",
             "| File | Author | Licence | Source |", "| --- | --- | --- | --- |"]
    for row in sorted(rows_out, key=lambda r: r["file"]):
        lines.append("| `%s` | %s | %s | %s |" % (
            row["file"], row.get("author") or "—", row.get("license") or "—",
            row.get("source") or "—"))
    (motion / "CREDITS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("manifest: %d logos (%d motion) -> %s" % (len(logos), len(entries), out_js))
    if missing:
        print("no credit row, defaulted: %d (%s)" % (len(missing), ", ".join(missing[:6])))


if __name__ == "__main__":
    main()