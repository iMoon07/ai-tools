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
print('before',d.execute_script("var b=document.querySelector('.alur-canvas-node .alur-node-box'); b.dataset.test='same'; return [b.getAttribute('stroke-width'), b.style.strokeWidth, document.querySelector('.alur-canvas-node').getAttribute('opacity')]"))
# input width and opacity
d.execute_script("""
var rs=document.querySelectorAll('#shapePanelBody input[type=range]');
rs[0].value='6'; rs[0].dispatchEvent(new Event('input',{bubbles:true}));
rs[1].value='50'; rs[1].dispatchEvent(new Event('input',{bubbles:true}));
"""); time.sleep(.2)
print('after',d.execute_script("var b=document.querySelector('.alur-canvas-node .alur-node-box'); return [b.dataset.test, b.getAttribute('stroke-width'), b.style.strokeWidth, document.querySelector('.alur-canvas-node').getAttribute('opacity')]"))
print('panel still',d.execute_script("return !document.getElementById('shapePanel').hidden"))
d.quit()
