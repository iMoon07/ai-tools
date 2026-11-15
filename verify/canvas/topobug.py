import json, subprocess, time, urllib.parse, urllib.request, shutil, re
PORT = 9731; PROF = "/tmp/alur-probes/prof-topobug"
shutil.rmtree(PROF, ignore_errors=True)
proc = subprocess.Popen(["chromium", "--headless=new", f"--remote-debugging-port={PORT}",
    f"--user-data-dir={PROF}", "--no-first-run", "--no-default-browser-check", "--disable-gpu",
    "--window-size=1600,1000", "--remote-allow-origins=*", "--hide-scrollbars", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
import websocket

def http(p, method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}", method=method), timeout=10).read())

for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)

t = http("/json/new?" + urllib.parse.quote("about:blank", safe=""), method="PUT")
ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
n = [0]

def send(m, **p):
    n[0] += 1; ws.send(json.dumps({"id": n[0], "method": m, "params": p}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == n[0]: return r.get("result", {})

def ev(e):
    r = send("Runtime.evaluate", expression=e, returnByValue=True, awaitPromise=True).get("result", {})
    return r.get("value") if r.get("subtype") != "error" else {"__err": r.get("description")}

send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride", width=1600, height=1000, deviceScaleFactor=1, mobile=False)
send("Page.navigate", url="http://127.0.0.1:8123/topology.html")
time.sleep(3.4)

md = open('/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture/server-single-tier-stack-en.md').read()
blocks = re.findall(r'```topology[ \t]*\n([\s\S]*?)\n```', md)

for idx, body in enumerate(blocks):
    src = '```topology\n' + body + '\n```'
    ev("(()=>{const t=document.getElementById('specBox');t.value=%s;"
       "t.dispatchEvent(new Event('input',{bubbles:true}));return 1})()" % json.dumps(src))
    time.sleep(1.4)
    out = ev("""(()=>{const p=document.getElementById('preview');
      return {status:document.getElementById('codeStatus').textContent,
        nodes:document.querySelectorAll('#preview .tp-node').length,
        fail:/Render error/.test(p.textContent),
        msg:(p.textContent.match(/Render error:[^\\n]*/)||[''])[0]};})()""")
    print('block', idx, json.dumps(out))

    # uji ketahanan: ikon berupa angka/objek tidak boleh melempar
    if idx == 0:
        ev("""(()=>{const t=document.getElementById('specBox');
          let x=t.value; x=x.slice(x.indexOf('\\n')+1);
          const s=window.Topo.parse(x);
          Object.keys(s.nodes).forEach(id=>{s.nodes[id][2]=42;});
          const d=document.createElement('div');
          try{window.Topo.render(d,s);return 'ok';}catch(e){return String(e);}})()""")
        print('   bad-icon guard:', json.dumps(ev("document.getElementById('preview').textContent.slice(0,60)")))

    # cari node yang ikonnya bukan string
    bad = ev("""(()=>{const box=document.getElementById('specBox');let t=box.value;
      t=t.slice(t.indexOf('\\n')+1); t=t.slice(0,t.lastIndexOf('\\n```'));
      const s=window.Topo.parse(t); const out=[];
      Object.keys(s.nodes).forEach(id=>{const n=s.nodes[id];
        const icons=Array.isArray(n[5])?n[5]:[];
        icons.forEach(ic=>{ if(typeof ic!=='string') out.push([id,typeof ic,String(ic).slice(0,40)]); });});
      return out.slice(0,6);})()""")
    if bad:
        print('   non-string icons:', json.dumps(bad))
proc.terminate()