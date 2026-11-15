global.window={};
global.window.TOPOLOGY_SPRITE=require('fs').readFileSync('/home/moon/Projects/imoon07.github.io/js/topology-icons.js','utf8');
global.window.ALUR_LOGO_MANIFEST=JSON.parse(require('fs').readFileSync('/home/moon/Projects/imoon07.github.io/js/logo-manifest.js','utf8').replace(/^[\s\S]*?=\s*/,'').replace(/;\s*$/,''));
require('/home/moon/Projects/imoon07.github.io/js/topo-lang.js');
const T=window.Topo;
const txt=require('fs').readFileSync(process.argv[2],'utf8');
const blocks=[...txt.matchAll(/```topology\n([\s\S]*?)\n```/g)].map(m=>m[1]);
blocks.forEach((b,i)=>{
  const s=T.parse(b);
  console.log('--- block',i,s.title);
  Object.keys(s.nodes).forEach(id=>{
    const n=s.nodes[id];
    console.log('   ', id.padEnd(12), JSON.stringify(n.label).padEnd(28), 'icons='+JSON.stringify(n.icons||[n.icon]));
  });
});
