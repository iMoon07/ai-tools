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
d.find_element(By.CSS_SELECTOR,'[data-tool="box"]').click(); drag(300,250,480,340)
print('tool after box',d.execute_script("return document.querySelector('#statusTool').textContent"))
print('selected',json.loads(d.execute_script("return document.getElementById('stage').getAttribute('data-spec')")).get('selected'))
d.find_element(By.CSS_SELECTOR,'[data-tool="arrow"]').click(); drag(250,400,650,400)
print('tool after arrow',d.execute_script("return document.querySelector('#statusTool').textContent"))
print('selectedEdge',json.loads(d.execute_script("return document.getElementById('stage').getAttribute('data-spec')")).get('selectedEdge'))
# shortcut card
d.find_element(By.ID,'helpBtn').click(); time.sleep(.2)
print('shortcut spans',len(d.find_elements(By.CSS_SELECTOR,'#shortcutCard span')))
print('shortcut text has sticky', 'sticky note' in d.find_element(By.ID,'shortcutCard').text)
d.quit()
