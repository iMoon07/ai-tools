(function () {
  var s = JSON.parse(document.getElementById('stage').getAttribute('data-spec') || '{}');
  return { sel: s.selected, nodes: Object.keys(s.nodes || {}), edges: (s.edges || []).length };
})()