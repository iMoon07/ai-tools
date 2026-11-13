from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time,json
opts=Options(); opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-gpu'); opts.add_argument('--window-size=1440,900')
d=webdriver.Chrome(service=webdriver.chrome.service.Service('/usr/bin/chromedriver'),options=opts)
d.get('http://127.0.0.1:8000/imoon07.github.io/preview.html'); time.sleep(1)
d.execute_script("localStorage.removeItem('ruang.scene.v1')"); d.refresh(); time.sleep(.8)
d.find_element(By.CSS_SELECTOR,'[data-panel="assets"]').click(); time.sleep(.3)
# module flow
d.execute_script("var e=document.getElementById('module'); e.value='flow'; e.dispatchEvent(new Event('change',{bubbles:true}))"); time.sleep(.5)
print('module flow',d.execute_script("return document.getElementById('stage').getAttribute('data-module')"))
print('flow nodes',len(d.find_elements(By.CSS_SELECTOR,'.alur-canvas-node')))
# chart
d.execute_script("var e=document.getElementById('module'); e.value='chart'; e.dispatchEvent(new Event('change',{bubbles:true}))"); time.sleep(.5)
print('chart type visible',d.execute_script("return getComputedStyle(document.getElementById('chartTypeRow')).display"))
d.execute_script("var e=document.getElementById('chartType'); e.value='gauge'; e.dispatchEvent(new Event('change',{bubbles:true}))"); time.sleep(.4)
print('chart module',d.execute_script("return document.getElementById('stage').getAttribute('data-module')"))
# back canvas
d.execute_script("var e=document.getElementById('module'); e.value='canvas'; e.dispatchEvent(new Event('change',{bubbles:true}))"); time.sleep(.5)
print('canvas back',d.execute_script("return document.getElementById('stage').getAttribute('data-module')"))
# spec apply
d.execute_script("""
var t=document.getElementById('spec'); t.value=JSON.stringify({module:'canvas',nodes:{n1:{x:100,y:100,w:160,h:60,shape:'box',label:'A'}},edges:[],drawings:[]});
document.getElementById('apply').click();
"""); time.sleep(.5)
print('spec nodes',len(json.loads(d.execute_script("return document.getElementById('stage').getAttribute('data-spec')"))['nodes']))
print('errors?', 'Something went wrong' in d.page_source)
d.quit()
