import re, os, difflib

ROOT = "/home/moon/Projects"
TGT = ROOT + "/Penjelajah-CyberSecurity/Experiments"

PAIRS = [
 ("/linux-investigation/LINUX-ENUMERATION-INVESTIGATION/linux-enumeration-investigation-en.md",
  "/LINUX-INVESTIGATION-FLOW/LINUX-ENUMERATION-INVESTIGATION/linux-enumeration-investigation-en.md"),
 ("/linux-investigation/LINUX-ENUMERATION-INVESTIGATION/linux-enumeration-investigation-id.md",
  "/LINUX-INVESTIGATION-FLOW/LINUX-ENUMERATION-INVESTIGATION/linux-enumeration-investigation-id.md"),
 ("/linux-investigation/REVERSE-SHELL-DETECTION/reverse-shell-server-side-en.md",
  "/LINUX-INVESTIGATION-FLOW/REVERSE-SHELL-DETECTION/reverse-shell-server-side-en.md"),
 ("/linux-investigation/REVERSE-SHELL-DETECTION/reverse-shell-server-side.md",
  "/LINUX-INVESTIGATION-FLOW/REVERSE-SHELL-DETECTION/reverse-shell-server-side.md"),
]

for sub in sorted(os.listdir(ROOT + "/LINUX-ATTACK-CHAIN")):
    sd = ROOT + "/LINUX-ATTACK-CHAIN/" + sub
    if not os.path.isdir(sd):
        continue
    for cand in ("/linux-post-exploitation/" + sub, "/web-security/" + sub):
        td = TGT + cand
        if not os.path.isdir(td):
            continue
        for f in sorted(os.listdir(sd)):
            if f.endswith(".md") and os.path.exists(td + "/" + f):
                PAIRS.append((cand + "/" + f, "/LINUX-ATTACK-CHAIN/" + sub + "/" + f))

MERMAID_OPEN = re.compile(r"^```mermaid[ \t]*\r?\n$")
TEXT_OPEN = re.compile(r"^```text[ \t]*\r?\n$")
FENCE = re.compile(r"^```\s*\r?\n$")


def read(path):
    return open(path, "r", encoding="utf-8", newline="").read()


def write(path, text):
    open(path, "w", encoding="utf-8", newline="").write(text)


def lines_of(text):
    return text.splitlines(keepends=True)


def norm(lines):
    return [l.rstrip("\r\n") for l in lines]


def eol_of(line):
    return "\r\n" if line.endswith("\r\n") else "\n"


def fenced_blocks(lines):
    out = []
    i = 0
    while i < len(lines):
        if MERMAID_OPEN.match(lines[i]) or TEXT_OPEN.match(lines[i]):
            j = i + 1
            while j < len(lines) and not FENCE.match(lines[j]):
                j += 1
            out.append((i, j + 1, lines[i].startswith("```mermaid")))
            i = j + 1
        else:
            i += 1
    return out


def difflib_convert(tgt_path, src_path):
    tl = lines_of(read(tgt_path))
    sl = lines_of(read(src_path))
    tn, sn = norm(tl), norm(sl)
    sb = [b for b in fenced_blocks(sl) if b[2]]
    ops = difflib.SequenceMatcher(None, sn, tn, autojunk=False).get_opcodes()
    repls = []
    for (s0, s1, _) in sb:
        j0 = j1 = None
        for tag, i1, i2, jj1, jj2 in ops:
            if i2 <= s0 or i1 >= s1 or tag == "equal":
                continue
            j0 = jj1 if j0 is None else min(j0, jj1)
            j1 = jj2 if j1 is None else max(j1, jj2)
        if j0 is None:
            print("   !! no target match for src mermaid line", s0 + 1)
            continue
        if not (TEXT_OPEN.match(tl[j0]) and j1 < len(tl) and FENCE.match(tl[j1])):
            print("   !! target not a text block at", j0 + 1)
            continue
        eol = eol_of(tl[j0])
        repls.append((j0, j1, s0, s1, eol))
    for (j0, j1, s0, s1, eol) in sorted(repls, key=lambda r: -r[0]):
        tl[j0:j1] = [l.rstrip("\r\n") + eol for l in sl[s0:s1 - 1]]
    write(tgt_path, "".join(tl))
    return len(repls)


def replace_text_block(tl, txt, mer):
    tn = norm(tl)
    target = txt.split("\n")
    for i, line in enumerate(tn):
        if line != "```text":
            continue
        j = i + 1
        while j < len(tl) and not FENCE.match(tl[j]):
            j += 1
        if tn[i + 1:j] == target:
            eol = eol_of(tl[i])
            tl[i:j + 1] = [l + eol for l in mer.rstrip("\n").split("\n")]
            return True
    return False


def main():
    total = 0
    for tgt_rel, src_rel in PAIRS:
        tgt_path = TGT + tgt_rel
        src_path = ROOT + src_rel
        if not os.path.exists(src_path):
            print("!! missing src", src_rel)
            continue
        n = difflib_convert(tgt_path, src_path)
        total += n
        print("%-2d %s" % (n, tgt_rel))
    print("total difflib blocks:", total)


if __name__ == "__main__":
    main()