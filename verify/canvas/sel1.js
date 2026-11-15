(function () {
  var st = document.getElementById('stage');
  var spec = function () { return JSON.parse(st.getAttribute('data-spec') || '{}'); };
  var out = {};
  function pe(t, el, cx, cy, buttons) {
    return new PointerEvent(t, { bubbles: true, cancelable: true, clientX: cx, clientY: cy,
      button: 0, buttons: buttons, pointerId: 1, pointerType: 'mouse', isPrimary: true });
  }
  function drag(from, dx, dy) {
    var el = document.elementFromPoint(from[0], from[1]);
    el.dispatchEvent(pe('pointerdown', el, from[0], from[1], 1));
    document.dispatchEvent(pe('pointermove', document.body, from[0] + dx * 0.5, from[1] + dy * 0.5, 1));
    document.dispatchEvent(pe('pointermove', document.body, from[0] + dx, from[1] + dy, 1));
    document.dispatchEvent(pe('pointerup', document.body, from[0] + dx, from[1] + dy, 0));
  }
  function center(id) {
    var el = document.querySelector('[data-node-id="' + id + '"]');
    var b = el.getBoundingClientRect();
    return [Math.round(b.x + b.width * 0.85), Math.round(b.y + b.height * 0.7)];
  }
  function xy(id) { var n = spec().nodes[id]; return { x: Math.round(n.x), y: Math.round(n.y) }; }

  out.before = xy('n1');
  var c1 = center('n1');
  drag(c1, -60, 40);
  out.afterDrag = xy('n1');
  out.selAfterDrag = spec().selected;

  var c2 = center('n2');
  drag(c2, 0, 0);
  out.selAfterClick = spec().selected;

  var a = center('n1'), b = center('n2');
  var x0 = Math.min(a[0], b[0]) - 30, y0 = Math.min(a[1], b[1]) - 30;
  var x1 = Math.max(a[0], b[0]) + 30, y1 = Math.max(a[1], b[1]) + 30;
  var mg = document.elementFromPoint(x0, y0);
  mg.dispatchEvent(pe('pointerdown', mg, x0, y0, 1));
  document.dispatchEvent(pe('pointermove', document.body, (x0 + x1) / 2, (y0 + y1) / 2, 1));
  document.dispatchEvent(pe('pointermove', document.body, x1, y1, 1));
  document.dispatchEvent(pe('pointerup', document.body, x1, y1, 0));
  out.marqueeSel = spec().selected;
  out.marquee = spec().selectedEdges;
  return out;
})()