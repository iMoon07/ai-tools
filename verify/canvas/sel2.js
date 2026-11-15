(function () {
  var st = document.getElementById('stage');
  var spec = function () { return JSON.parse(st.getAttribute('data-spec') || '{}'); };
  function pe(t, cx, cy, buttons) {
    return new PointerEvent(t, { bubbles: true, cancelable: true, clientX: cx, clientY: cy,
      button: 0, buttons: buttons, pointerId: 1, pointerType: 'mouse', isPrimary: true });
  }
  function center(id) {
    var el = document.querySelector('[data-node-id="' + id + '"]');
    var b = el.getBoundingClientRect();
    return [Math.round(b.x + b.width * 0.85), Math.round(b.y + b.height * 0.7)];
  }
  var out = {};
  var c2 = center('n2');
  var el = document.elementFromPoint(c2[0], c2[1]);
  out.pt = c2;
  out.target = el ? el.tagName + '.' + (el.getAttribute('class') || '') : 'none';
  out.selBefore = spec().selected;
  el.dispatchEvent(pe('pointerdown', c2[0], c2[1], 1));
  out.selAfterDown = spec().selected;
  document.dispatchEvent(pe('pointerup', c2[0], c2[1], 0));
  out.selAfterUp = spec().selected;
  return out;
})()