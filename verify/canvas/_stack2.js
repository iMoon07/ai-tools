(function(){
  try{
    var box=document.getElementById('specBox');
    var t=box.value;
    t=t.slice(t.indexOf('\n')+1);
    t=t.slice(0,t.lastIndexOf('\n```'));
    var spec=window.Topo.parse(t);
    var d=document.createElement('div');
    window.Topo.render(d,spec);
    return 'no error';
  }catch(e){return (e&&e.stack)||String(e);}
})()
