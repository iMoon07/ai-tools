(async function () {
  var wait = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
  var st = document.getElementById('stage');
  function pe(t, cx, cy, b) {
    return new PointerEvent(t, { bubbles: true, cancelable: true, clientX: cx, clientY: cy,
      button: 0, buttons: b, pointerId: 1, pointerType: 'mouse', isPrimary: true });
  }
  var out = {};
  var btn = document.querySelector('[data-tool="text"]') || document.querySelector('[data-mode="text"]');
  out.toolBtn = btn ? (btn.getAttribute('data-tool') || btn.getAttribute('data-mode')) : null;
  return out;
})()