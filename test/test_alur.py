import time,json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
opts=Options(); opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-dev-shm-usage'); opts.add_argument('--window-size=390,844'); opts.binary_location='/usr/bin/chromium'; opts.set_capability('goog:loggingPrefs',{'browser':'ALL'})
d=webdriver.Chrome(options=opts, service=Service('/usr/bin/chromedriver'))
for w,h in [(390,844),(360,640),(500,757)]:
    d.set_window_size(w,h)
    d.get('http://localhost:8000/imoon07.github.io/alur.html'); time.sleep(1.6)
    print('size',w,h,'viewport',d.execute_script('return [innerWidth,innerHeight,document.body.scrollWidth,document.body.scrollHeight]'))
    print('counts',d.execute_script("return {nodes:document.querySelectorAll('.alur-canvas-node').length,edges:document.querySelectorAll('.alur-canvas-edge').length,heads:document.querySelectorAll('.alur-edge-head').length}"))
    fab=d.find_element(By.ID,'mobileFab')
    a=ActionChains(d); a.move_to_element(fab).click().perform(); time.sleep(.35)
    m=d.execute_script("var m=document.getElementById('mobileMenu');var r=m.getBoundingClientRect();return {hidden:m.hidden,display:getComputedStyle(m).display,x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom,scrollH:m.scrollHeight,clientH:m.clientHeight,win:[innerWidth,innerHeight],overflowX:m.scrollWidth>m.clientWidth}")
    print('menu',m)
    # click panels via JS to ensure handlers
    print('panel click',d.execute_script("document.querySelector('[data-mobile-panel=\"assets\"]').click(); return {assets:document.getElementById('panelAssets').classList.contains('is-open'),menuHidden:document.getElementById('mobileMenu').hidden}"))
    time.sleep(.3)
    print('assets rect',d.execute_script("var p=document.getElementById('panelAssets');var r=p.getBoundingClientRect();return {hidden:p.hidden,display:getComputedStyle(p).display,x:r.x,y:r.y,w:r.width,h:r.height,bottom:r.bottom,win:[innerWidth,innerHeight]}"))
    # close assets and open menu again
    d.execute_script("var b=document.querySelector('[data-close=\"assets\"]'); if(b)b.click(); document.getElementById('mobileFab').click();")
    time.sleep(.25)
    # drag n1 -> n3 arrow
    d.execute_script("document.querySelector('[data-mobile-tool=\"arrow\"]').click(); document.getElementById('mobileMenu').hidden=true;")
    time.sleep(.2)
    nodes=d.find_elements(By.CSS_SELECTOR,'.alur-canvas-node')
    a=ActionChains(d); a.move_to_element(nodes[0]).click_and_hold().move_by_offset(20,0).move_to_element(nodes[2]).release().perform(); time.sleep(.6)
    print('after arrow',d.execute_script("return {edges:document.querySelectorAll('.alur-canvas-edge').length,heads:document.querySelectorAll('.alur-edge-head').length}"))
    print('errors',[x for x in d.get_log('browser') if x['level']=='SEVERE' and 'favicon' not in x['message']])
# redirect
d.set_window_size(390,844)
d.get('http://localhost:8000/imoon07.github.io/preview.html'); time.sleep(.7)
print('redirect',d.current_url, d.execute_script('return document.title'))
d.quit()
