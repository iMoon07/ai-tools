import time,json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
opts=Options(); opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-dev-shm-usage'); opts.add_argument('--window-size=500,900'); opts.add_argument('--force-device-scale-factor=1'); opts.binary_location='/usr/bin/chromium'; opts.set_capability('goog:loggingPrefs',{'browser':'ALL'})
d=webdriver.Chrome(options=opts, service=Service('/usr/bin/chromedriver')); d.set_window_size(500,900)
d.get('http://localhost:8000/imoon07.github.io/preview.html'); time.sleep(2)
print('viewport',d.execute_script('return [innerWidth,innerHeight,document.body.scrollWidth,document.body.scrollHeight]'))
print('counts',d.execute_script("return {nodes:document.querySelectorAll('.alur-canvas-node').length,edges:document.querySelectorAll('.alur-canvas-edge').length,heads:document.querySelectorAll('.alur-edge-head').length}"))
# open menu
fab=d.find_element(By.ID,'mobileFab')
a=ActionChains(d); a.move_to_element(fab).click().perform(); time.sleep(.4)
print('menu',d.execute_script("var m=document.getElementById('mobileMenu');var r=m.getBoundingClientRect();return {hidden:m.hidden,display:getComputedStyle(m).display,x:r.x,y:r.y,w:r.width,h:r.height,scrollH:m.scrollHeight,clientH:m.clientHeight,win:[innerWidth,innerHeight]}"))
print('menu items',d.execute_script("return [document.querySelectorAll('[data-mobile-tool]').length,document.querySelectorAll('[data-mobile-panel]').length,document.querySelectorAll('[data-mobile-action]').length,document.querySelectorAll('.mobile-site-links a').length]"))
# click arrow item
d.find_element(By.CSS_SELECTOR,'[data-mobile-tool="arrow"]').click(); time.sleep(.3)
print('tool',d.execute_script("return document.getElementById('editorMode').textContent"))
# drag n1 to n3 (new edge)
nodes=d.find_elements(By.CSS_SELECTOR,'.alur-canvas-node')
a=ActionChains(d); a.move_to_element(nodes[0]).click_and_hold().move_by_offset(20,0).move_to_element(nodes[2]).release().perform(); time.sleep(.7)
print('after connect',d.execute_script("return {edges:document.querySelectorAll('.alur-canvas-edge').length,heads:document.querySelectorAll('.alur-edge-head').length}"))
print('edges',d.execute_script("return [...document.querySelectorAll('.alur-canvas-edge')].map(p=>p.getAttribute('d'))"))
print('heads',d.execute_script("return [...document.querySelectorAll('.alur-edge-head')].map(h=>{const r=h.getBoundingClientRect();return {op:h.style.opacity,x:r.x,y:r.y,w:r.width,h:r.height}})"))
# switch select, drag n1 by 50,30
d.execute_script("document.querySelector('[data-tool=\"select\"]').click()"); time.sleep(.2)
n1=d.find_element(By.CSS_SELECTOR,'[data-node-id="n1"]')
before=d.execute_script("return [...document.querySelectorAll('.alur-canvas-edge')].map(p=>p.getAttribute('d'))")
a=ActionChains(d); a.move_to_element(n1).click_and_hold().move_by_offset(50,30).release().perform(); time.sleep(.7)
print('n1 rect after', d.execute_script("var n=document.querySelector('[data-node-id=\\\"n1\\\"]');var r=n.getBoundingClientRect();return [r.x,r.y,r.width,r.height]"))
print('edges after drag',d.execute_script("return [...document.querySelectorAll('.alur-canvas-edge')].map(p=>p.getAttribute('d'))"))
print('heads after drag',d.execute_script("return [...document.querySelectorAll('.alur-edge-head')].map(h=>{const r=h.getBoundingClientRect();return {op:h.style.opacity,x:r.x,y:r.y,w:r.width,h:r.height}})"))
print('body overflow',d.execute_script("return {sw:document.body.scrollWidth,cw:document.body.clientWidth,sh:document.body.scrollHeight,ch:document.body.clientHeight}"))
d.save_screenshot('/home/moon/Projects/ai-tools/js-extracts/preview-mobile-final.png')
print('logs',[x for x in d.get_log('browser') if x['level']=='SEVERE'])
d.quit()
