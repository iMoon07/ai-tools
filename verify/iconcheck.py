import re,subprocess,json
CHROME="/usr/bin/chromium"
for lang in ["en","id","ms","tl"]:
    out=subprocess.run([CHROME,"--headless","--no-sandbox","--disable-gpu",
        "--window-size=1280,900","--virtual-time-budget=5000","--dump-dom",
        f"file:///home/moon/Projects/ai-tools/snapshots/pages/harness-{lang}.html"],capture_output=True,text=True,timeout=90).stdout
    uses=set(re.findall(r'<use[^>]*href="#([^"]+)"',out))
    have=set(re.findall(r'\bid="([^"]+)"',out))
    miss=sorted(u for u in uses if u not in have)
    print(lang,"uses",len(uses),"missing",miss)
