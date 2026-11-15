(function(){
  var R=function(e){if(!e)return null;var b=e.getBoundingClientRect();return [Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height)];};
  var p=document.getElementById('preview');
  var tp=p.querySelector('.tp');
  var board=p.querySelector('.tp-board');
  var grid=p.querySelector('.tp-grid');
  var cols=[].slice.call(p.querySelectorAll('.tp-col'));
  var nodes=[].slice.call(p.querySelectorAll('.tp-node'));
  var head=p.querySelector('.tp-head');
  var cs=function(e,k){return e?getComputedStyle(e)[k]:null;};
  return {
    preview:R(p), tp:R(tp), head:R(head), board:R(board), grid:R(grid),
    gridStyle:grid?[cs(grid,'display'),cs(grid,'flexDirection'),cs(grid,'alignItems'),cs(grid,'gap')]:null,
    cols:cols.map(R), colStyle:cols[0]?[cs(cols[0],'maxWidth'),cs(cols[0],'width'),cs(cols[0],'flex')]:null,
    nodes:nodes.map(function(n){return {r:R(n),label:(n.querySelector('.tp-node-label')||{}).textContent,icon:!!n.querySelector('.tp-icon'),cls:n.className};}),
    nodeStyle:nodes[0]?[cs(nodes[0],'display'),cs(nodes[0],'padding'),cs(nodes[0],'borderRadius'),cs(nodes[0],'background'),cs(nodes[0],'border')]:null,
    wires:(function(){var w=p.querySelector('.tp-wires');return w?[w.getAttribute('viewBox'),R(w)]:null;})(),
    emptyRight: grid? (Math.round(grid.getBoundingClientRect().width) - Math.round(cols[cols.length-1].getBoundingClientRect().right + grid.getBoundingClientRect().left)) : null
  };
})()
