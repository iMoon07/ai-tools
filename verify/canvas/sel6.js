(async function () {
  var wait = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
  function pe(t, cx, cy, b) {
    return new PointerEvent(t, { bubbles: true, cancelable: true, clientX: cx, clientY: cy,
      button: 0, buttons: b, pointerId: 1, pointerType: 'mouse', isPrimary: true });
  }
  var sel = function () {
    return Array.prototype.map.call(document.querySelectorAll('.alur-canvas-node.is-selected'),
      function (e) { return e.getAttribute('data-node-id'); });
  };
  var pos = function (id) {
    var e = document.querySelector('[data-node-id="' + id + '"]');
    var m = /translate\(([-\d.]+) ([-\d.]+)\)/.exec(e.getAttribute('transform') || '');
    return Math.round(+m[1]) + ',' + Math.round(+m[2]);
  };
  function down(el, x, y) { el.dispatchEvent(pe('pointerdown', x, y, 1)); }
  function move(x, y) { document.dispatchEvent(pe('pointermove', x, y, 1)); }
  function up(x, y) { document.dispatchEvent(pe('pointerup', x, y, 0)); }
  var out = {};

  var logo = document.querySelector('[data-node-id="n1"] .alur-logo-img');
  if (logo) {
    var b = logo.getBoundingClientRect();
    var x = Math.round(b.x + b.width / 2), y = Math.round(b.y + b.height / 2);
    out.logoHit = document.elementFromPoint(x, y).getAttribute('class');
    var p0 = pos('n1');
    down(logo, x, y); move(x - 44, y + 44); up(x - 44, y + 44);
    await wait(150);
    out.logoDrag = { from: p0, to: pos('n1'), sel: sel() };
  }

  down(document.elementFromPoint(600, 150), 600, 150);
  move(650, 200); move(950, 320); up(950, 320);
  await wait(150);
  out.multi = sel();
  var first = out.multi[0];
  var el = document.querySelector('[data-node-id="' + first + '"]');
  var rb = el.getBoundingClientRect();
  var cx = Math.round(rb.x + rb.width * 0.85), cy = Math.round(rb.y + rb.height * 0.7);
  down(document.elementFromPoint(cx, cy), cx, cy); up(cx, cy);
  await wait(150);
  out.afterCollapse = sel();
  return out;
})()