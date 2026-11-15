(function () {
  var el = document.elementFromPoint(212, 286);
  var chain = [];
  var p = el;
  while (p && chain.length < 8) {
    chain.push(p.tagName + (p.getAttribute && p.getAttribute('class') ? '.' + p.getAttribute('class').split(' ')[0] : '') +
      (p.getAttribute && p.getAttribute('data-node-id') ? '#' + p.getAttribute('data-node-id') : ''));
    p = p.parentElement || (p.parentNode && p.parentNode.host ? null : p.parentNode);
    if (p && p.nodeType !== 1) p = p.parentElement;
  }
  var g = document.querySelector('.alur-chart-node');
  return { tag: el && el.tagName, cls: el && el.getAttribute && el.getAttribute('class'), chain: chain,
    chartPE: g ? getComputedStyle(g).pointerEvents : null,
    boxPE: g ? getComputedStyle(g.querySelector('.alur-chart-box')).pointerEvents : null,
    foPE: g ? getComputedStyle(g.querySelector('.alur-chart-fo')).pointerEvents : null,
    embedPE: (function(){var e=g&&g.querySelector('.alur-module-embed');return e?getComputedStyle(e).pointerEvents:null;})() };
})()