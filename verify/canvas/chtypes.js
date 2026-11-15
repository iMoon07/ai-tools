(async function(){
  var wait=function(ms){return new Promise(function(r){setTimeout(r,ms);});};
  var out={};
  document.querySelector('[data-scene-module="chart"]').click();
  await wait(700);
  var types=['bar','line','area','donut','kpi','gauge','table','hbar','scatter'];
  out.res={};
  for (var i=0;i<types.length;i++){
    var t=types[i];
    var sel=document.getElementById('chartType');
    if(!sel){ out.res[t]='no select'; continue; }
    var has=false;
    for (var j=0;j<sel.options.length;j++){ if(sel.options[j].value===t){has=true;break;} }
    if(!has){ out.res[t]='not offered'; continue; }
    sel.value=t;
    sel.dispatchEvent(new Event('change',{bubbles:true}));
    await wait(450);
    var chart=document.querySelector('.alur-chart-node');
    if(!chart){ out.res[t]='no chart node'; continue; }
    var svg=chart.querySelector('svg');
    var marks=svg?svg.querySelectorAll('rect,path,circle,text').length:0;
    var texts=svg?Array.prototype.map.call(svg.querySelectorAll('text'),function(x){return x.textContent;}).slice(0,8):[];
    var box=chart.querySelector('.alur-chart-box');
    var spec=chart.querySelector('[data-spec]');
    out.res[t]={marks:marks,texts:texts,type:spec?JSON.parse(spec.getAttribute('data-spec')).type:null,
      box:box?Math.round(box.getBBox().width)+'x'+Math.round(box.getBBox().height):null};
  }
  return out;
})()