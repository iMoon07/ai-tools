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
d.find_element(By.CSS_SELECTOR,'[data-panel="assets"]').click(); time.sleep(.3)
d.find_elements(By.CSS_SELECTOR,'.logo-tile')[0].click(); time.sleep(.4)
def state(): return json.loads(d.execute_script("return document.getElementById('stage').getAttribute('data-spec')"))
print('nodes',state()['nodes'])
def size(): return d.execute_script("var i=document.querySelector('.alur-canvas-node .alur-logo-img'); return i ? i.getAttribute('width') : null")
print('size before',size())
d.execute_script("""
var h=document.querySelector('.alur-handle[data-handle="se"]"); var r=h.getBoundingClientRect();
var x=r.x+r.width/2,y=r.y+r.height/2;
function e(t,x,y,buttons){return new PointerEvent(t,{clientX:x,clientY:y,bubbles:true,cancelable:true,pointerId:1,pointerType:'mouse',button:0,buttons:buttons});}
h.dispatchEvent(e('pointerdown',x,y,1)); window.dispatchEvent(e('pointermove',x+120,y+80,1)); window.dispatchEvent(e('pointerup',x+120,y+80,0));
"""); time.sleep(.6)
print('nodes after',state()['nodes'])
print('size after',size())
d.quit()
