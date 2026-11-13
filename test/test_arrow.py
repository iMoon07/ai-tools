import time,json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
opts=Options(); opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-dev-shm-usage'); opts.add_argument('--window-size=500,900'); opts.binary_location='/usr/bin/chromium'
d=webdriver.Chrome(options=opts, service=Service('/usr/bin/chromedriver'))
d.set_window_size(500,900)
d.get('http://localhost:8000/imoon07.github.io/preview.html'); time.sleep(2)
print('counts before', d.execute_script("return [document.querySelectorAll('.alur-canvas-node').length,document.querySelectorAll('.alur-canvas-edge').length]"))
nodes=d.find_elements(By.CSS_SELECTOR,'.alur-canvas-node')
print('nodes', [(n.get_attribute('data-node-id'), n.location, n.size) for n in nodes[:3]])
# use menu arrow tool
d.execute_script("document.getElementById('mobileFab').click()")
time.sleep(.3)
print('menu', d.execute_script("var m=document.getElementById('mobileMenu');var r=m.getBoundingClientRect();return {hidden:m.hidden,x:r.x,y:r.y,w:r.width,h:r.height,display:getComputedStyle(m).display}"))
d.execute_script("document.querySelector('[data-mobile-tool=\"arrow\"]').click()")
time.sleep(.3)
print('tool', d.execute_script("return document.getElementById('editorMode').textContent"))
nodes=d.find_elements(By.CSS_SELECTOR,'.alur-canvas-node')
a=ActionChains(d); a.move_to_element(nodes[0]).click_and_hold().move_to_element(nodes[1]).release().perform()
time.sleep(.7)
print('counts after', d.execute_script("return [document.querySelectorAll('.alur-canvas-node').length,document.querySelectorAll('.alur-canvas-edge').length]"))
print('edges', d.execute_script(r'''
const out=[];document.querySelectorAll('.alur-canvas-edge').forEach(p=>{const r=p.getBoundingClientRect();out.push({d:p.getAttribute('d'),x:r.x,y:r.y,w:r.width,h:r.height});});return out;
'''))
print('nodes2', d.execute_script(r'''
const out=[];document.querySelectorAll('.alur-canvas-node').forEach(n=>{const r=n.getBoundingClientRect();out.push({id:n.getAttribute('data-node-id'),x:r.x,y:r.y,w:r.width,h:r.height,cx:r.x+r.width/2,cy:r.y+r.height/2});});return out;
'''))
d.save_screenshot('/home/moon/Projects/ai-tools/renders/arrow-test.png')
d.quit()
