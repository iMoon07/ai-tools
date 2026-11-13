import sys, json
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8000/imoon07.github.io/read.html"
MD = "http://localhost:8000/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture/server-single-tier-stack-{lang}.md"

def run(pw, lang, w, h, label):
    b = pw.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": w, "height": h})
    msgs = []
    pg.on("console", lambda m: msgs.append(m.text))
    url = BASE + "?url=" + MD.format(lang=lang)
    pg.goto(url, wait_until="load", timeout=60000)
    try:
        pg.wait_for_selector(".topology .topo-node", timeout=30000)
    except Exception as e:
        print(f"[{label}] NO TOPOLOGY NODE: {e}")
    pg.wait_for_timeout(2500)
    data = pg.evaluate("""() => {
      const out = {topo:0, mermaid:0, blocks:[], idAttrs:[], proseW:0, overflow:[]};
      const prose = document.querySelector('.prose');
      out.proseW = prose ? Math.round(prose.getBoundingClientRect().width) : 0;
      out.topo = document.querySelectorAll('.topology').length;
      out.mermaid = document.querySelectorAll('.mermaid').length;
      const nodesAll = [...document.querySelectorAll('.topo-node')];
      out.nodeCount = nodesAll.length;
      // any id attributes anywhere in content
      document.querySelectorAll('#content [id]').forEach(el => {
        out.idAttrs.push(el.tagName.toLowerCase() + '#' + el.id);
      });
      document.querySelectorAll('.topology').forEach((r,i)=>{
        const c = r.querySelector('.topo-canvas');
        const st = r.querySelector('.topo-stage');
        const cols = r.querySelector('.topo-columns');
        const cr = r.getBoundingClientRect();
        const paths = [...r.querySelectorAll('.topo-svg path')];
        let minX=1e9,maxX=-1e9,minY=1e9,maxY=-1e9;
        paths.forEach(p=>{ try{const bb=p.getBBox(); minX=Math.min(minX,bb.x);maxX=Math.max(maxX,bb.x+bb.width);minY=Math.min(minY,bb.y);maxY=Math.max(maxY,bb.y+bb.height);}catch(e){} });
        const b = {i, nodes:r.querySelectorAll('.topo-node').length, paths:paths.length,
          canvas:c?Math.round(c.offsetWidth)+'x'+Math.round(c.offsetHeight):'-',
          zoom:c?c.style.zoom:'-', stage:st?Math.round(st.clientWidth)+'x'+Math.round(st.clientHeight):'-',
          cols:cols?Math.round(cols.offsetWidth)+'x'+Math.round(cols.offsetHeight):'-',
          rootW:Math.round(cr.width), rootH:Math.round(cr.height),
          narrow:r.classList.contains('topo--narrow'),
          pathBox: isFinite(minX)?[Math.round(minX),Math.round(minY),Math.round(maxX),Math.round(maxY)]:null};
        // overlap check among nodes
        const ns=[...r.querySelectorAll('.topo-node')].map(n=>({id:n.dataset.node,rc:n.getBoundingClientRect()}));
        const ov=[];
        for(let a=0;a<ns.length;a++)for(let c2=a+1;c2<ns.length;c2++){
          const A=ns[a].rc,B=ns[c2].rc;
          if(A.left<B.right-1&&B.left<A.right-1&&A.top<B.bottom-1&&B.top<A.bottom-1) ov.push(ns[a].id+'/'+ns[c2].id);
        }
        b.overlaps=ov;
        out.blocks.push(b);
      });
      return out;
    }""")
    print(f"===== [{label}] {lang} {w}x{h} =====")
    print(json.dumps(data, indent=1, ensure_ascii=False))
    if msgs:
        print("CONSOLE:", " | ".join(msgs[-8:]))
    pg.screenshot(path=f"/home/moon/Projects/ai-tools/renders/v-{label}-{lang}.png", full_page=False)
    b.close()

with sync_playwright() as pw:
    run(pw, "en", 1280, 900, "desktop")
    run(pw, "en", 390, 844, "mobile")
    run(pw, "id", 1280, 900, "desktop")