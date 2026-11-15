(async function(){
  var wait=function(ms){return new Promise(function(r){setTimeout(r,ms);});};
  var out={};
  var box=document.getElementById('exportBox');
  box.open=true;
  await wait(200);
  var ta=document.getElementById('drawCode');
  var v=ta.value;
  out.head=v.slice(0,10);
  out.tail=v.slice(-6);
  out.fenced=/^```draw\n/.test(v)&&/\n```$/.test(v);
  var body=v.replace(/^```draw\n/,'').replace(/\n```$/,'');
  var spec=JSON.parse(body);
  out.parsed=!!spec&&spec.module;
  spec.title='Applied from fenced block';
  ta.value='```draw\n'+JSON.stringify(spec,null,2)+'\n```';
  document.getElementById('applyCode').click();
  await wait(500);
  var live=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));
  out.applied=live.title;
  document.getElementById('revertCode').click();
  await wait(250);
  out.reverted=document.getElementById('drawCode').value.slice(0,10);
  return out;
})()