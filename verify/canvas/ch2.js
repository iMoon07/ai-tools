(async function(){
  var wait=function(ms){return new Promise(function(r){setTimeout(r,ms);});};
  var out={};
  document.querySelector('[data-scene-module="chart"]').click();
  await wait(700);
  var chart=document.querySelector('.alur-chart-node');
  out.created=!!chart;
  var spec=chart?JSON.parse(chart.querySelector('[data-spec]').getAttribute('data-spec')):null;
  out.spec=spec?{type:spec.type,labels:spec.labels,data:spec.data}:null;
  var row=document.getElementById('chartDataRow');
  var box=document.getElementById('chartData');
  out.dataRowHidden=row?row.hidden:null;
  out.dataValue=box?box.value:null;
  if(box){
    box.value='api = 12\nweb = 8\ndb = 3';
    box.dispatchEvent(new Event('input',{bubbles:true}));
    await wait(500);
    var ch2=document.querySelector('.alur-chart-node');
    var s2=ch2?JSON.parse(ch2.querySelector('[data-spec]').getAttribute('data-spec')):null;
    out.afterType=s2?{labels:s2.labels,data:s2.data}:null;
    out.bars=ch2?ch2.querySelectorAll('.alur-bar').length:0;
  }
  var res={};
  var sel=document.getElementById('chartType');
  ['bar','line','donut','kpi','gauge','table','scatter'].forEach(function(t){});
  ['kpi','gauge','scatter'].forEach(function(t){
    if(!sel) return;
    sel.value=t; sel.dispatchEvent(new Event('change',{bubbles:true}));
  });
  await wait(600);
  var ch3=document.querySelector('.alur-chart-node');
  var s3=ch3?JSON.parse(ch3.querySelector('[data-spec]').getAttribute('data-spec')):null;
  out.lastType=s3?s3.type:null;
  out.lastData=s3?s3.data:null;
  out.texts=ch3?Array.prototype.map.call(ch3.querySelectorAll('text'),function(x){return x.textContent;}).slice(0,8):[];
  out.nan=/NaN/.test(ch3?ch3.textContent:'');
  return out;
})()