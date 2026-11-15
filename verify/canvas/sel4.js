(async function () {
  var st = document.getElementById('stage');
  var wait = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
  function pe(t, cx, cy, buttons) {
    return new PointerEvent(t, { bubbles: true, cancelable: true, clientX: cx, clientY: cy,
      button: 0, buttons: buttons, pointerId: 1, pointerType: 'mouse', isPrimary: true });
  }
  var sel = function () {
    return Array.prototype.map.call(document.querySelectorAll('.alur-canvas-node.is-selected'),
      function (e) { return e.getAttribute('data-node-id'); });
  };
  var pos = function () {
    return Array.prototype.map.call(document.querySelectorAll('.alur-canvas-node'),
      function (e) { var m = /translate\(([-\d.]+) ([-\d.]+)\)/.exec(e.getAttribute('transform') || '');
        return e.getAttribute('data-node-id') + '=' + (m ? Math.round(+m[1]) + ',' + Math.round(+m[2]) : '?'); });
  };
  function center(id) {
    var el = document.querySelector('[data-node-id="' + id + '"]');
    var b = el.getBoundingClientRect();
    return [Math.round(b.x + b.width * 0.85), Math.round(b.y + b.height * 0.7)];
  }
  function down(el, x, y) { el.dispatchEvent(pe('pointerdown', x, y, 1)); }
  function move(x, y) { document.dispatchEvent(pe('pointermove', x, y, 1)); }
  function up(x, y) { document.dispatchEvent(pe('pointerup', x, y, 0)); }

  var out = {};
  var c1 = center('n1'), c2 = center('n2');

  down(document.elementFromPoint(c1[0], c1[1]), c1[0], c1[1]); up(c1[0], c1[1]); await wait(120);
  out.click1 = sel();

  down(document.elementFromPoint(c2[0], c2[1]), c2[0], c2[1]); up(c2[0], c2[1]); await wait(120);
  out.click2 = sel();

  down(document.elementFromPoint(c2[0], c2[1]), c2[0], c2[1]); move(c2[0] - 60, c2[1] + 40); up(c2[0] - 60, c2[1] + 40);
  await wait(150);
  out.afterDrag = { sel: sel(), pos: pos() };

  var mg = document.elementFromPoint(320, 700);
  down(mg, 320, 700); move(900, 400); up(900, 400); await wait(150);
  out.marquee = { sel: sel(), target: mg.tagName + '.' + (mg.getAttribute('class') || '') };
  return out;
})()