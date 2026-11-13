from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time,json
opts=Options(); opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-gpu'); opts.add_argument('--window-size=1440,900')
d=webdriver.Chrome(service=webdriver.chrome.service.Service('/usr/bin/chromedriver'),options=opts)
d.get('http://127.0.0.1:8000/imoon07.github.io/preview.html'); time.sleep(1)
d.execute_script("localStorage.removeItem('ruang.scene.v1')"); d.refresh(); time.sleep(.8)
# create box then apply logo via assets
d.find_element(By.CSS_SELECTOR,'[data-tool="box"]').click()
d.execute_script("""
var svg=document.querySelector('#stage svg');
function e(t,x,y,buttons){return new PointerEvent(t,{clientX:x,clientY:y,bubbles:true,cancelable:true,pointerId:1,pointerType:'mouse',button:0,buttons:buttons});}
svg.dispatchEvent(e('pointerdown',300,250,1)); window.dispatchEvent(e('pointermove',480,340,1)); window.dispatchEvent(e('pointerup',480,340,0));
"""); time.sleep(.4)
d.find_element(By.CSS_SELECTOR,'[data-panel="assets"]').click(); time.sleep(.3)
d.find_elements(By.CSS_SELECTOR,'.logo-tile')[0].click(); time.sleep(.4)
def logo_size():
 return d.execute_script("var i=document.querySelector('.alur-canvas-node .alur-logo-img'); return i ? [i.getAttribute('width'),i.getAttribute('x'),i.getAttribute('y')] : null")
print('logo size small',logo_size())
# resize node via SE handle
h=d.find_elements(By.CSS_SELECTOR,'.alur-handle')
print('handles',len(h))
if h:
 se=[x for x in h if x.get_attribute('data-handle')=='se'][0]
 from selenium.webdriver.common.action_chains import ActionChains
 a=ActionChains(d); a.click_and_hold(se).move_by_offset(120,80).release().perform(); time.sleep(.5)
 print('logo size big',logo_size())
print('node w',json.loads(d.execute_script("return document.getElementById('stage').getAttribute('data-spec')"))['nodes'])
print('asset tile border',d.execute_script("var e=document.querySelector('.logo-tile'); var s=getComputedStyle(e); return [s.borderTopWidth,s.backgroundImage,s.backgroundColor,s.boxShadow]"))
d.quit()
