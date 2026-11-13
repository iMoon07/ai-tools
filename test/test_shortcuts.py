from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time,json
opts=Options(); opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-gpu'); opts.add_argument('--window-size=1440,900')
d=webdriver.Chrome(service=webdriver.chrome.service.Service('/usr/bin/chromedriver'),options=opts)
d.get('http://127.0.0.1:8000/imoon07.github.io/preview.html'); time.sleep(1)
d.execute_script("localStorage.removeItem('ruang.scene.v1')"); d.refresh(); time.sleep(.8)
def key(k, **mods):
 d.execute_script("""
 var o={key:arguments[0],bubbles:true,cancelable:true}; for (var k in arguments[1]) o[k]=arguments[1][k]; document.body.dispatchEvent(new KeyboardEvent('keydown',o));
 """, k, mods)
def spec(): return json.loads(d.execute_script("return document.getElementById('stage').getAttribute('data-spec')"))
# box and select via N? create box
d.find_element(By.CSS_SELECTOR,'[data-tool="box"]').click()
d.execute_script("""
var svg=document.querySelector('#stage svg');
function e(t,x,y,buttons){return new PointerEvent(t,{clientX:x,clientY:y,bubbles:true,cancelable:true,pointerId:1,pointerType:'mouse',button:0,buttons:buttons});}
svg.dispatchEvent(e('pointerdown',300,250,1)); window.dispatchEvent(e('pointermove',480,340,1)); window.dispatchEvent(e('pointerup',480,340,0));
"""); time.sleep(.4)
print('shape before',list(spec()['nodes'].values())[0].get('shape'))
key('Tab'); time.sleep(.3)
print('shape after tab',list(spec()['nodes'].values())[0].get('shape'))
key("'"); time.sleep(.2); print('grid',spec().get('grid'))
key('z', altKey=True); time.sleep(.2); print('view mode',d.execute_script("return document.body.classList.contains('view-mode')"))
key('z', altKey=True); time.sleep(.2)
key('r', altKey=True); time.sleep(.2); print('view mode2',d.execute_script("return document.body.classList.contains('view-mode')"))
key('r', altKey=True); time.sleep(.2)
key('d', altKey=True, shiftKey=True); time.sleep(.2); print('theme',d.execute_script("return document.body.classList.contains('light-theme')"))
key('d', altKey=True, shiftKey=True); time.sleep(.2)
# N creates plain text and inline edit
key('n'); time.sleep(.4)
print('nodes after n',len(spec()['nodes']),'inline',d.execute_script("var e=document.getElementById('inlineText'); return e && getComputedStyle(e).display !== 'none'"))
d.execute_script("document.getElementById('inlineText').dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))")
d.quit()
