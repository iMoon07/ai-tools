import re,subprocess,json
CHROME="/usr/bin/chromium"
out=subprocess.run([CHROME,"--headless","--no-sandbox","--disable-gpu",
 "--window-size=1280,900","--virtual-time-budget=5000","--dump-dom",
 "file:///home/moon/Projects/ai-tools/snapshots/pages/harness-en.html"],capture_output=True,text=True,timeout=90).stdout
# per topology block, count marker-end
blocks=re.split(r'<div class="topology',out)[1:]
for i,b in enumerate(blocks):
    me=b.count("marker-end")
    flow=b.count("topo-arrow-flow")
    back=b.count("topo-arrow-back")
    print("block",i,"marker-end",me,"flow-markers",flow,"back-markers",back)
