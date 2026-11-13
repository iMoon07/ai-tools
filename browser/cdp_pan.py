import subprocess,time,json,urllib.request,websocket,shutil
profile='/tmp/kilo/cdp-profile3'; shutil.rmtree(profile,ignore_errors=True)
c=subprocess.Popen(['/usr/bin/chromium','--headless=new','--no-sandbox','--disable-gpu','--remote-debugging-port=9224','--remote-allow-origins=*','--user-data-dir='+profile,'--window-size=1200,800','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 for _ in range(100):
  try:
   p=json.load(urllib.request.urlopen('http://127.0.0.1:9224/json/list'))
   if p: break
  except: time.sleep(.1)
 ws=websocket.create_connection(p[0]['webSocketDebuggerUrl'],timeout=30);mid=0
 def cmd(m,pa=None):
  global mid;mid+=1;ws.send(json.dumps({'id':mid,'method':m,'params':pa or {}}))
  while True:
   x=json.loads(ws.recv())
   if x.get('id')==mid:return x
 cmd('Page.enable');cmd('Runtime.enable');cmd('Page.navigate',{'url':'http://localhost:8000/imoon07.github.io/preview.html'});time.sleep(3)
 expr=r'''(async()=>{const sleep=ms=>new Promise(r=>setTimeout(r,ms));const d=document,w=window;const svg=d.querySelector('#stage svg');const vb0=svg.getAttribute('viewBox');const r=svg.getBoundingClientRect(),sx=r.left+r.width/2,sy=r.top+r.height/2;function pe(t,x,y,b){svg.dispatchEvent(new w.PointerEvent(t,{bubbles:true,cancelable:true,clientX:x,clientY:y,pointerId:6,button:1,buttons:b}));}pe('pointerdown',sx,sy,4);for(let i=0;i<10;i++){pe('pointermove',sx+i*8,sy+i*4,4);await sleep(16);}pe('pointerup',sx+72,sy+36,0);await sleep(300);const vb1=svg.getAttribute('viewBox');return JSON.stringify({vb0,vb1,panX:JSON.parse(d.getElementById('spec').value).panX,panY:JSON.parse(d.getElementById('spec').value).panY});})()'''
 res=cmd('Runtime.evaluate',{'expression':expr,'awaitPromise':True,'returnByValue':True});print(res['result']['result'].get('value'))
finally:
 c.terminate()
 try:c.wait(timeout=5)
 except:c.kill()
