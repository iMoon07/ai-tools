const fs=require('fs'), path=require('path');
global.window={};
global.window.TOPOLOGY_SPRITE=fs.readFileSync('/home/moon/Projects/imoon07.github.io/js/topology-icons.js','utf8');
global.window.ALUR_LOGO_MANIFEST=JSON.parse(fs.readFileSync('/home/moon/Projects/imoon07.github.io/js/logo-manifest.js','utf8').replace(/^[\s\S]*?=\s*/,'').replace(/;\s*$/,''));
require('/home/moon/Projects/imoon07.github.io/js/topo-lang.js');
const T=window.Topo;
const root='/home/moon/Projects/Penjelajah-CyberSecurity';
const files=[];
(function walk(d){for(const f of fs.readdirSync(d)){const p=path.join(d,f);
  const st=fs.statSync(p); if(st.isDirectory()){if(f==='node_modules'||f.startsWith('.git'))continue;walk(p);}
  else if(f.endsWith('.md'))files.push(p);}})(root);
let blocks=0, diff=0, errs=0;
for(const f of files){
  const txt=fs.readFileSync(f,'utf8');
  const re=/```topology[ \t]*\n([\s\S]*?)\n```/g; let m;
  while((m=re.exec(txt))){
    blocks++;
    const a=m[1];
    const s1=T.parse(a);
    if(s1._errors){errs++;console.log('ERR ',path.relative(root,f),s1._errors);}
    const b=T.stringify(s1);
    const s2=T.parse(b);
    const c=T.stringify(s2);
    if(b!==c){diff++;console.log('DIFF',path.relative(root,f));console.log('  A:',JSON.stringify(b.slice(0,200)));console.log('  B:',JSON.stringify(c.slice(0,200)));}
    // bandingkan struktur
    const k1=JSON.stringify([s1.columns,Object.keys(s1.nodes).sort(),s1.edges]);
    const k2=JSON.stringify([s2.columns,Object.keys(s2.nodes).sort(),s2.edges]);
    if(k1!==k2){console.log('STRUCT',path.relative(root,f));}
  }
}
console.log('blocks',blocks,'| roundtrip diff',diff,'| parse errors',errs);
