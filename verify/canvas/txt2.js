(async function () {
  var wait = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
  function pe(t, cx, cy, b) {
    return new PointerEvent(t, { bubbles: true, cancelable: true, clientX: cx, clientY: cy,
      button: 0, buttons: b, pointerId: 1, pointerType: 'mouse', isPrimary: true });
  }
  var out = {};
  document.querySelector('[data-tool="text"]').click();
  await wait(120);
  var st = document.getElementById('stage');
  var r = st.getBoundingClientRect();
  var x = Math.round(r.left + 300), y = Math.round(r.top + 400);
  var el = document.elementFromPoint(x, y);
  out.target = el ? el.tagName + '.' + (el.getAttribute('class') || '') : 'none';
  el.dispatchEvent(pe('pointerdown', x, y, 1));
  document.dispatchEvent(pe('pointermove', x, y, 1));
  document.dispatchEvent(pe('pointerup', x, y, 0));
  await wait(200);
  var area = document.getElementById('inlineText');
  out.editorOpen = !!(area && area.style.display !== 'none');
  if (area) {
    area.value = 'hello\nworld';
    area.dispatchEvent(new Event('input', { bubbles: true }));
    await wait(80);
    area.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
    await wait(200);
  }
  out.nodes = Array.prototype.map.call(document.querySelectorAll('.alur-canvas-node'),
    function (e) { return e.getAttribute('data-node-id') + ':' + (e.getAttribute('transform') || ''); });
  out.texts = Array.prototype.map.call(document.querySelectorAll('.alur-node-label'),
    function (t) { return t.textContent; });
  out.decoration = (function () { var l = document.querySelector('.alur-node-label'); return l ? l.getAttribute('text-decoration') : null; })();
  return out;
})()