from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time,json
opts=Options(); opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-gpu'); opts.add_argument('--window-size=1440,900')
d=webdriver.Chrome(service=webdriver.chrome.service.Service('/usr/bin/chromedriver'),options=opts)
d.get('http://127.0.0.1:8000/imoon07.github.io/preview.html'); time.sleep(1)
d.execute_script("localStorage.removeItem('ruang.scene.v1')"); d.refresh(); time.sleep(.8)
def drag(x1,y1,x2,y2):
 d.execute_script("""
 var svg=document.querySelector('#stage svg');
 function e(t,x,y,buttons){return new PointerEvent(t,{clientX:x,clientY:y,bubbles:true,cancelable:true,pointerId:1,pointerType:'mouse',button:0,buttons:buttons});}
 svg.dispatchEvent(e('pointerdown',arguments[0],arguments[1],1)); window.dispatchEvent(e('pointermove',arguments[2],arguments[3],1)); window.dispatchEvent(e('pointerup',arguments[2],arguments[3],0));
 """,x1,y1,x2,y2); time.sleep(.3)
def spec(): return json.loads(d.execute_script("return document.getElementById('stage').getAttribute('data-spec')"))
# text tool
d.find_element(By.CSS_SELECTOR,'[data-tool="text"]').click(); drag(350,300,500,350)
print('text nodes',len(spec().get('nodes',{})))
print('inline visible',d.execute_script("var e=document.getElementById('inlineText'); return e && getComputedStyle(e).display !== 'none'"))
d.execute_script("var e=document.getElementById('inlineText'); e.value='Hello world'; e.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}))"); time.sleep(.3)
print('label',list(spec().get('nodes',{}).values())[0].get('label'))
# free arrow
d.find_element(By.CSS_SELECTOR,'[data-tool="arrow"]').click(); drag(250,450,650,450)
print('free edges',len(spec().get('edges',[])),'selected',spec().get('selectedEdge'))
print('points',len(d.find_elements(By.CSS_SELECTOR,'.alur-edge-point')))
# click edge path
print('edge path count',len(d.find_elements(By.CSS_SELECTOR,'.alur-canvas-edge')))
# click at center of path
d.execute_script("""
var p=document.querySelector('.alur-canvas-edge'); var r=p.getBoundingClientRect(); var x=r.x+r.width/2,y=r.y+r.height/2;
p.dispatchEvent(new PointerEvent('pointerdown',{clientX:x,clientY:y,bubbles:true,cancelable:true,pointerId:1,pointerType:'mouse',button:0,buttons:1}));
window.dispatchEvent(new PointerEvent('pointerup',{clientX:x,clientY:y,bubbles:true,cancelable:true,pointerId:1,pointerType:'mouse',button:0,buttons:0}));
"""); time.sleep(.3)
print('selected edge after click',spec().get('selectedEdge'),'points',len(d.find_elements(By.CSS_SELECTOR,'.alur-edge-point')))
# linked arrow test: drag from node to empty then release on node? create box
d.find_element(By.CSS_SELECTOR,'[data-tool="box"]').click(); drag(700,300,850,400)
print('nodes',len(spec().get('nodes',{})))
# arrow from first node to second using node element events
d.find_element(By.CSS_SELECTOR,'[data-tool="arrow"]').click()
d.execute_script("""
var nodes=document.querySelectorAll('.alur-canvas-node'); var a=nodes[0],b=nodes[1];
function ev(t,x,y,buttons){return new PointerEvent(t,{clientX:x,clientY:y,bubbles:true,cancelable:true,pointerId:1,pointerType:'mouse',button:0,buttons:buttons});}
var ar=a.getBoundingClientRect(),br=b.getBoundingClientRect();
a.dispatchEvent(ev('pointerdown',ar.x+ar.width/2,ar.y+ar.height/2,1));
window.dispatchEvent(ev('pointermove',br.x+br.width/2,br.y+br.height/2,1));
window.dispatchEvent(ev('pointerup',br.x+br.width/2,br.y+br.height/2,0));
"""); time.sleep(.4)
s=spec(); print('edges after bind',len(s.get('edges',[])),[ (e.get('from'),e.get('to')) for e in s.get('edges',[])])
d.quit()
