(function(){
  var issues=[];
  function scan(root,label){
    if(!root) return;
    var all=root.querySelectorAll('*');
    for(var i=0;i<all.length;i++){
      var e=all[i];
      var r=e.getBoundingClientRect();
      var cs=getComputedStyle(e);
      if(cs.display==='none'||cs.visibility==='hidden') continue;
      if(r.width<1||r.height<1){
        if(e.children.length===0 && (e.textContent||'').trim())
          issues.push([label,'zero-size',e.tagName+'.'+e.className,JSON.stringify((e.textContent||'').trim().slice(0,30))]);
        continue;
      }
      if(e.scrollWidth>e.clientWidth+2 && cs.overflowX!=='auto' && cs.overflowX!=='scroll' && cs.textOverflow!=='ellipsis')
        issues.push([label,'h-overflow',e.tagName+'.'+e.className,e.scrollWidth+'/'+e.clientWidth]);
      if(e.scrollHeight>e.clientHeight+2 && cs.overflowY!=='auto' && cs.overflowY!=='scroll' && e.children.length===0)
        issues.push([label,'v-overflow',e.tagName+'.'+e.className,e.scrollHeight+'/'+e.clientHeight]);
    }
  }
  scan(document.querySelector('.topbar'),'topbar');
  scan(document.querySelector('.dock-body'),'dock');
  scan(document.querySelector('.tp'),'diagram');
  var tabs=document.getElementById('dockTabs');
  var tr=tabs.getBoundingClientRect();
  return {issues:issues.slice(0,14), count:issues.length,
    tabsFitsTabs: tabs.scrollWidth<=tabs.clientWidth+1,
    dockTabsRect:[Math.round(tr.x),Math.round(tr.y),Math.round(tr.width),Math.round(tr.height)]};
})()
