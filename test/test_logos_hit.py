import time,json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
opts=Options(); opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-dev-shm-usage'); opts.add_argument('--window-size=900,700'); opts.binary_location='/usr/bin/chromium'
d=webdriver.Chrome(options=opts, service=Service('/usr/bin/chromedriver')); d.set_window_size(900,700)
d.get('http://localhost:8000/imoon07.github.io/alur.html'); time.sleep(1.5)
spec={'module':'canvas','title':'logos','grid':True,'width':900,'height':520,'nodes':{
 'tools':{'x':100,'y':100,'w':220,'h':110,'shape':'box','label':'Tools','logos':['security:burp','security:distributor-logo-kali'],'color':'amber'},
 'circle':{'x':520,'y':100,'w':160,'h':160,'shape':'circle','label':'Circle','color':'cyan'},
 'diamond':{'x':160,'y':340,'w':180,'h':130,'shape':'diamond','label':'Diamond','color':'purple'},
 'pill':{'x':560,'y':340,'w':220,'h':90,'shape':'pill','label':'Pill','color':'green'}
},'edges':[]}
d.execute_script("document.getElementById('spec').value=arguments[0]; document.getElementById('apply').click();", json.dumps(spec))
time.sleep(1.2)
print('logos',d.execute_script(r'''
return [...document.querySelectorAll('.alur-logo-img')].map(i=>{const r=i.getBoundingClientRect();const x=r.x+r.width/2,y=r.y+r.height/2;const el=document.elementFromPoint(x,y);return {src:i.getAttribute('href')||i.getAttribute('src'),x:r.x,y:r.y,w:r.width,h:r.height,target:el?el.tagName:null,cls:el&&el.className.baseVal!==undefined?el.className.baseVal:el?el.className:null,anc:el&&el.closest?!!el.closest('.alur-canvas-node'):false};});
'''))
print('nodes',d.execute_script(r'''
return [...document.querySelectorAll('.alur-canvas-node')].map(n=>{const r=n.getBoundingClientRect();return {id:n.getAttribute('data-node-id'),x:r.x,y:r.y,w:r.width,h:r.height,cx:r.x+r.width/2,cy:r.y+r.height/2};});
'''))
# arrow from first logo center to circle center
logos=d.find_elements(By.CSS_SELECTOR,'.alur-logo-img')
print('logo count',len(logos))
d.execute_script("document.querySelector('[data-tool=\"arrow\"]').click()"); time.sleep(.2)
circle=d.find_element(By.CSS_SELECTOR,'[data-node-id="circle"]')
# drag from logo element (Selenium clicks center)
a=ActionChains(d); a.move_to_element(logos[0]).click_and_hold().move_by_offset(20,0).move_to_element(circle).release().perform(); time.sleep(.7)
print('edges',d.execute_script("return [...document.querySelectorAll('.alur-canvas-edge')].map(p=>p.getAttribute('d'))"))
print('heads',d.execute_script("return [...document.querySelectorAll('.alur-edge-head')].map(h=>{const r=h.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})"))
# line from second logo to diamond
logos=d.find_elements(By.CSS_SELECTOR,'.alur-logo-img'); diamond=d.find_element(By.CSS_SELECTOR,'[data-node-id="diamond"]')
d.execute_script("document.querySelector('[data-tool=\"line\"]').click()"); time.sleep(.2)
a=ActionChains(d); a.move_to_element(logos[1]).click_and_hold().move_by_offset(20,0).move_to_element(diamond).release().perform(); time.sleep(.7)
print('edges2',d.execute_script("return [...document.querySelectorAll('.alur-canvas-edge')].map(p=>p.getAttribute('d'))"))
d.quit()
