(function(){
  var out=[];
  var list=document.querySelectorAll('.tp');
  for(var k=0;k<list.length;k++){
    var p=list[k];
    var paths=[].slice.call(p.querySelectorAll('.tp-wire'));
    var labels=[].slice.call(p.querySelectorAll('.tp-wire-label'));
    out.push({i:k,
      wires:paths.length,
      d:paths.slice(0,4).map(function(e){return e.getAttribute('d');}),
      markers:paths.slice(0,4).map(function(e){return e.getAttribute('marker-end');}),
      labels:labels.map(function(e){return (e.textContent||'').trim();}).slice(0,4)});
  }
  return out;
})()
