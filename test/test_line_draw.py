import time,json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
opts=Options(); opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-dev-shm-usage'); opts.add_argument('--window-size=900,700'); opts.binary_location='/usr/bin/chromium'
d=webdriver.Chrome(options=opts, service=Service('/usr/bin/chromedriver')); d.set_window_size(900,700)
d.get('http://localhost:8000/imoon07.github.io/draw.html'); time.sleep(1.2)
spec={'module':'canvas','title':'shapes','grid':True,'width':900,'height':520,'nodes':{
 'box':{'x':60,'y':60,'w':180,'h':90,'shape':'box','label':'Box','logos':['security:burp','security:distributor-logo-kali']},
 'circle':{'x':340,'y':60,'w':140,'h':140,'shape':'circle','label':'Circle'},
 'diamond':{'x':600,'y':60,'w':170,'h':120,'shape':'diamond','label':'Diamond'},
 'pill':{'x':120,'y':330,'w':200,'h':80,'shape':'pill','label':'Pill'},
 'round':{'x':420,'y':330,'w':180,'h':90,'shape':'box','edge':'round','label':'Round'}
},'edges':[]}
d.execute_script("document.getElementById('spec').value=arguments[0]; document.getElementById('apply').click();", json.dumps(spec)); time.sleep(1.2)
for a,b in [('box','circle'),('circle','diamond'),('diamond','pill'),('pill','round'),('round','box')]:
    d.execute_script("document.querySelector('[data-tool=\"line\"]').click()"); time.sleep(.25)
    na=d.find_element(By.CSS_SELECTOR,'[data-node-id="'+a+'"]'); nb=d.find_element(By.CSS_SELECTOR,'[data-node-id="'+b+'"]')
    before=d.execute_script("return document.querySelectorAll('.alur-canvas-edge').length")
    ac=ActionChains(d); ac.move_to_element(na).click_and_hold().move_by_offset(15,0).move_to_element(nb).release().perform(); time.sleep(.55)
    after=d.execute_script("return document.querySelectorAll('.alur-canvas-edge').length")
    print(a,'->',b,before,'->',after)
print('heads',d.execute_script("return document.querySelectorAll('.alur-edge-head').length"))
print('paths',d.execute_script("return [...document.querySelectorAll('.alur-canvas-edge')].map(p=>p.getAttribute('d'))"))
d.quit()
