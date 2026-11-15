global.window={};
global.window.TOPOLOGY_SPRITE=require('fs').readFileSync('/home/moon/Projects/imoon07.github.io/js/topology-icons.js','utf8');
global.window.ALUR_LOGO_MANIFEST={logos:[{name:'mean'},{name:'mern'}]};
require('/home/moon/Projects/imoon07.github.io/js/topo-lang.js');
const T=window.Topo;
const src=`topology Solution Stack
  mean  MEAN
    mern  MERN  mongodb express react nodejs
    mevn  MEVN
  php
    laravel  Laravel
    symfony  Symfony
  infra
  lone  Lone Node
  a > b`;
const s=T.parse(src);
console.log(JSON.stringify(s.columns));
console.log('---roundtrip---');
console.log(T.stringify(s));
