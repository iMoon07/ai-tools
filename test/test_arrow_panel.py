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
"""); time.sleep(.4)
print('edge panel visible',d.execute_script("return !document.getElementById('shapePanel').hidden"))
print('title',d.execute_script("return document.getElementById('shapePanelTitle').textContent"))
print('labels',d.execute_script("return Array.from(document.querySelectorAll('#shapePanelBody .shape-label')).map(function(e){return e.textContent})"))
print('heads',len(d.find_elements(By.CSS_SELECTOR,'.alur-edge-head')))
# toggle start
d.execute_script("""
var labels=document.querySelectorAll('#shapePanelBody .shape-label'); var g;
for (var i=0;i<labels.length;i++) { if (labels[i].textContent === 'Arrow heads') { g=labels[i].parentNode; break; } }
var checks=g.querySelectorAll('input[type=checkbox]'); checks[0].click();
"""); time.sleep(.4)
print('heads after start',len(d.find_elements(By.CSS_SELECTOR,'.alur-edge-head')))
s=json.loads(d.execute_script("return document.getElementById('stage').getAttribute('data-spec')"))
print('edge props', {k:s['edges'][0].get(k) for k in ['arrowStart','arrowEnd','arrowType','curved']})
# type triangle
d.execute_script("""
var ss=document.querySelectorAll('#shapePanelBody select'); var e=ss[ss.length-1]; e.value='triangle'; e.dispatchEvent(new Event('change',{bubbles:true}));
"""); time.sleep(.4)
print('heads triangle',len(d.find_elements(By.CSS_SELECTOR,'.alur-edge-head')))
d.quit()
