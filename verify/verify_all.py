import os, re, subprocess, sys

ROOT = "/home/moon/Projects/Penjelajah-CyberSecurity"
EXP = ROOT + "/Experiments"
SCOPE = [
    "linux-investigation",
    "linux-post-exploitation",
    "web-security/WEBSHELL-REVERSE-SHELL",
    "web-security/SQLI-WEBSHELL-REVSHELL",
    "web-security/COMMAND-INJECTION-REVERSE-SHELL",
]

G = set("│▼▲┌┐└┘├┤┬┴┼─↓↑→←")
DIAGRAM_BOX = re.compile(r"\+[-=]{3,}\+")

issues = []
stats = {"files": 0, "mermaid": 0, "text": 0, "links": 0}


def strip_fences(t):
    out, inf = [], False
    for line in t.splitlines():
        if line.startswith("```"):
            inf = not inf
            continue
        if not inf:
            out.append(line)
    return out


def head(f):
    try:
        return subprocess.check_output(["git", "show", "HEAD:" + f], cwd=ROOT).decode()
    except subprocess.CalledProcessError:
        return None


def check_file(path):
    rel = os.path.relpath(path, EXP)
    raw = open(path, newline="").read()
    t = raw.replace("\r\n", "\n")
    stats["files"] += 1

    fences = len(re.findall(r"^```", t, re.M))
    if fences % 2:
        issues.append("%s: jumlah code fence ganjil (%d)" % (rel, fences))

    mer = list(re.finditer(r"^```mermaid[ \t]*\n(.*?)\n```", t, re.S | re.M))
    stats["mermaid"] += len(mer)
    for i, m in enumerate(mer):
        body = m.group(1)
        first = body.strip().splitlines()[0].strip() if body.strip() else ""
        if not re.match(r"^(flowchart|graph)\s+(TD|TB|LR|RL|BT)\b", first):
            issues.append("%s: mermaid#%d first line invalid: %r" % (rel, i, first))
        if body.count("[") != body.count("]"):
            issues.append("%s: mermaid#%d bracket tidak seimbang" % (rel, i))
        if body.count('"') % 2:
            issues.append("%s: mermaid#%d quote ganjil" % (rel, i))
        if body.count("(") != body.count(")"):
            issues.append("%s: mermaid#%d paren tidak seimbang" % (rel, i))
        if "```" in body:
            issues.append("%s: mermaid#%d mengandung fence" % (rel, i))
        if re.search(r"^\s+\S", body, re.M) and "    " not in body:
            issues.append("%s: mermaid#%d indentasi aneh" % (rel, i))

    txt = list(re.finditer(r"^```text[ \t]*\n(.*?)\n```", t, re.S | re.M))
    stats["text"] += len(txt)
    for i, m in enumerate(txt):
        body = m.group(1)
        if any(c in body for c in G) or DIAGRAM_BOX.search(body):
            issues.append("%s: text#%d masih berupa diagram ASCII" % (rel, i))

    # language link
    name = os.path.basename(path)
    links = re.findall(r"\[(🇮🇩|🇬🇧)[^\]]*\]\(([^)]+\.md)\)", t)
    stats["links"] += len(links)
    if name.endswith("-en.md"):
        if len(links) != 1 or links[0][0] != "🇮🇩" or not links[0][1].endswith("-id.md"):
            issues.append("%s: link bahasa EN salah %r" % (rel, links))
        if "🇬🇧" in t:
            issues.append("%s: -en.md mengandung bendera EN" % rel)
    elif name.endswith("-id.md"):
        if len(links) != 1 or links[0][0] != "🇬🇧" or not links[0][1].endswith("-en.md"):
            issues.append("%s: link bahasa ID salah %r" % (rel, links))
        if "🇮🇩" in t:
            issues.append("%s: -id.md mengandung bendera ID" % rel)
    else:
        if links:
            issues.append("%s: file tanpa suffix -en/-id punya link bahasa %r" % (rel, links))

    # resolve links & images
    d = os.path.dirname(path)
    targets = []
    for m in re.finditer(r"!?\[[^\]]*\]\(([^)]+)\)", t):
        l = m.group(1).strip()
        if l.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if m.group(0).startswith("!["):
            if not os.path.isfile(os.path.join(d, l)):
                issues.append("%s: gambar tidak ada -> %s" % (rel, l))
        else:
            targets.append(l)
            if not os.path.exists(os.path.join(d, l)):
                issues.append("%s: link rusak -> %s" % (rel, l))
    dup = [x for x in set(targets) if targets.count(x) > 1 and x.endswith(".md")]
    for x in dup:
        issues.append("%s: link duplikat -> %s" % (rel, x))

    # non-fence content diff vs HEAD
    old = head(os.path.relpath(path, ROOT))
    if old is not None:
        a, b = strip_fences(old), strip_fences(t)
        if a != b:
            changed = [l for l in set(a) ^ set(b) if "🇮🇩" not in l and "🇬🇧" not in l]
            if changed:
                issues.append("%s: isi non-kode berubah (di luar link bahasa): %r" % (rel, changed[:3]))
            else:
                stats.setdefault("link_fix", 0)
                stats["link_fix"] += 1

    # line endings preserved vs HEAD
    oldraw = subprocess.run(["git", "show", "HEAD:" + os.path.relpath(path, ROOT)],
                            cwd=ROOT, capture_output=True).stdout.decode("utf-8", "replace")
    if oldraw:
        if ("\r\n" in oldraw) != ("\r\n" in raw):
            issues.append("%s: line ending berubah (CRLF<->LF)" % rel)


for s in SCOPE:
    base = os.path.join(EXP, s)
    if not os.path.isdir(base):
        issues.append("folder tidak ada: " + s)
        continue
    for dp, _, fs in os.walk(base):
        for f in sorted(fs):
            if f.endswith(".md"):
                check_file(os.path.join(dp, f))

print("files=%d mermaid=%d text=%d links=%d link_fix_files=%d"
      % (stats["files"], stats["mermaid"], stats["text"], stats["links"], stats.get("link_fix", 0)))
print("issues=%d" % len(issues))
for i in issues:
    print(" -", i)