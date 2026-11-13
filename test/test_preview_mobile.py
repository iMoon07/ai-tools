import json, sys, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

opts=Options()
opts.add_argument('--headless=new')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--window-size=500,900')
opts.set_capability('goog:loggingPrefs', {'browser':'ALL'})
opts.binary_location='/usr/bin/chromium'
d=webdriver.Chrome(options=opts, service=Service('/usr/bin/chromedriver'))
d.set_window_size(500,900)
d.get('http://localhost:8000/imoon07.github.io/preview.html')
time.sleep(2)
errs=[]
d.get_log('browser') if False else None
# collect console errors via JS
errs=d.execute_script("return (window.__errs||[])")
print('viewport',d.execute_script('return [innerWidth,innerHeight,document.body.scrollWidth,document.body.scrollHeight]'))
print('canvas-mode',d.execute_script("return document.body.classList.contains('canvas-mode')"))
fab=d.find_element(By.ID,'mobileFab')
print('fab',d.execute_script("var e=arguments[0];var r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,display:getComputedStyle(e).display};",fab))
# drag FAB
start=d.execute_script("var e=arguments[0];var r=e.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2];",fab)
a=ActionChains(d); a.move_to_element_with_offset(fab, start[0]-fab.location['x']-fab.size['width']/2, start[1]-fab.location['y']-fab.size['height']/2).click_and_hold().move_by_offset(-100,-150).release().perform()
time.sleep(.4)
pos=d.execute_script("var e=document.getElementById('mobileFab');var r=e.getBoundingClientRect();return [r.x,r.y];")
print('fab after drag',pos)
# tap FAB center to open
a=ActionChains(d); a.move_to_element_with_offset(fab, 0, 0).click().perform()
time.sleep(.4)
print('menu',d.execute_script("var m=document.getElementById('mobileMenu');var r=m.getBoundingClientRect();return {hidden:m.hidden,x:r.x,y:r.y,w:r.width,h:r.height,scrollH:m.scrollHeight,clientH:m.clientHeight,win:[innerWidth,innerHeight]};"))
# click arrow tool
d.execute_script("document.querySelector('[data-mobile-tool=\\\"arrow\\\"]').click()")
time.sleep(.3)
print('tool',d.execute_script("return document.getElementById('editorMode').textContent"))
# close menu
d.execute_script("document.getElementById('mobileMenuClose').click()")
time.sleep(.2)
# draw arrow between n1 and n2 using pointer events via JS
res=d.execute_script(r'''
const n1=document.querySelector('[data-node="n1"]')||document.querySelector('.alur-canvas-node');
const nodes=[...document.querySelectorAll('.alur-canvas-node')];
function rect(el){const r=el.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,cx:r.x+r.width/2,cy:r.y+r.height/2};}
const a=rect(nodes[0]), b=rect(nodes[1]);
const svg=document.querySelector('#stage svg');
function ev(type,x,y){return new PointerEvent(type,{bubbles:true,cancelable:true,clientX:x,clientY:y,pointerId:1,pointerType:'touch',isPrimary:true,button:0,buttons:type==='pointerup'?0:1});}
a.cx; a.cy;
svg.dispatchEvent(ev('pointerdown',a.cx,a.cy));
svg.dispatchEvent(ev('pointermove',a.cx+10,a.cy+10));
svg.dispatchEvent(ev('pointermove',b.cx,b.cy));
svg.dispatchEvent(ev('pointerup',b.cx,b.cy));
return {a,b,nodes:nodes.length};
''')
print('drag',res)
time.sleep(.6)
# inspect edge path and node rects
edge=d.execute_script(r'''
const nodes=[...document.querySelectorAll('.alur-canvas-node')].slice(0,2).map(n=>{const r=n.getBoundingClientRect();return {id:n.dataset.node,x:r.x,y:r.y,w:r.width,h:r.height,cx:r.x+r.width/2,cy:r.y+r.height/2};});
const paths=[...document.querySelectorAll('.alur-canvas-edge')].map(p=>{const r=p.getBoundingClientRect();return {cls:p.getAttribute('class'),d:p.getAttribute('d'),x:r.x,y:r.y,w:r.width,h:r.height};});
const heads=[...document.querySelectorAll('.alur-edge-head')].map(h=>{const r=h.getBoundingClientRect();return {op:h.style.opacity,x:r.x,y:r.y,w:r.width,h:r.height};});
return {nodes,paths,heads};
''')
print('edge',json.dumps(edge,indent=2)[:4000])
# compact flow test
flow=d.execute_script(r'''
const spec={module:'flow',title:'compact',columns:[['a'],['b'],['c']],nodes:{a:{label:'A'},b:{label:'B'},c:{label:'C'}},edges:[['a','b','TLS'],['b','c']]};
const host=document.createElement('div');host.className='alur';host.setAttribute('data-module','flow');host.setAttribute('data-spec',JSON.stringify(spec));host.style.position='fixed';host.style.left='-2000px';host.style.width='900px';host.style.height='440px';document.body.appendChild(host);Alur.init(host);const svg=host.querySelector('.alur-svg');return {err:!!host.querySelector('.alur-error'),svg:!!svg,paths:svg?svg.querySelectorAll('path').length:0};
''')
print('flow',flow); print('flow html', d.execute_script("var h=document.querySelector('div[style*=\\\"-2000px\\\"]'); return h?h.outerHTML.slice(0,500):'none'")); print('logs', d.get_log('browser'))
d.save_screenshot('/home/moon/Projects/ai-tools/browser/mobile-after.png')
d.quit()
