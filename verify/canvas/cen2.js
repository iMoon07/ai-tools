(function(){
  var spec = {"module":"canvas","title":"My canvas","grid":true,"width":900,"height":520,
    "nodes":{
      "n2":{"label":"Client","sub":"browser","logo":"stack:github","color":"blue","id":"n2","w":132,"h":66,"shape":"box","x":748,"y":990},
      "n3":{"label":"Edge","sub":"nginx","logo":"stack:nginx","color":"green","id":"n3","w":132,"h":66,"shape":"box","x":968,"y":990},
      "n4":{"label":"Web","sub":"react","logo":"programming:react","color":"amber","id":"n4","w":132,"h":66,"shape":"box","x":1166,"y":990},
      "n5":{"label":"API","sub":"node","logo":"programming:nodejs","color":"red","id":"n5","w":132,"h":66,"shape":"box","x":1386,"y":990}},
    "edges":[{"from":"n2","to":"n3"},{"from":"n3","to":"n4"},{"from":"n4","to":"n5"}],
    "selected":null,"selectedEdge":null,"selectedEdges":[],"selectedDrawing":null,
    "zoom":1,"panX":288.4,"panY":674.5,"edgeStyle":{},"drawings":[]};
  var host=document.getElementById('content')||document.body;
  var d=document.createElement('div');
  d.className='alur draw';
  d.setAttribute('data-spec', JSON.stringify(spec));
  host.appendChild(d);
  window.Alur.mount(d);
  var svg=d.querySelector('svg');
  var out={layers:{}, nodes:{}};
  ['draw','edges','points','nodes'].forEach(function(n){
    var l=svg.querySelector('.alur-layer-'+n);
    if(!l){out.layers[n]='missing';return;}
    try{var b=l.getBBox();out.layers[n]=[Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height)];}
    catch(e){out.layers[n]='err';}
  });
  Array.prototype.forEach.call(svg.querySelectorAll('.alur-canvas-node'),function(g){
    var b=g.getBBox(); out.nodes[g.getAttribute('data-node-id')]=[Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height)];
  });
  var vb=svg.getAttribute('viewBox');
  out.vb=vb;
  var r=svg.getBoundingClientRect();
  out.screen=[Math.round(r.width),Math.round(r.height)];
  return out;
})()