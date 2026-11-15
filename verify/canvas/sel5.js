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
  var pos = function () {
    return Array.prototype.map.call(document.querySelectorAll('.alur-canvas-node'),
      function (e) { var m = /translate\(([-\d.]+) ([-\d.]+)\)/.exec(e.getAttribute('transform') || '');
        return e.getAttribute('data-node-id') + '=' + (m ? Math.round(+m[1]) + ',' + Math.round(+m[2]) : '?'); });
  };
  function down(el, x, y) { el.dispatchEvent(pe('pointerdown', x, y, 1)); }
  function move(x, y) { document.dispatchEvent(pe('pointermove', x, y, 1)); }
  function up(x, y) { document.dispatchEvent(pe('pointerup', x, y, 0)); }
  var out = {};
  var mg = document.elementFromPoint(250, 90);
  out.start = mg.tagName + '.' + (mg.getAttribute('class') || '');
  down(mg, 250, 90); move(600, 200); move(980, 300); up(980, 300);
  await wait(160);
  out.marqueeSel = sel();
  out.posAfterMarquee = pos();
  if (!out.marqueeSel.length) return out;
  var a = document.querySelector('[data-node-id="' + out.marqueeSel[0] + '"]').getBoundingClientRect();
  var x = Math.round(a.x + a.width * 0.85), y = Math.round(a.y + a.height * 0.7);
  down(document.elementFromPoint(x, y), x, y); move(x + 44, y + 44); up(x + 44, y + 44);
  await wait(160);
  out.afterMultiDrag = pos();
  out.selAfter = sel();
  return out;
})()