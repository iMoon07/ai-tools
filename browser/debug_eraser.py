from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time,json
opts=Options(); opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-gpu'); opts.add_argument('--window-size=1440,900')
d=webdriver.Chrome(service=webdriver.chrome.service.Service('/usr/bin/chromedriver'),options=opts)
d.get('http://127.0.0.1:8000/imoon07.github.io/preview.html'); time.sleep(1)
d.execute_script("localStorage.removeItem('ruang.scene.v1')"); d.refresh(); time.sleep(.8)
# create box
d.find_element(By.CSS_SELECTOR,'[data-tool="box"]').click()
d.execute_script("""
var svg=document.querySelector('#stage svg');
function e(t,x,y,buttons){return new PointerEvent(t,{clientX:x,clientY:y,bubbles:true,cancelable:true,pointerId:1,pointerType:'mouse',button:0,buttons:buttons});}
svg.dispatchEvent(e('pointerdown',300,250,1)); window.dispatchEvent(e('pointermove',480,340,1)); window.dispatchEvent(e('pointerup',480,340,0));
"""); time.sleep(.4)
print('nodes', d.execute_script("return JSON.parse(document.getElementById('stage').getAttribute('data-spec')).nodes"))
print('rect', d.execute_script("var r=document.querySelector('.alur-canvas-node .alur-node-box').getBoundingClientRect(); return [r.x,r.y,r.width,r.height]"))
print('elements', d.execute_script("return document.elementsFromPoint(300,250).map(function(e){return e.tagName+'.'+(e.getAttribute('class')||'')})"))
d.find_element(By.CSS_SELECTOR,'[data-tool="eraser"]').click(); time.sleep(.1)
print('tool', d.execute_script("return document.querySelector('#statusTool').textContent"))
d.execute_script("""
var svg=document.querySelector('#stage svg');
function e(t,x,y,buttons){return new PointerEvent(t,{clientX:x,clientY:y,bubbles:true,cancelable:true,pointerId:1,pointerType:'mouse',button:0,buttons:buttons});}
svg.dispatchEvent(e('pointerdown',300,250,1)); window.dispatchEvent(e('pointermove',480,340,1)); window.dispatchEvent(e('pointerup',480,340,0));
"""); time.sleep(.4)
print('nodes after', d.execute_script("return JSON.parse(document.getElementById('stage').getAttribute('data-spec')).nodes"))
print('status', d.execute_script("return document.getElementById('statusTool').textContent"))
d.quit()
