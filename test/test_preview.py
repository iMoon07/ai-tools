from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import json, time, sys

opts=Options()
opts.add_argument('--headless=new')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-gpu')
opts.add_argument('--window-size=1440,900')
d=webdriver.Chrome(service=webdriver.chrome.service.Service('/usr/bin/chromedriver'), options=opts)
d.get('http://127.0.0.1:8000/imoon07.github.io/preview.html')
time.sleep(1.2)
print('title', d.title)
print('errors?', 'Something went wrong' in d.page_source)
print('tool count', len(d.find_elements(By.CSS_SELECTOR,'#editorBar [data-tool]')))
print('panelScene exists', len(d.find_elements(By.ID,'panelScene')))
print('sceneSection exists', len(d.find_elements(By.ID,'sceneSection')))
print('target meta visible', d.execute_script("var e=document.getElementById('logoMeta'); return e ? getComputedStyle(e).display : 'missing'"))
print('properties hidden', d.execute_script("var e=document.getElementById('panelProperties'); return e ? getComputedStyle(e).display : 'missing'"))
print('logo tile bg', d.execute_script("var e=document.querySelector('.logo-tile'); return e ? getComputedStyle(e).backgroundColor : 'none'"))

def spec():
    return json.loads(d.execute_script("return document.getElementById('stage').getAttribute('data-spec')"))

def tool(name):
    d.find_element(By.CSS_SELECTOR,f'[data-tool="{name}"]').click()
    time.sleep(.1)

def drag(x1,y1,x2,y2):
    d.execute_script("""
      var svg=document.querySelector('#stage svg');
      function e(t,x,y,buttons){return new PointerEvent(t,{clientX:x,clientY:y,bubbles:true,cancelable:true,pointerId:1,pointerType:'mouse',button:0,buttons:buttons});}
      svg.dispatchEvent(e('pointerdown',arguments[0],arguments[1],1));
      window.dispatchEvent(e('pointermove',arguments[2],arguments[3],1));
      window.dispatchEvent(e('pointerup',arguments[2],arguments[3],0));
    """, x1,y1,x2,y2)
    time.sleep(.25)

# clear local scene to empty canvas
d.execute_script("localStorage.removeItem('ruang.scene.v1')")
d.refresh(); time.sleep(.8)

tool('box'); drag(300,250,480,340)
s=spec(); print('box nodes', len(s.get('nodes',{})), 'label', list(s.get('nodes',{}).values())[0].get('label') if s.get('nodes') else None)
print('box fill', d.execute_script("var e=document.querySelector('.alur-canvas-node .alur-node-box'); return e ? getComputedStyle(e).fill : 'none'"))

tool('diamond'); drag(600,250,720,340)
s=spec(); print('diamond nodes', len(s.get('nodes',{})))

tool('arrow'); drag(300,400,600,400)
s=spec(); print('edges', len(s.get('edges',[])), 'free', bool(s.get('edges',[{}])[0].get('points')) if s.get('edges') else False)
print('edge points', len(d.find_elements(By.CSS_SELECTOR,'.alur-edge-point')))

# drag first point
pts=d.find_elements(By.CSS_SELECTOR,'.alur-edge-point')
if pts:
    a=ActionChains(d); a.click_and_hold(pts[0]).move_by_offset(20,30).release().perform(); time.sleep(.3)
    s=spec(); print('after point drag', s['edges'][0]['points'])

tool('laser'); drag(700,450,850,500)
print('laser paths', len(d.find_elements(By.CSS_SELECTOR,'.alur-laser')))

# text dblclick
tool('select')
n=d.find_elements(By.CSS_SELECTOR,'.alur-canvas-node')
if n:
    a=ActionChains(d); a.double_click(n[0]).perform(); time.sleep(.2)
    print('inline text visible', d.execute_script("var e=document.getElementById('inlineText'); return e && getComputedStyle(e).display !== 'none'"))
    d.execute_script("var e=document.getElementById('inlineText'); e.value='Hello'; e.dispatchEvent(new Event('input',{bubbles:true}))")
    d.find_element(By.ID,'inlineText').send_keys('\n') if False else None
    d.execute_script("document.getElementById('inlineText').dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}))")
    time.sleep(.4)
    print('label after text', list(spec().get('nodes',{}).values())[0].get('label'))

# eraser
tool('eraser'); drag(300,250,480,340)
print('nodes after eraser', len(spec().get('nodes',{})))

# ctrl+a
tool('select'); d.find_element(By.TAG_NAME,'body').send_keys('\ue009' if False else '')
# use ActionChains ctrl+a
d.execute_script("document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'a',ctrlKey:true,bubbles:true}))"); time.sleep(.2)
print('selected', spec().get('selected'))
print('console ok')
d.quit()
