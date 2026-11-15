(function(){
  var spec = {"module":"canvas","title":"My canvas","grid":true,"width":900,"height":520,
    "nodes":{
      "n10":{"label":"Client","sub":"browser","logo":"stack:github","color":"blue","id":"n10","w":132,"h":66,"shape":"box","x":638,"y":1518},
      "n11":{"label":"Reverse Proxy","sub":"edge layer","logo":"stack:nginx","color":"cyan","id":"n11","w":132,"h":66,"shape":"box","x":858,"y":1518}},
    "edges":[{"from":"n10","to":"n11"}],
    "selected":"n10","selectedEdge":null,"selectedEdges":[],"selectedDrawing":null,
    "zoom":1,"panX":590,"panY":943.9,"edgeStyle":{},"drawings":[]};
  var host=document.getElementById('content')||document.body;
  var d=document.createElement('div');
  d.className='alur draw';
  d.setAttribute('data-spec', JSON.stringify(spec));
  host.appendChild(d);
  window.Alur.mount(d);
  var svg=d.querySelector('svg');
  return {
    handles: svg.querySelectorAll('.alur-layer-handles *').length,
    selectedNodes: svg.querySelectorAll('.alur-canvas-node.is-selected').length,
    selBoxes: svg.querySelectorAll('.alur-selection-box').length,
    vb: svg.getAttribute('viewBox'),
    nodeCls: (svg.querySelector('.alur-canvas-node')||{}).getAttribute?svg.querySelector('.alur-canvas-node').getAttribute('class'):null
  };
})()