import subprocess, time, json, urllib.request, websocket, os, shutil, sys
profile='/tmp/kilo/cdp-profile'
shutil.rmtree(profile, ignore_errors=True)
chrome=subprocess.Popen(['/usr/bin/chromium','--headless=new','--no-sandbox','--disable-gpu','--remote-debugging-port=9222','--remote-allow-origins=*','--user-data-dir='+profile,'--window-size=1200,800','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for _ in range(100):
        try:
            pages=json.load(urllib.request.urlopen('http://127.0.0.1:9222/json/list'))
            if pages: break
        except Exception: time.sleep(0.1)
    page=pages[0]
    ws=websocket.create_connection(page['webSocketDebuggerUrl'], timeout=30)
    mid=0
    def cmd(method, params=None):
        global mid
        mid+=1
        ws.send(json.dumps({'id':mid,'method':method,'params':params or {}}))
        while True:
            msg=json.loads(ws.recv())
            if msg.get('id')==mid: return msg
    cmd('Page.enable'); cmd('Runtime.enable')
    cmd('Page.navigate', {'url':'http://localhost:8000/imoon07.github.io/preview.html'})
    time.sleep(3.0)
    expr=r'''
(async()=>{
 const sleep=ms=>new Promise(r=>setTimeout(r,ms));
 const out={};
 const d=document, w=window;
 out.ready=!!(d.getElementById('stage')&&d.querySelector('#stage svg'));
 w.__mounts=[]; const orig=w.Alur.mount; w.Alur.mount=function(){const t=performance.now();const r=orig.apply(this,arguments);w.__mounts.push(performance.now()-t);return r;};
 const nodes={}; for(let i=0;i<18;i++){nodes['n'+i]={x:(i%6)*220+40,y:Math.floor(i/6)*150+40,w:180,h:64,shape:i%3?'box':'pill',label:'Node '+i,sub:'service',color:['blue','green','amber','purple'][i%4],logo:'stack:docker',logoSize:18,logoPos:'left'};}
 const edges=[]; for(let i=0;i<17;i++){edges.push({from:'n'+i,to:'n'+(i+1),cable:'neon',motion:'flowMany',count:3,duration:2600});}
 const spec={module:'canvas',title:'Perf',grid:true,width:1200,height:800,nodes,edges,zoom:1,panX:0,panY:0};
 let t=performance.now(); d.getElementById('spec').value=JSON.stringify(spec); d.getElementById('apply').click(); out.applyMs=performance.now()-t;
 await sleep(600); out.mounts=w.__mounts.slice(-1).map(x=>Math.round(x*100)/100); w.__mounts.length=0;
 const svg=d.querySelector('#stage svg'); const r=svg.getBoundingClientRect(); const sx=r.left+r.width/2, sy=r.top+r.height/2;
 function pe(target,type,x,y,buttons){target.dispatchEvent(new w.PointerEvent(type,{bubbles:true,cancelable:true,clientX:x,clientY:y,pointerId:3,button:0,buttons:buttons}));}
 t=performance.now(); pe(svg,'pointerdown',sx,sy,4); for(let i=0;i<60;i++) pe(svg,'pointermove',sx+i*2,sy+i,4); out.panMs=performance.now()-t; pe(svg,'pointerup',sx+118,sy+59,0);
 const handle=d.querySelector('#stage [data-handle="se"]'); if(handle){const hr=handle.getBoundingClientRect();const hx=hr.left+4,hy=hr.top+4; t=performance.now(); pe(handle,'pointerdown',hx,hy,1); for(let i=0;i<30;i++) pe(handle,'pointermove',hx+i*2,hy+i,1); out.resizeMs=performance.now()-t; out.resizeMounts=w.__mounts.length; pe(handle,'pointerup',hx+58,hy+29,0);} else out.resize='no handle';
 await sleep(300); w.__mounts.length=0; t=performance.now(); for(let i=0;i<20;i++) svg.dispatchEvent(new w.WheelEvent('wheel',{bubbles:true,cancelable:true,deltaY:-8,clientX:sx,clientY:sy})); out.zoomMs=performance.now()-t;
 await sleep(300); out.finalMounts=w.__mounts.length;
 return JSON.stringify(out);
})()
'''
    res=cmd('Runtime.evaluate', {'expression':expr,'awaitPromise':True,'returnByValue':True})
    print(res['result']['result'].get('value'))
finally:
    chrome.terminate()
    try: chrome.wait(timeout=5)
    except: chrome.kill()
