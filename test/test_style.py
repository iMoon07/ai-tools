from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time,json
opts=Options(); opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-gpu'); opts.add_argument('--window-size=1440,900')
d=webdriver.Chrome(service=webdriver.chrome.service.Service('/usr/bin/chromedriver'),options=opts)
d.get('http://127.0.0.1:8000/imoon07.github.io/preview.html'); time.sleep(1)
d.execute_script("localStorage.removeItem('ruang.scene.v1')"); d.refresh(); time.sleep(.8)
print('properties display',d.execute_script("return getComputedStyle(document.getElementById('panelProperties')).display"))
d.find_element(By.CSS_SELECTOR,'[data-tool="box"]').click()
d.execute_script("""
var svg=document.querySelector('#stage svg');
function e(t,x,y,buttons){return new PointerEvent(t,{clientX:x,clientY:y,bubbles:true,cancelable:true,pointerId:1,pointerType:'mouse',button:0,buttons:buttons});}
svg.dispatchEvent(e('pointerdown',300,250,1)); window.dispatchEvent(e('pointermove',480,340,1)); window.dispatchEvent(e('pointerup',480,340,0));
"""); time.sleep(.3)
print('node css',d.execute_script("""
var n=document.querySelector('.alur-canvas-node'), b=document.querySelector('.alur-canvas-node .alur-node-box'), l=document.querySelector('.alur-canvas-node .alur-node-label');
return {nodeTransition:getComputedStyle(n).transitionDuration, nodeAnim:getComputedStyle(n).animationName, fill:getComputedStyle(b).fill, stroke:getComputedStyle(b).stroke, labelFont:getComputedStyle(l).fontFamily, labelSize:getComputedStyle(l).fontSize};
"""))
print('body font',d.execute_script("return getComputedStyle(document.body).fontFamily"))
print('label text',d.execute_script("var e=document.querySelector('.alur-canvas-node .alur-node-label'); return e ? e.textContent : 'none'"))
d.quit()
