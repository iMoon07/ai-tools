from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time,json
opts=Options(); opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-gpu'); opts.add_argument('--window-size=1440,900')
d=webdriver.Chrome(service=webdriver.chrome.service.Service('/usr/bin/chromedriver'),options=opts)
d.get('http://127.0.0.1:8000/imoon07.github.io/preview.html'); time.sleep(1)
d.execute_script("localStorage.removeItem('ruang.scene.v1')"); d.refresh(); time.sleep(.8)
# open assets
d.find_element(By.CSS_SELECTOR,'[data-panel="assets"]').click(); time.sleep(.3)
print('assets open',d.execute_script("return document.getElementById('panelAssets').classList.contains('is-open')"))
print('scene section',d.execute_script("return !!document.getElementById('sceneSection')"))
print('grid visible',d.execute_script("var e=document.getElementById('gridToggle'); return e ? [e.offsetParent!==null, e.checked] : 'missing'"))
# click first logo
d.find_elements(By.CSS_SELECTOR,'.logo-tile')[0].click(); time.sleep(.4)
s=json.loads(d.execute_script("return document.getElementById('stage').getAttribute('data-spec')"))
print('nodes after logo',len(s.get('nodes',{})),'logo',list(s.get('nodes',{}).values())[0].get('logo') if s.get('nodes') else None)
print('logo tile in node',d.execute_script("var e=document.querySelector('.alur-canvas-node .alur-logo-tile'); return e ? getComputedStyle(e).display : 'none'"))
print('node label',list(s.get('nodes',{}).values())[0].get('label'))
# export buttons exist
for i in ['exportJson','exportSvg','apply','reset','surprise','spec']:
    print(i, len(d.find_elements(By.ID,i)))
d.quit()
