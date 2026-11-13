import re, io, json, subprocess

BASE = "Experiments/foundations/server-architecture"
pat = re.compile(r"```mermaid\n(.*?)```", re.S)

def nonfence(txt):
    return pat.sub("@@MERMAID@@", txt)

for lang in ["en","id","ms","tl"]:
    p = f"{BASE}/server-single-tier-stack-{lang}.md"
    txt = io.open(p, encoding="utf-8", newline="").read()
    old = subprocess.check_output(["git","show",f"HEAD:{p}"], text=True)
    ms = pat.findall(txt)
    print(f"== {lang}: blocks={len(ms)} click={txt.count('click ')}")
    print(f"   nonfence_same={nonfence(txt)==nonfence(old)}")
    for i,b in enumerate(ms):
        lines=b.split("\n")
        init=lines[0]
        assert init.startswith("%%{init: ") and init.endswith("}%%"), (lang,i)
        js=json.loads(init[len("%%{init: "):-len("}%%")].strip())
        assert js["themeVariables"]["background"]=="transparent"
        # every non-blank, non-init line that starts a node must be a valid-ish shape
        assert "```" not in b
    print("   fence_count", txt.count("```"), "balanced", txt.count("```")%2==0)
