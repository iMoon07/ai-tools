import subprocess,time,json,urllib.request,websocket,shutil
profile='/tmp/alur-probes/cdp-profile4'; shutil.rmtree(profile,ignore_errors=True)
c=subprocess.Popen(['/usr/bin/chromium','--headless=new','--no-sandbox','--disable-gpu','--remote-debugging-port=9225','--remote-allow-origins=*','--user-data-dir='+profile,'--window-size=1200,800','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 for _ in range(100):
  try:
   p=json.load(urllib.request.urlopen('http://127.0.0.1:9225/json/list'))
   if p: break
  except: time.sleep(.1)
 ws=websocket.create_connection(p[0]['webSocketDebuggerUrl'],timeout=30);mid=0
 def cmd(m,pa=None):
  global mid;mid+=1;ws.send(json.dumps({'id':mid,'method':m,'params':pa or {}}))
  while True:
   x=json.loads(ws.recv())
   if x.get('id')==mid:return x
 cmd('Page.enable');cmd('Runtime.enable')
 cmd('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__errs=[];window.addEventListener('error',e=>window.__errs.push(String(e.message)));window.addEventListener('unhandledrejection',e=>window.__errs.push('rejection:'+String(e.reason)));"})
 cmd('Page.navigate',{'url':'http://localhost:8000/imoon07.github.io/preview.html'});time.sleep(3)
 expr=r'''(async()=>{const sleep=ms=>new Promise(r=>setTimeout(r,ms));const d=document,w=window;d.getElementById('addBox').click();await sleep(300);const n=d.querySelector('.alur-canvas-node');const r=n.getBoundingClientRect();n.dispatchEvent(new w.PointerEvent('pointerdown',{bubbles:true,cancelable:true,clientX:r.left+20,clientY:r.top+20,pointerId:1,button:0}));n.dispatchEvent(new w.PointerEvent('pointerup',{bubbles:true,cancelable:true,clientX:r.left+20,clientY:r.top+20,pointerId:1,button:0}));await sleep(200);const h=d.querySelector('.alur-handle');if(h){const hr=h.getBoundingClientRect();h.dispatchEvent(new w.PointerEvent('pointerdown',{bubbles:true,cancelable:true,clientX:hr.left+4,clientY:hr.top+4,pointerId:2,button:0}));for(let i=0;i<5;i++)h.dispatchEvent(new w.PointerEvent('pointermove',{bubbles:true,cancelable:true,clientX:hr.left+4+i*3,clientY:hr.top+4+i*2,pointerId:2,button:0,buttons:1}));h.dispatchEvent(new w.PointerEvent('pointerup',{bubbles:true,cancelable:true,clientX:hr.left+16,clientY:hr.top+12,pointerId:2,button:0}));}await sleep(400);return JSON.stringify({errs:w.__errs||[],nodes:d.querySelectorAll('.alur-node').length,spec:!!JSON.parse(d.getElementById('stage').getAttribute('data-spec'))});})()'''
 res=cmd('Runtime.evaluate',{'expression':expr,'awaitPromise':True,'returnByValue':True});print(res['result']['result'].get('value'))
finally:
 c.terminate()
 try:c.wait(timeout=5)
 except:c.kill()
