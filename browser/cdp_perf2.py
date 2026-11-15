import subprocess, time, json, urllib.request, websocket, shutil
profile='/tmp/alur-probes/cdp-profile2'; shutil.rmtree(profile, ignore_errors=True)
chrome=subprocess.Popen(['/usr/bin/chromium','--headless=new','--no-sandbox','--disable-gpu','--remote-debugging-port=9223','--remote-allow-origins=*','--user-data-dir='+profile,'--window-size=1200,800','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for _ in range(100):
        try:
            pages=json.load(urllib.request.urlopen('http://127.0.0.1:9223/json/list'))
            if pages: break
        except Exception: time.sleep(0.1)
    ws=websocket.create_connection(pages[0]['webSocketDebuggerUrl'], timeout=30); mid=0
    def cmd(method, params=None):
        global mid; mid+=1; ws.send(json.dumps({'id':mid,'method':method,'params':params or {}}))
        while True:
            msg=json.loads(ws.recv())
            if msg.get('id')==mid: return msg
    cmd('Page.enable'); cmd('Runtime.enable'); cmd('Page.navigate', {'url':'http://localhost:8000/imoon07.github.io/preview.html'}); time.sleep(3)
    expr=r'''
(async()=>{const sleep=ms=>new Promise(r=>setTimeout(r,ms));const d=document,w=window;const out={};w.__mounts=[];const orig=w.Alur.mount;w.Alur.mount=function(){const t=performance.now();const r=orig.apply(this,arguments);w.__mounts.push(performance.now()-t);return r;};
 const nodes={};for(let i=0;i<60;i++){nodes['n'+i]={x:(i%10)*120+30,y:Math.floor(i/10)*100+30,w:100,h:48,shape:i%3?'box':'pill',label:'N'+i,sub:'svc',color:['blue','green','amber','purple','cyan'][i%5],logo:'stack:docker',logoSize:14,logoPos:'left'};}
 const edges=[];for(let i=0;i<59;i++)edges.push({from:'n'+i,to:'n'+(i+1),cable:['solid','neon','glow','bundle'][i%4],motion:['flow','comet','flowMany','dash'][i%4]});
 const spec={module:'canvas',title:'Perf60',grid:true,width:1300,height:700,nodes,edges,zoom:1,panX:0,panY:0};
 let t=performance.now();d.getElementById('spec').value=JSON.stringify(spec);d.getElementById('apply').click();out.applyMs=performance.now()-t;await sleep(600);out.mounts=w.__mounts.slice(-1);w.__mounts.length=0;
 const svg=d.querySelector('#stage svg'),r=svg.getBoundingClientRect(),sx=r.left+r.width/2,sy=r.top+r.height/2;function pe(target,type,x,y,buttons){target.dispatchEvent(new w.PointerEvent(type,{bubbles:true,cancelable:true,clientX:x,clientY:y,pointerId:3,button:0,buttons:buttons}));}
 t=performance.now();pe(svg,'pointerdown',sx,sy,4);for(let i=0;i<60;i++)pe(svg,'pointermove',sx+i*2,sy+i,4);out.panMs=performance.now()-t;pe(svg,'pointerup',sx+118,sy+59,0);
 const handle=d.querySelector('#stage [data-handle="se"]');if(handle){const hr=handle.getBoundingClientRect(),hx=hr.left+4,hy=hr.top+4;t=performance.now();pe(handle,'pointerdown',hx,hy,1);for(let i=0;i<30;i++)pe(handle,'pointermove',hx+i*2,hy+i,1);out.resizeMs=performance.now()-t;out.resizeMounts=w.__mounts.length;pe(handle,'pointerup',hx+58,hy+29,0);}else out.resize='no handle';
 await sleep(300);w.__mounts.length=0;t=performance.now();for(let i=0;i<20;i++)svg.dispatchEvent(new w.WheelEvent('wheel',{bubbles:true,cancelable:true,deltaY:-8,clientX:sx,clientY:sy}));out.zoomMs=performance.now()-t;await sleep(300);out.finalMounts=w.__mounts.length;return JSON.stringify(out);})()
'''
    res=cmd('Runtime.evaluate', {'expression':expr,'awaitPromise':True,'returnByValue':True}); print(res['result']['result'].get('value'))
finally:
    chrome.terminate()
    try: chrome.wait(timeout=5)
    except: chrome.kill()
