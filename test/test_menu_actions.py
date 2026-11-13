import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
opts=Options(); opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-dev-shm-usage'); opts.add_argument('--window-size=390,844'); opts.binary_location='/usr/bin/chromium'; opts.set_capability('goog:loggingPrefs',{'browser':'ALL'})
d=webdriver.Chrome(options=opts, service=Service('/usr/bin/chromedriver')); d.set_window_size(390,844)
d.get('http://localhost:8000/imoon07.github.io/alur.html'); time.sleep(1.5)
def open_menu():
    d.execute_script("var f=document.getElementById('mobileFab'); if(document.getElementById('mobileMenu').hidden){var r=f.getBoundingClientRect(); f.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,clientX:r.x+r.width/2,clientY:r.y+r.height/2,pointerId:1,pointerType:'touch',isPrimary:true,button:0,buttons:1})); f.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,clientX:r.x+r.width/2,clientY:r.y+r.height/2,pointerId:1,pointerType:'touch',isPrimary:true,button:0,buttons:0}));}")
    time.sleep(.25)
def click(sel):
    d.execute_script("document.querySelector(arguments[0]).click()", sel); time.sleep(.3)
open_menu(); print('menu open',d.execute_script("return !document.getElementById('mobileMenu').hidden"))
click('[data-mobile-panel="layers"]'); print('layers',d.execute_script("return {open:document.getElementById('panelLayers').classList.contains('is-open'),hidden:document.getElementById('panelLayers').hidden}"))
open_menu(); click('[data-mobile-panel="properties"]'); print('properties',d.execute_script("return {shapeHidden:document.getElementById('shapePanel').hidden,title:document.getElementById('shapePanelTitle').textContent}"))
open_menu(); click('[data-mobile-panel="shortcuts"]'); print('shortcuts',d.execute_script("return {hidden:document.getElementById('shortcutCard').hidden}"))
open_menu(); click('[data-mobile-action="zoom-in"]'); print('zoom',d.execute_script("return document.getElementById('zoomVal').textContent"))
open_menu(); click('[data-mobile-action="undo"]'); print('undo ok')
open_menu(); print('site links',d.execute_script("return [...document.querySelectorAll('.mobile-site-links a')].map(a=>a.getAttribute('href'))"))
print('errors',[x for x in d.get_log('browser') if x['level']=='SEVERE' and 'favicon' not in x['message']])
d.save_screenshot('/home/moon/Projects/ai-tools/renders/menu-actions.png')
d.quit()
