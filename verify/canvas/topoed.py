import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT = 9703; PROF = "/tmp/alur-probes/prof-topoed"
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
n = [0]; exc = []

def send(m, **p):
    n[0] += 1; ws.send(json.dumps({"id": n[0], "method": m, "params": p}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == n[0]: return r.get("result", {})
        if r.get("method") == "Runtime.exceptionThrown":
            d = r["params"]["exceptionDetails"]
            exc.append(d.get("text", "") + " " + (d.get("exception") or {}).get("description", "")[:200])

def ev(e):
    r = send("Runtime.evaluate", expression=e, returnByValue=True, awaitPromise=True).get("result", {})
    return r.get("value") if r.get("subtype") != "error" else {"__err": r.get("description")}

send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride", width=1600, height=1000, deviceScaleFactor=1, mobile=False)
send("Page.navigate", url="http://127.0.0.1:8123/topology.html")
time.sleep(3.4)

SRC = """```topology
topology Toko Kopi
  c  Customer  browser
  p  Waiter  waiter
  k  Chef  cook
  g  Pantry  warehouse
  c > p : 1
  p > k : 2
  k > g : 3
  g < k : 4
```"""

ev("""(()=>{const t=document.getElementById('specBox');
 t.value=%s; t.dispatchEvent(new Event('input',{bubbles:true}));
 return t.value.slice(0,40)})()""" % json.dumps(SRC))
time.sleep(1.6)

SRC = '```topology\ntopology Solution Stack\n  js  JS / TS  javascript typescript\n    mean  MEAN  mongodb express angular nodejs\n    mern  MERN  mongodb express react nodejs\n    mevn  MEVN  mongodb express vue nodejs\n    pern  PERN  postgresql express react nodejs\n    nextjs  Next.js  react nextdotjs nodejs\n    t3  T3  typescript trpc prisma nextdotjs tailwindcss\n    jamstack  JAMstack  si-jamstack\n    bun  Bun  si-bun\n  php  PHP  si-php\n    laravel  Laravel  si-laravel\n    symfony  Symfony  si-symfony\n    lamp  LAMP  linux apache mysql php\n    lemp  LEMP  linux nginx mysql php\n    wamp  WAMP  windows apache mysql php\n    wimp  WIMP  windows iis mysql php\n    famp  FAMP  freebsd apache mysql php\n    xampp  XAMPP  apache mariadb php perl\n  python  Python  si-python\n    django  Django  si-django\n    fastapi  FastAPI  si-fastapi\n    flask  Flask  si-flask\n    pyramid  Pyramid  si-pyramid\n  dotnet  .NET  si-dotnet\n    aspnet  ASP.NET Core  dotnet\n    blazor  Blazor  si-blazor\n  java  Java  openjdk\n    spring  Spring  si-spring\n    jakarta  Jakarta EE  openjdk jakartaee\n    quarkus  Quarkus  si-quarkus\n  ruby  Ruby  si-ruby\n    rails  Ruby on Rails  ruby rubyonrails\n    sinatra  Sinatra  si-sinatra\n  go  Go  si-go\n    gin  Gin  si-gin\n    echo  Echo  si-echo\n    fiber  Fiber  si-fiber\n    gostd  Go Stdlib  go\n  rust  Rust  si-rust\n    actix  Actix Web  si-actix\n    axum  Axum  si-axum\n    rocket  Rocket  si-rocket\n  infra  Infra  server\n    wazuh  Wazuh  wazuh-manager wazuh-indexer wazuh-dashboard\n    elk  Elastic Stack (ELK)  elasticsearch logstash kibana\n    promgraf  Prometheus + Grafana  prometheus grafana\n    tick  TICK Stack  telegraf influxdb chronograf kapacitor\n  root  Solution Stack  layers\n```'
print("status  :", json.dumps(ev("document.getElementById('codeStatus').textContent")))
print("stack   :", json.dumps(ev("(function(){\n  try{\n    var box=document.getElementById('specBox');\n    var t=box.value;\n    t=t.slice(t.indexOf('\\n')+1);\n    t=t.slice(0,t.lastIndexOf('\\n```'));\n    var spec=window.Topo.parse(t);\n    var d=document.createElement('div');\n    window.Topo.render(d,spec);\n    return 'no error';\n  }catch(e){return (e&&e.stack)||String(e);}\n})()\n")))
print("preview :", json.dumps(ev("""(()=>{const p=document.getElementById('preview');
 const nodes=[...p.querySelectorAll('.tp-node')];
 return {cls:p.className, nodes:nodes.length, cols:p.querySelectorAll('.tp-col').length,
   edges:p.querySelectorAll('.tp-wires-g > *').length,
   labels:nodes.map(nd=>(nd.querySelector('.tp-node-label')||{}).textContent||''),
   icons:p.querySelectorAll('.tp-icon').length,
   fail:/Diagram (gagal|tidak)/.test(p.textContent)};})()""")))
print("fence   :", json.dumps(ev("document.getElementById('specBox').value")))
print("panels  :", json.dumps(ev("""(()=>{const c=document.getElementById('nodeList');
 return {cards:c.children.length, first:(c.querySelector('.card-head b')||{}).textContent||''};})()""")))

# tautkan ulang: parse hasil fence lagi (round-trip)
ev("""(()=>{const t=document.getElementById('specBox');
 t.value='```topology\\n'+document.getElementById('specBox').value.replace(/^```topology\\n/,'').replace(/\\n```$/,'')+'\\n```';
 t.dispatchEvent(new Event('input',{bubbles:true}));return 1})()""")
time.sleep(1.2)
print("status2 :", json.dumps(ev("document.getElementById('codeStatus').textContent")))
print("preview2:", json.dumps(ev("document.getElementById('preview').querySelectorAll('.tp-node').length")))

print("exceptions:", exc if exc else "none")
proc.terminate()