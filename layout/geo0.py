import json,re,subprocess
out = subprocess.run(["/usr/bin/chromium","--headless","--no-sandbox","--disable-gpu",
  "--window-size=1280,900","--virtual-time-budget=5000","--dump-dom","file:///home/moon/Projects/ai-tools/snapshots/pages/harness-en.html"],
  capture_output=True,text=True,timeout=90).stdout
# build a JS measurement by injecting? simpler: regex the SVG paths of block 0
m = re.search(r'<div class="topology[^"]*"[^>]*data-index="0".*?</div>\s*</figure>', out, re.S)
if not m:
    # fallback: first .topology block
    m = re.search(r'<div class="topology.*?</div>\s*</div>\s*</div>\s*</figure>', out, re.S)
seg = m.group(0) if m else out[:200000]
paths = re.findall(r'<path[^>]*d="([^"]+)"[^>]*class="([^"]*)"', seg)
print('paths', len(paths))
for d,c in paths: print(c, d[:110])
print('--- nodes ---')
for mm in re.finditer(r'<div class="topo-node ([^"]*)" data-node="([^"]*)"[^>]*style="([^"]*)"', seg):
    print(mm.group(2), mm.group(1), mm.group(3)[:80])
