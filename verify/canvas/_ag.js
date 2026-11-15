(function(){
  var out=[];
  var list=document.querySelectorAll('.tp');
  for(var k=0;k<list.length;k++){
    var p=list[k];
    var b=p.getBoundingClientRect();
    var bd=p.querySelector('.tp-board');
    if(!bd){out.push({i:k,err:'no board'});continue;}
    var br=bd.getBoundingClientRect();
    var cols=[].slice.call(p.querySelectorAll('.tp-col')).map(function(c){
      var r=c.getBoundingClientRect(); return [Math.round(r.left-br.left), Math.round(r.width)];});
    var nodes=[].slice.call(p.querySelectorAll('.tp-node'));
    var hs=nodes.map(function(nd){return Math.round(nd.getBoundingClientRect().height);});
    var ws=nodes.map(function(nd){return Math.round(nd.getBoundingClientRect().width);});
    var minL=cols.length?Math.min.apply(null,cols.map(function(c){return c[0];})):0;
    var maxR=cols.length?Math.max.apply(null,cols.map(function(c){return c[0]+c[1];})):0;
    out.push({i:k,title:(p.querySelector('.tp-title')||{}).textContent,
      board:[Math.round(br.width),Math.round(br.height)],
      cols:cols.length,colW:Array.from(new Set(cols.map(function(c){return c[1];}))),
      padL:minL,padR:Math.round(br.width-maxR),
      nodeH:Array.from(new Set(hs)),nodeW:Array.from(new Set(ws)).slice(0,4),
      rows:new Set(nodes.map(function(nd){return Math.round(nd.getBoundingClientRect().top);})).size,
      overflow: br.width>p.clientWidth+1});
  }
  return out;
})()
