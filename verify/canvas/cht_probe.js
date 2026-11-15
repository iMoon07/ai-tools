(function () {
  var s = JSON.parse(document.getElementById('stage').getAttribute('data-spec') || '{}');
  var n = s.nodes && s.nodes.n4;
  var host = document.querySelector('.alur-chart-node');
  var layer = host ? host.parentNode : null;
  var marks = [];
  if (layer) {
    Array.prototype.forEach.call(layer.children, function (e) {
      var c = e.getAttribute && e.getAttribute('class');
      if (c && /handle|resize|select/i.test(c)) marks.push(c);
    });
  }
  var spec = null;
  if (n && n.staticSpec) {
    spec = { type: n.staticSpec.type, labels: n.staticSpec.labels, data: n.staticSpec.data };
  }
  return {
    sel: { selected: s.selected, edge: s.selectedEdge },
    node: n ? { shape: n.shape, w: n.w, h: n.h, x: Math.round(n.x), y: Math.round(n.y) } : null,
    spec: spec,
    layerChildren: layer ? layer.children.length : -1,
    marks: marks,
    title: (document.querySelector('#panelProperties b') || {}).textContent,
    hintText: /drag to move/.test(document.body.textContent),
    svgTexts: Array.prototype.map.call(document.querySelectorAll('.alur-chart-node text'), function (t) { return t.textContent; }).slice(0, 12)
  };
})()