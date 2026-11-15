(function(){
  var spec = {
    "module":"canvas","title":"My canvas","grid":true,"width":900,"height":520,
    "cable":"solid","motion":"flow","speed":1,
    "nodes":{
      "n2":{"label":"Client","sub":"browser","logo":"stack:github","color":"blue","id":"n2","w":132,"h":66,"shape":"box","x":748,"y":990},
      "n3":{"label":"Edge","sub":"nginx","logo":"stack:nginx","color":"green","id":"n3","w":132,"h":66,"shape":"box","x":968,"y":990},
      "n4":{"label":"Web","sub":"react","logo":"programming:react","color":"amber","id":"n4","w":132,"h":66,"shape":"box","x":1166,"y":990},
      "n5":{"label":"API","sub":"node","logo":"programming:nodejs","color":"red","id":"n5","w":132,"h":66,"shape":"box","x":1386,"y":990}
    },
    "edges":[{"from":"n2","to":"n3"},{"from":"n3","to":"n4"},{"from":"n4","to":"n5"}],
    "selected":null,"selectedEdge":null,"selectedEdges":[],"selectedDrawing":null,
    "zoom":1,"panX":288.4,"panY":674.5,"edgeStyle":{},"drawings":[]
  };
  var host=document.getElementById('content')||document.body;
  var d=document.createElement('div');
  d.className='alur draw';
  d.setAttribute('data-spec', JSON.stringify(spec));
  host.appendChild(d);
  window.Alur.mount(d);
  var svg=d.querySelector('svg');
  var vb=svg.getAttribute('viewBox');
  var parts=vb.split(/\s+/).map(Number);
  var b=svg.getBBox();
  var r=svg.getBoundingClientRect();
  return {vb:vb, bbox:{x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height)},
    screen:{w:Math.round(r.width),h:Math.round(r.height)},
    contentLeftInView:Math.round(b.x-parts[0]), contentTopInView:Math.round(b.y-parts[1]),
    viewW:Math.round(parts[2]), viewH:Math.round(parts[3])};
})()