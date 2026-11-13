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
 """,x1,y1,x2,y2); time.sleep(.35)
def spec(): return json.loads(d.execute_script("return document.getElementById('stage').getAttribute('data-spec')"))
d.find_element(By.CSS_SELECTOR,'[data-tool="box"]').click(); drag(300,250,480,340)
print('shape panel visible',d.execute_script("return !document.getElementById('shapePanel').hidden"))
print('title',d.execute_script("return document.getElementById('shapePanelTitle').textContent"))
print('groups',d.execute_script("return Array.from(document.querySelectorAll('#shapePanelBody .shape-label')).map(function(e){return e.textContent})"))
# click red swatch in stroke group (first group)
print('swatches',len(d.find_elements(By.CSS_SELECTOR,'#shapePanelBody .swatch')))
# click fill transparent? choose green fill (second swatch group)
d.execute_script("""
var labels=document.querySelectorAll('#shapePanelBody .shape-label'); var g;
for (var i=0;i<labels.length;i++) { if (labels[i].textContent === 'Background') { g=labels[i].parentNode; break; } }
var b=g.querySelectorAll('.swatch')[2]; b.click();
"""); time.sleep(.4)
s=spec(); n=list(s['nodes'].values())[0]; print('fill',n.get('fill'))
# change width
d.execute_script("""
var r=document.querySelectorAll('#shapePanelBody input[type=range]')[0]; r.value='4'; r.dispatchEvent(new Event('input',{bubbles:true}));
"""); time.sleep(.3)
n=list(spec()['nodes'].values())[0]; print('strokeWidth',n.get('strokeWidth'))
# style dashed
d.execute_script("""
var ss=document.querySelectorAll('#shapePanelBody select'); var e=ss[0]; e.value='dashed'; e.dispatchEvent(new Event('change',{bubbles:true}));
"""); time.sleep(.4)
n=list(spec()['nodes'].values())[0]; print('strokeStyle',n.get('strokeStyle'))
print('style attr',d.execute_script("var b=document.querySelector('.alur-canvas-node .alur-node-box'); return b ? b.getAttribute('style') : 'none'"))
# ctrl+a boxes
d.execute_script("document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'a',ctrlKey:true,bubbles:true}))"); time.sleep(.3)
print('select boxes',len(d.find_elements(By.CSS_SELECTOR,'.alur-selection-box')))
# tool stays active after drawing circle
d.find_element(By.CSS_SELECTOR,'[data-tool="circle"]').click(); drag(600,250,720,370)
print('tool after draw',d.execute_script("return document.querySelector('#statusTool').textContent"))
print('circle nodes',len(spec()['nodes']))
d.quit()
