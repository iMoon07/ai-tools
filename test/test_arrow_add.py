from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time,json
opts=Options(); opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-gpu'); opts.add_argument('--window-size=1440,900')
d=webdriver.Chrome(service=webdriver.chrome.service.Service('/usr/bin/chromedriver'),options=opts)
d.get('http://127.0.0.1:8000/imoon07.github.io/preview.html'); time.sleep(1)
d.execute_script("localStorage.removeItem('ruang.scene.v1')"); d.refresh(); time.sleep(.8)
d.find_element(By.CSS_SELECTOR,'[data-tool="arrow"]').click()
d.execute_script("""
var svg=document.querySelector('#stage svg');
function e(t,x,y,buttons){return new PointerEvent(t,{clientX:x,clientY:y,bubbles:true,cancelable:true,pointerId:1,pointerType:'mouse',button:0,buttons:buttons});}
svg.dispatchEvent(e('pointerdown',250,400,1)); window.dispatchEvent(e('pointermove',650,400,1)); window.dispatchEvent(e('pointerup',650,400,0));
"""); time.sleep(.3)
print('points before',len(d.find_elements(By.CSS_SELECTOR,'.alur-edge-point')))
d.execute_script("""
var p=document.querySelector('.alur-canvas-edge'); var r=p.getBoundingClientRect();
var x=r.x+r.width/2,y=r.y+r.height/2;
for(var i=0;i<2;i++) p.dispatchEvent(new MouseEvent('dblclick',{clientX:x,clientY:y,bubbles:true,cancelable:true}));
"""); time.sleep(.4)
print('points after',len(d.find_elements(By.CSS_SELECTOR,'.alur-edge-point')))
print('spec points',len(json.loads(d.execute_script("return document.getElementById('stage').getAttribute('data-spec')"))['edges'][0]['points']))
d.quit()
