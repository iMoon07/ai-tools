#!/usr/bin/env python3
"""Verify that a touch swipe scrolls a nested list on a phone-sized viewport.

Written for the draw.html logo grid: a tile fills its grid cell, so
`touch-action: none` made every swipe start a drag instead of a scroll. This
drives Chromium over CDP with emulated touch, swipes over a target element, and
reports the scrollTop delta. Pass --control to re-apply the old rule inline and
prove the difference (A/B).

Usage:
  python3 ai-tools/verify/mobile_touch_scroll.py \
      --url http://localhost:8000/draw.html \
      --open ".mobile-fab,[data-mobile-panel='assets']" \
      --target "#logoGrid"

Chromium must be on PATH. Requires: websocket-client.
"""
import argparse
import json
import subprocess
import time
import urllib.parse
import urllib.request

import websocket

CHROME = 'chromium'


def http(port, path, method='GET'):
    req = urllib.request.Request(f'http://127.0.0.1:{port}{path}', method=method)
    return json.loads(urllib.request.urlopen(req, timeout=10).read())


class Cdp:
    def __init__(self, port, url):
        self.ws = None
        self.proc = subprocess.Popen(
            [CHROME, '--headless=new', f'--remote-debugging-port={port}',
             f'--user-data-dir=/tmp/kilo/mob/prof-{port}', '--no-first-run',
             '--no-default-browser-check', '--disable-gpu', '--window-size=390,844',
             '--remote-allow-origins=*', 'about:blank'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(60):
            try:
                http(port, '/json/version')
                break
            except Exception:
                time.sleep(0.3)
        target = http(port, '/json/new?' + urllib.parse.quote(url, safe=''), 'PUT')
        self.ws = websocket.create_connection(target['webSocketDebuggerUrl'],
                                              timeout=30, suppress_origin=True)
        self.n = 0
        self.send('Page.enable')
        self.send('Runtime.enable')

    def send(self, method, **params):
        self.n += 1
        self.ws.send(json.dumps({'id': self.n, 'method': method, 'params': params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get('id') == self.n:
                if 'error' in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get('result', {})

    def ev(self, expr):
        r = self.send('Runtime.evaluate', expression=expr, returnByValue=True)
        return r.get('result', {}).get('value')

    def close(self):
        try:
            self.ws.close()
        finally:
            self.proc.terminate()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--url', default='http://localhost:8000/draw.html')
    ap.add_argument('--target', default='#logoGrid', help='scroller to swipe over')
    ap.add_argument('--open', default='', help='comma-separated click sequence')
    ap.add_argument('--width', type=int, default=390)
    ap.add_argument('--height', type=int, default=844)
    ap.add_argument('--control', action='store_true',
                    help='also swipe with touch-action:none restored (expect no scroll)')
    ap.add_argument('--port', type=int, default=9336)
    a = ap.parse_args()

    c = Cdp(a.port, a.url)
    try:
        c.send('Emulation.setDeviceMetricsOverride', width=a.width, height=a.height,
               deviceScaleFactor=2, mobile=True)
        c.send('Emulation.setTouchEmulationEnabled', enabled=True, maxTouchPoints=5)
        c.send('Page.navigate', url=a.url)
        time.sleep(2.5)
        for sel in [s for s in a.open.split(',') if s]:
            c.ev(f'document.querySelector({json.dumps(sel)}).click()')
            time.sleep(0.6)

        read = (f'JSON.stringify((()=>{{const e=document.querySelector({json.dumps(a.target)});'
                f'return {{top:e.scrollTop,sh:e.scrollHeight,ch:e.clientHeight,'
                f'touch:getComputedStyle(e).touchAction}};}})())')
        print('before ', c.ev(read))

        box = json.loads(c.ev(
            f'JSON.stringify((()=>{{const r=document.querySelector({json.dumps(a.target)})'
            '.getBoundingClientRect();return {x:Math.round(r.left+r.width/2),'
            'y:Math.round(r.top+r.height*0.6)};})())'))
        if not (0 < box['y'] < a.height):
            c.ev(f'document.querySelector({json.dumps(a.target)}).scrollIntoView({{block:"center"}})')
            time.sleep(0.5)
            box = json.loads(c.ev(
                f'JSON.stringify((()=>{{const r=document.querySelector({json.dumps(a.target)})'
                '.getBoundingClientRect();return {x:Math.round(r.left+r.width/2),'
                'y:Math.round(r.top+r.height*0.6)};})())'))

        def swipe(label):
            c.send('Input.dispatchTouchEvent', type='touchStart',
                   touchPoints=[{'x': box['x'], 'y': box['y'], 'id': 1}])
            for i in range(1, 10):
                c.send('Input.dispatchTouchEvent', type='touchMove',
                       touchPoints=[{'x': box['x'], 'y': box['y'] - i * 18, 'id': 1}])
                time.sleep(0.02)
            c.send('Input.dispatchTouchEvent', type='touchEnd', touchPoints=[])
            time.sleep(0.8)
            print(label, c.ev(read))

        if a.control:
            c.ev(f'document.querySelectorAll({json.dumps(a.target + " *")})'
                 '.forEach(t=>t.style.touchAction="none")')
            c.ev(f'document.querySelector({json.dumps(a.target)}).scrollTop=0')
            time.sleep(0.3)
            swipe('old none')
            c.ev(f'document.querySelectorAll({json.dumps(a.target + " *")})'
                 '.forEach(t=>t.style.touchAction="")')
            c.ev(f'document.querySelector({json.dumps(a.target)}).scrollTop=0')
            time.sleep(0.3)
        swipe('new    ')
    finally:
        c.close()


if __name__ == '__main__':
    main()