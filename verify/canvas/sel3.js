(async function () {
  var st = document.getElementById('stage');
  var wait = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
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
  function dragAt(pt, dx, dy) {
    var el = document.elementFromPoint(pt[0], pt[1]);
    el.dispatchEvent(pe('pointerdown', pt[0], pt[1], 1));
    document.dispatchEvent(pe('pointermove', pt[0] + dx / 2, pt[1] + dy / 2, 1));
    document.dispatchEvent(pe('pointermove', pt[0] + dx, pt[1] + dy, 1));
    document.dispatchEvent(pe('pointerup', pt[0] + dx, pt[1] + dy, 0));
  }
  var out = {};
  var c1 = center('n1'), c2 = center('n2'), c3 = center('n3');
  out.pts = { n1: c1, n2: c2, n3: c3 };

  dragAt(c1, 0, 0); await wait(160);
  out.clickN1 = spec().selected;

  dragAt(c2, 0, 0); await wait(160);
  out.clickN2 = spec().selected;

  var x0 = Math.min(c1[0], c3[0]) - 40, y0 = Math.min(c1[1], c3[1]) - 50;
  var x1 = Math.max(c1[0], c3[0]) + 40, y1 = Math.max(c1[1], c3[1]) + 60;
  var mg = document.elementFromPoint(x0, y0);
  mg.dispatchEvent(pe('pointerdown', x0, y0, 1));
  document.dispatchEvent(pe('pointermove', (x0 + x1) / 2, (y0 + y1) / 2, 1));
  document.dispatchEvent(pe('pointermove', x1, y1, 1));
  document.dispatchEvent(pe('pointerup', x1, y1, 0));
  await wait(180);
  out.marquee = spec().selected;
  out.marqueeTarget = mg.tagName + '.' + (mg.getAttribute('class') || '');

  var before = spec().nodes;
  dragAt([x1 - 10, y1 - 10], -50, 30); await wait(180);
  var after = spec().nodes;
  out.moved = Object.keys(after).map(function (k) { return k + ':' + Math.round(after[k].x) + ',' + Math.round(after[k].y); });
  out.before = Object.keys(before).map(function (k) { return k + ':' + Math.round(before[k].x) + ',' + Math.round(before[k].y); });
  return out;
})()