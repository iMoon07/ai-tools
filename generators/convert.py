import re, os, sys, difflib

ROOT = "/home/moon/Projects"
TGT = ROOT + "/Penjelajah-CyberSecurity/Experiments"

PAIRS = [
 ("/linux-investigation/LINUX-ENUMERATION-INVESTIGATION/linux-enumeration-investigation-en.md",
  "/LINUX-INVESTIGATION-FLOW/LINUX-ENUMERATION-INVESTIGATION/linux-enumeration-investigation-en.md"),
 ("/linux-investigation/LINUX-ENUMERATION-INVESTIGATION/linux-enumeration-investigation-id.md",
  "/LINUX-INVESTIGATION-FLOW/LINUX-ENUMERATION-INVESTIGATION/linux-enumeration-investigation-id.md"),
 ("/linux-investigation/REVERSE-SHELL-DETECTION/reverse-shell-server-side-en.md",
  "/LINUX-INVESTIGATION-FLOW/REVERSE-SHELL-DETECTION/reverse-shell-server-side-en.md"),
 ("/linux-investigation/REVERSE-SHELL-DETECTION/reverse-shell-server-side-id.md",
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

MERMAID_RE = re.compile(r"^```mermaid[ \t]*$", re.M)
TEXT_RE = re.compile(r"^```text[ \t]*$", re.M)


def find_fenced(lines, opener_re):
    out = []
    i = 0
    while i < len(lines):
        if opener_re.match(lines[i]):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            out.append((i, j + 1))  # [start, end)
            i = j + 1
        else:
            i += 1
    return out


def plan(tgt_path, src_path):
    tl = open(tgt_path, encoding="utf-8").read().splitlines(keepends=True)
    sl = open(src_path, encoding="utf-8").read().splitlines(keepends=True)
    sb = find_fenced(sl, MERMAID_RE)
    tb = find_fenced(tl, TEXT_RE)
    sm = difflib.SequenceMatcher(None, sl, tl, autojunk=False)
    ops = sm.get_opcodes()
    repls = []
    for (s0, s1) in sb:
        j0 = j1 = None
        for tag, i1, i2, jj1, jj2 in ops:
            if i2 <= s0 or i1 >= s1:
                continue
            if tag == "equal":
                continue
            if j0 is None:
                j0, j1 = jj1, jj2
            else:
                j0, j1 = min(j0, jj1), max(j1, jj2)
        repls.append((s0, s1, j0, j1))
    return tl, sl, repls


def main(apply=False):
    for tgt_rel, src_rel in PAIRS:
        tgt_path = TGT + tgt_rel
        src_path = ROOT + src_rel
        if not os.path.exists(src_path):
            print("!! MISSING SRC", src_rel)
            continue
        tl, sl, repls = plan(tgt_path, src_path)
        print("=" * 90)
        print(tgt_rel, " mermaid=%d" % len(repls))
        for (s0, s1, j0, j1) in repls:
            if j0 is None:
                print("   !! NO TARGET MATCH for source mermaid line", s0 + 1)
                continue
            block = "".join(tl[j0:j1])
            is_text = bool(TEXT_RE.match(tl[j0])) and j1 < len(tl) and tl[j1].startswith("```")
            print("   src_mermaid@%d -> tgt[%d:%d] %s  (%d lines)" %
                  (s0 + 1, j0 + 1, j1, "OK" if is_text else "!! NOT A TEXT BLOCK", j1 - j0))
            if not is_text:
                print("      >>> " + block.replace("\n", "\n      >>> "))
        if apply:
            for (s0, s1, j0, j1) in sorted(repls, key=lambda r: -r[2]):
                if j0 is None:
                    continue
                if not (TEXT_RE.match(tl[j0]) and j1 < len(tl) and tl[j1].startswith("```")):
                    continue
                tl[j0:j1] = sl[s0:s1 - 1]
            open(tgt_path, "w", encoding="utf-8").write("".join(tl))


if __name__ == "__main__":
    main("--apply" in sys.argv)