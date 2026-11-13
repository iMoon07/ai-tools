import time,json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
opts=Options(); opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-dev-shm-usage'); opts.add_argument('--window-size=900,700'); opts.binary_location='/usr/bin/chromium'; opts.set_capability('goog:loggingPrefs',{'browser':'ALL'})
d=webdriver.Chrome(options=opts, service=Service('/usr/bin/chromedriver')); d.set_window_size(900,700)
d.get('http://localhost:8000/imoon07.github.io/alur.html'); time.sleep(1.5)
spec={
 'module':'canvas','title':'shapes','grid':True,'width':900,'height':520,
 'nodes':{
  'burp':{'x':80,'y':80,'w':220,'h':110,'shape':'box','label':'Burp','logos':['security:burp','security:kali'],'color':'amber'},
  'circle':{'x':480,'y':80,'w':160,'h':160,'shape':'circle','label':'Circle','color':'cyan'},
  'diamond':{'x':120,'y':330,'w':180,'h':130,'shape':'diamond','label':'Diamond','color':'purple'},
  'pill':{'x':520,'y':330,'w':220,'h':90,'shape':'pill','label':'Pill','color':'green'}
 },
 'edges':[]
}
d.execute_script("document.getElementById('spec').value=arguments[0]; document.getElementById('apply').click();", json.dumps(spec))
time.sleep(1.2)
print('nodes',d.execute_script("return [...document.querySelectorAll('.alur-canvas-node')].map(n=>{const r=n.getBoundingClientRect();return {id:n.getAttribute('data-node-id'),x:r.x,y:r.y,w:r.width,h:r.height,cx:r.x+r.width/2,cy:r.y+r.height/2}})"))
print('logos',d.execute_script("return [...document.querySelectorAll('.alur-logo-img')].map(i=>{const r=i.getBoundingClientRect();return {src:i.getAttribute('src'),x:r.x,y:r.y,w:r.width,h:r.height}})"))
# set arrow tool
d.execute_script("document.querySelector('[data-tool=\"arrow\"]').click()"); time.sleep(.2)
# drag from burp center (logo) to circle center
nodes=d.find_elements(By.CSS_SELECTOR,'.alur-canvas-node')
print('node ids',[n.get_attribute('data-node-id') for n in nodes])
a=ActionChains(d); a.move_to_element(nodes[0]).click_and_hold().move_by_offset(20,0).move_to_element(nodes[1]).release().perform(); time.sleep(.7)
print('edges',d.execute_script("return [...document.querySelectorAll('.alur-canvas-edge')].map(p=>p.getAttribute('d'))"))
print('heads',d.execute_script("return [...document.querySelectorAll('.alur-edge-head')].map(h=>{const r=h.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})"))
# drag circle to diamond
nodes=d.find_elements(By.CSS_SELECTOR,'.alur-canvas-node')
a=ActionChains(d); a.move_to_element(nodes[1]).click_and_hold().move_by_offset(20,0).move_to_element(nodes[2]).release().perform(); time.sleep(.7)
print('edges2',d.execute_script("return [...document.querySelectorAll('.alur-canvas-edge')].map(p=>p.getAttribute('d'))"))
print('errors',[x for x in d.get_log('browser') if x['level']=='SEVERE' and 'favicon' not in x['message']])
d.save_screenshot('/home/moon/Projects/ai-tools/renders/shapes-arrows.png')
d.quit()
