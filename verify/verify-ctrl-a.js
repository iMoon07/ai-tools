(async()=>{
const targets=await (await fetch('http://127.0.0.1:9224/json')).json();
const page=targets.find(t=>t.type==='page');
const ws=new WebSocket(page.webSocketDebuggerUrl); let id=0; const p=new Map();
ws.onmessage=e=>{const m=JSON.parse(e.data); if(m.id&&p.has(m.id)){p.get(m.id)(m);p.delete(m.id);}};
await new Promise(r=>ws.onopen=r);
const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}))});
const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true}); if(r.result.exceptionDetails)console.log('EXC',JSON.stringify(r.result.exceptionDetails).slice(0,500)); return r.result&&r.result.result&&r.result.result.value};
await send('Runtime.enable'); await send('Page.enable');
await send('Page.navigate',{url:'file:///home/moon/Projects/imoon07.github.io/preview.html'});
await new Promise(r=>setTimeout(r,1500));
await ev("document.querySelector('[data-tool=\\\"text\\\"]').click()"); await new Promise(r=>setTimeout(r,150));
const st=await ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return{x:r.left+r.width*0.35,y:r.top+r.height*0.4}})()");
await send('Input.dispatchMouseEvent',{type:'mousePressed',x:st.x,y:st.y,button:'left',buttons:1,clickCount:1});
await send('Input.dispatchMouseEvent',{type:'mouseReleased',x:st.x,y:st.y,button:'left',buttons:0,clickCount:1});
await new Promise(r=>setTimeout(r,400));
for(const ch of 'hello'){await send('Input.dispatchKeyEvent',{type:'keyDown',text:ch,key:ch});await send('Input.dispatchKeyEvent',{type:'keyUp',key:ch});}
await ev("window.__keys=[];window.addEventListener('keydown',e=>window.__keys.push({key:e.key,ctrl:e.ctrlKey,meta:e.metaKey,target:e.target.id,prevented:e.defaultPrevented}),true);setTimeout(()=>window.__keys.push({phase:'later',sel:[document.getElementById('inlineText').selectionStart,document.getElementById('inlineText').selectionEnd]}),100)");
await send('Input.dispatchKeyEvent',{type:'rawKeyDown',modifiers:2,key:'a',code:'KeyA',windowsVirtualKeyCode:65,nativeVirtualKeyCode:65});
await send('Input.dispatchKeyEvent',{type:'keyUp',modifiers:2,key:'a',code:'KeyA',windowsVirtualKeyCode:65,nativeVirtualKeyCode:65});
await new Promise(r=>setTimeout(r,300));
console.log('keys',await ev("window.__keys"));
console.log('sel',await ev("(()=>{const a=document.getElementById('inlineText');return [a.value,a.selectionStart,a.selectionEnd]})()"));
ws.close();})();
