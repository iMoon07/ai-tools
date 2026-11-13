import re, os

ROOT = "/home/moon/Projects"
TGT = ROOT + "/Penjelajah-CyberSecurity/Experiments"

def blocks(text, lang):
    return [m for m in re.finditer(r"^```"+lang+r"[ \t]*\n(.*?)^```", re.S|re.M, )]

def show(tgt, src, only=None):
    tt = open(tgt, encoding="utf-8").read()
    st = open(src, encoding="utf-8").read()
    tb = [m for m in re.finditer(r"^```text[ \t]*\n(.*?)^```", tt, re.S|re.M)]
    sb = [m for m in re.finditer(r"^```mermaid[ \t]*\n(.*?)^```", st, re.S|re.M)]
    print("#"*100)
    print("TARGET:", os.path.relpath(tgt, TGT))
    for i,b in enumerate(tb):
        print("--- TEXT#%d (line %d)" % (i, tt[:b.start()].count("\n")+1))
        print(b.group(1).rstrip())
    print("SOURCE:", os.path.relpath(src, ROOT))
    for i,b in enumerate(sb):
        print("--- MERMAID#%d" % i)
        print(b.group(1).rstrip())

if __name__ == "__main__":
    import sys
    show(sys.argv[1], sys.argv[2])