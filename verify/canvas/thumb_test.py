import json, subprocess, time, urllib.parse, urllib.request
import websocket
PORT=9360
proc=subprocess.Popen(['chromium','--headless=new',f'--remote-debugging-port={PORT}',
 '--user-data-dir=/tmp/alur-probes/prof-th','--no-first-run','--no-default-browser-check','--disable-gpu',
 '--window-size=1280,900','--remote-allow-origins=*','about:blank'],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def http(p,method='GET'):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{PORT}{p}',method=method),timeout=10).read())
for _ in range(60):
    try: http('/json/version'); break
    except Exception: time.sleep(0.3)
t=http('/json/new?'+urllib.parse.quote('about:blank',safe=''),method='PUT')
ws=websocket.create_connection(t['webSocketDebuggerUrl'],timeout=30,suppress_origin=True)
n=0
def send(m,**p):
    global n; n+=1
    ws.send(json.dumps({'id':n,'method':m,'params':p}))
    while True:
        r=json.loads(ws.recv())
        if r.get('id')==n:
            if 'error' in r: raise RuntimeError(f"{m}: {r['error']}")
            return r.get('result',{})
def ev(e): return send('Runtime.evaluate',expression=e,returnByValue=True,awaitPromise=True).get('result',{}).get('value')
send('Page.enable'); send('Runtime.enable')

for lang in ['en']:
    send('Page.navigate',url=f'http://localhost:8777/read.html?post=linux-enumeration-investigation&lang={lang}')
    time.sleep(6)
    out = ev("JSON.stringify((()=>{const imgs=[...document.querySelectorAll('img')];return {title:document.title.slice(0,50),src:imgs.map(i=>i.getAttribute('src')).filter(s=>s&&!s.startsWith('data:')),imgs:imgs.length,hero:(document.querySelector('.article-hero img, .article-cover img, article img')||{}).getAttribute?document.querySelector('.article-hero img, .article-cover img, article img').getAttribute('src'):null};})())")
    print('related thumbs:', ev("JSON.stringify([...document.querySelectorAll('.related-item')].map(a=>({href:(a.getAttribute('href')||'').slice(0,60),thumb:(a.querySelector('img[data-thumb]')||{}).src})).slice(0,6))")[:900])
    print(lang, out[:200])
ws.close(); proc.terminate()
