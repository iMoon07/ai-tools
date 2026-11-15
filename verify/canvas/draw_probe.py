import json, subprocess, time, urllib.parse, urllib.request, base64, shutil, sys

PORT = 9431
PROF = "/tmp/alur-probes/prof-draw"
BASE = "http://127.0.0.1:8123/draw.html"
shutil.rmtree(PROF, ignore_errors=True)
proc = subprocess.Popen(["chromium", "--headless=new", f"--remote-debugging-port={PORT}",
    f"--user-data-dir={PROF}", "--no-first-run", "--no-default-browser-check",
    "--disable-gpu", "--window-size=1400,1000", "--remote-allow-origins=*", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
import websocket

def http(p, method="GET"):
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(f"http://127.0.0.1:{PORT}{p}", method=method), timeout=10).read())

for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)

def newtab():
    t = http("/json/new?" + urllib.parse.quote("about:blank", safe=""), method="PUT")
    ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
    n = [0]
    def send(m, **p):
        n[0] += 1
        ws.send(json.dumps({"id": n[0], "method": m, "params": p}))
        while True:
            r = json.loads(ws.recv())
            if r.get("id") == n[0]:
                if r.get("error"): raise RuntimeError(r["error"])
                if r.get("method") == "Runtime.consoleAPICalled":
                    a = r["params"]["args"]
                    print("   [console]", " ".join(str(x.get("value", x.get("description"))) for x in a))
                if r.get("method") == "Runtime.exceptionThrown":
                    print("   [exception]", r["params"]["exceptionDetails"].get("text"))
                return r.get("result", {})
    return ws, send

def run(width, height, label):
    ws, send = newtab()
    send("Runtime.enable"); send("Page.enable"); send("Log.enable")
    send("Emulation.setDeviceMetricsOverride", width=width, height=height, deviceScaleFactor=1, mobile=width < 700)
    send("Page.navigate", url=BASE)
    time.sleep(4)
    print(f"== {label} ({width}x{height}) ==")
    print("  module registered:", send("Runtime.evaluate", returnByValue=True,
          expression="JSON.stringify({hasTopology: !!(window.Alur && Alur.get('topology')), engine: !!window.Topology})")["result"]["value"])

    # insert a flow block -> exercises AlurKit.arrowHead
    send("Runtime.evaluate", expression="document.querySelector('[data-scene-module=flow]').click()")
    time.sleep(2)
    heads = send("Runtime.evaluate", returnByValue=True, expression="""JSON.stringify(
      [...document.querySelectorAll('.alur-edge-head')].map(p => ({
        d: p.getAttribute('d'), sw: p.getAttribute('stroke-width'),
        fill: p.getAttribute('fill'), cap: p.getAttribute('stroke-linecap'),
        len: Math.round(p.getTotalLength ? p.getTotalLength() : 0)
      })).slice(0, 6))""")["result"]["value"]
    print("  arrowheads:", heads)

    # insert a topology block
    send("Runtime.evaluate", expression="document.querySelector('[data-scene-module=topology]').click()")
    time.sleep(2)
    info = send("Runtime.evaluate", returnByValue=True, expression="""(()=>{
      const emb = document.querySelector('.alur-module-embed[data-module=topology]');
      if (!emb) return JSON.stringify({found:false});
      const nodes = emb.querySelectorAll('.topo-node');
      const paths = emb.querySelectorAll('path');
      const holder = emb.closest('.alur-topology') || emb.parentElement;
      return JSON.stringify({
        found: true,
        nodes: nodes.length,
        paths: paths.length,
        gridClass: !!holder.querySelector('.is-grid'),
        bg: getComputedStyle(holder).backgroundImage.slice(0, 60),
        w: Math.round(emb.getBoundingClientRect().width),
        scrollW: emb.scrollWidth, clientW: emb.clientWidth
      });
    })()""")["result"]["value"]
    print("  topology block:", info)

    # toggle grid off in spec and re-render
    send("Runtime.evaluate", expression="""(()=>{const s=JSON.parse(document.getElementById('spec').value);
      const k=Object.keys(s.nodes).find(id=>s.nodes[id].shape==='module'&&s.nodes[id].module==='topology');
      s.nodes[k].moduleSpec.grid=false;
      document.getElementById('spec').value=JSON.stringify(s,null,2);
      document.getElementById('spec').dispatchEvent(new Event('input',{bubbles:true}));
      return k;})()""")
    time.sleep(2)
    grid = send("Runtime.evaluate", returnByValue=True, expression="""(()=>{
      const emb=document.querySelector('.alur-module-embed[data-module=topology]');
      const holder=emb && (emb.closest('.alur-topology')||emb.parentElement);
      return JSON.stringify({bg: holder ? getComputedStyle(holder).backgroundImage.slice(0,40) : 'n/a',
                             cls: holder ? holder.className : 'n/a'});
    })()""")["result"]["value"]
    print("  after grid=false:", grid)
    ws.close()

run(1400, 1000, "desktop")
run(390, 844, "mobile")
proc.terminate()