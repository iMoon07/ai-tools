(function(){
  var t=document.getElementById('specBox');
  var a=t.value;
  var body=a.slice(a.indexOf('\n')+1);
  body=body.slice(0,body.lastIndexOf('\n```'));
  var s=window.Topo.parse(body);
  var b=window.Topo.stringify(s);
  return {same:a===('```topology\n'+b+'\n```'), len:a.length, blen:b.length};
})()
