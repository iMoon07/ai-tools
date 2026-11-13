from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time,json
opts=Options(); opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-gpu'); opts.add_argument('--window-size=1440,900')
d=webdriver.Chrome(service=webdriver.chrome.service.Service('/usr/bin/chromedriver'),options=opts)
d.get('http://127.0.0.1:8000/imoon07.github.io/preview.html'); time.sleep(1)
d.execute_script("localStorage.removeItem('ruang.scene.v1')"); d.refresh(); time.sleep(.8)
d.find_element(By.CSS_SELECTOR,'[data-tool="box"]').click()
d.execute_script("""
var svg=document.querySelector('#stage svg');
function e(t,x,y,buttons){return new PointerEvent(t,{clientX:x,clientY:y,bubbles:true,cancelable:true,pointerId:1,pointerType:'mouse',button:0,buttons:buttons});}
svg.dispatchEvent(e('pointerdown',300,250,1)); window.dispatchEvent(e('pointermove',480,340,1)); window.dispatchEvent(e('pointerup',480,340,0));
"""); time.sleep(.4)
print('labels',d.execute_script("return Array.from(document.querySelectorAll('#shapePanelBody .shape-label')).map(function(e){return e.textContent})"))
# click fill green
d.execute_script("""
var labels=document.querySelectorAll('#shapePanelBody .shape-label'); var g;
for (var i=0;i<labels.length;i++) { if (labels[i].textContent === 'Fill') { g=labels[i].parentNode; break; } }
g.querySelectorAll('.swatch')[2].click();
"""); time.sleep(.4)
print('fill props', {k:list(json.loads(d.execute_script("return document.getElementById('stage').getAttribute('data-spec')"))['nodes'].values())[0].get(k) for k in ['fill','fillStyle']})
print('labels2',d.execute_script("return Array.from(document.querySelectorAll('#shapePanelBody .shape-label')).map(function(e){return e.textContent})"))
# click cross-hatch
d.execute_script("""
var bs=Array.prototype.slice.call(document.querySelectorAll('#shapePanelBody .ghost')); var b=bs.filter(function(x){return x.textContent==='Cross-hatch';})[0]; b.click();
"""); time.sleep(.4)
print('fillStyle',list(json.loads(d.execute_script("return document.getElementById('stage').getAttribute('data-spec')"))['nodes'].values())[0].get('fillStyle'))
print('fill attr',d.execute_script("var b=document.querySelector('.alur-canvas-node .alur-node-box'); return b ? b.getAttribute('fill') : 'none'"))
print('patterns',len(d.find_elements(By.CSS_SELECTOR,'.alur-canvas-node pattern')))
d.quit()
