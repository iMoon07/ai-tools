import re, sys, os, json

ROOT = "/home/moon/Projects"
TGT = ROOT + "/Penjelajah-CyberSecurity/Experiments"

pairs = []
# linux-investigation
pairs += [
 (TGT+"/linux-investigation/LINUX-ENUMERATION-INVESTIGATION/linux-enumeration-investigation-en.md",
  ROOT+"/LINUX-INVESTIGATION-FLOW/LINUX-ENUMERATION-INVESTIGATION/linux-enumeration-investigation-en.md"),
 (TGT+"/linux-investigation/LINUX-ENUMERATION-INVESTIGATION/linux-enumeration-investigation-id.md",
  ROOT+"/LINUX-INVESTIGATION-FLOW/LINUX-ENUMERATION-INVESTIGATION/linux-enumeration-investigation-id.md"),
 (TGT+"/linux-investigation/REVERSE-SHELL-DETECTION/reverse-shell-server-side-en.md",
  ROOT+"/LINUX-INVESTIGATION-FLOW/REVERSE-SHELL-DETECTION/reverse-shell-server-side-en.md"),
 (TGT+"/linux-investigation/REVERSE-SHELL-DETECTION/reverse-shell-server-side-id.md",
  ROOT+"/LINUX-INVESTIGATION-FLOW/REVERSE-SHELL-DETECTION/reverse-shell-server-side.md"),
]
# linux-post-exploitation + web-security from LINUX-ATTACK-CHAIN
for sub in os.listdir(ROOT+"/LINUX-ATTACK-CHAIN"):
    sd = ROOT+"/LINUX-ATTACK-CHAIN/"+sub
    if not os.path.isdir(sd): continue
    for cand in ["/linux-post-exploitation/"+sub, "/web-security/"+sub]:
        td = TGT + cand
        if os.path.isdir(td):
            for f in sorted(os.listdir(sd)):
                if f.endswith(".md") and os.path.exists(td+"/"+f):
                    pairs.append((td+"/"+f, sd+"/"+f))

def blocks(text, lang):
    pat = re.compile(r"^```"+lang+r"[ \t]*\n(.*?)^```", re.S|re.M)
    return [m for m in pat.finditer(text)]

GLYPHS = set("│▼▲┌┐└┘├┤┬┴┼─↓↑→←╔╗╚╝║═")

for tgt, src in pairs:
    if not os.path.exists(src):
        print("MISSING SRC", src); continue
    tt = open(tgt, encoding="utf-8").read()
    st = open(src, encoding="utf-8").read()
    tb = blocks(tt, "text")
    sb = blocks(st, "mermaid")
    dia = [b for b in tb if any(ch in b.group(1) for ch in GLYPHS)]
    print("="*90)
    print(os.path.relpath(tgt, TGT))
    print("  src:", os.path.relpath(src, ROOT))
    print("  text-blocks=%d  diagram-like=%d  mermaid-src=%d" % (len(tb), len(dia), len(sb)))
    for i,b in enumerate(dia):
        first = b.group(1).strip().splitlines()[0][:60]
        print("    D%02d @%d: %s" % (i, tt[:b.start()].count("\n")+1, first))
    for i,b in enumerate(sb):
        first = b.group(1).strip().splitlines()[0][:60]
        print("    M%02d: %s" % (i, first))