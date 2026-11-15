(function () {
  var st = document.getElementById('stage');
  var n1 = document.querySelector('[data-node-id="n1"]');
  var b = n1.getBoundingClientRect();
  var x = Math.round(b.x + b.width * 0.8), y = Math.round(b.y + b.height * 0.6);
  var el = document.elementFromPoint(x, y);
  var ev = function (t, cx, cy, buttons) {
    return new PointerEvent(t, { bubbles: true, cancelable: true, clientX: cx, clientY: cy,
      button: 0, buttons: buttons, pointerId: 1, pointerType: 'mouse', isPrimary: true });
  };
  el.dispatchEvent(ev('pointerdown', x, y, 1));
  document.dispatchEvent(ev('pointermove', x - 30, y + 20, 1));
  document.dispatchEvent(ev('pointermove', x - 60, y + 40, 1));
  document.dispatchEvent(ev('pointerup', x - 60, y + 40, 0));
  var s = JSON.parse(document.getElementById('stage').getAttribute('data-spec') || '{}');
  var n = s.nodes && s.nodes.n1;
  var el2 = document.querySelector('[data-node-id="n1"]');
  var b2 = el2.getBoundingClientRect();
  return { target: el.getAttribute('class'), x: n && Math.round(n.x), y: n && Math.round(n.y),
    screenX: Math.round(b2.x), screenY: Math.round(b2.y), selected: s.selected };
})()