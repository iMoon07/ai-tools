import json, time, urllib.request, subprocess, tempfile
import websocket
exec(open('mobaudit.py').read().split("AUDIT =")[0])
ev("""(function(){Array.prototype.forEach.call(document.querySelectorAll('.dock'),function(d){d.hidden=false; d.classList.add('is-open');});})()""")
time.sleep(0.6)
print('dark body:', ev("document.body.className"))
print('tab bar bg:', ev("(function(){var e=document.querySelector('.mobile-tabs-bar'); return e?getComputedStyle(e).backgroundColor:null;})()"))
print('field bg:', ev("(function(){var e=document.querySelector('.dock input'); return e?getComputedStyle(e).backgroundColor:null;})()"))
print('head bg:', ev("(function(){var e=document.querySelector('.shape-head'); return e?getComputedStyle(e).backgroundColor:null;})()"))
c.close(); proc.terminate()
