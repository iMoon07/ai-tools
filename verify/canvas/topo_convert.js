#!/usr/bin/env node
/* Konversi blok ```topology lama (JSON) ke sintaks TOPO yang baru.

   Pakai: node /tmp/alur-probes/topo_convert.js <file.md> [...]
   Hanya mengganti isi blok ```topology. Blok yang sudah berbentuk sintaks
   baru dibiarkan apa adanya. */
'use strict';
const fs = require('fs');
const path = require('path');

global.window = global.window || {};
global.window.TOPOLOGY_SPRITE = fs.readFileSync(
    '/home/moon/Projects/imoon07.github.io/js/topology-icons.js', 'utf8');
global.window.ALUR_LOGO_MANIFEST = JSON.parse(
    fs.readFileSync('/home/moon/Projects/imoon07.github.io/js/logo-manifest.js', 'utf8')
        .replace(/^[\s\S]*?=\s*/, '').replace(/;\s*$/, ''));
require('/home/moon/Projects/imoon07.github.io/js/topo-lang.js');
const Topo = global.window.Topo;

/* node lama: [label, sub, icon|icons, kind, href]
   component: [label, icon, href] */
function toNode(id, v, isComponent) {
    if (Array.isArray(v)) {
        let label, sub, icons, kind, href;
        if (isComponent) {
            label = v[0] || id;
            sub = '';
            icons = v[1] ? [v[1]] : [];
            kind = '';
            href = v[2] || '';
        } else {
            label = v[0] || id;
            sub = v[1] || '';
            const raw = v[2];
            icons = Array.isArray(raw) ? raw.filter(Boolean) : (raw ? [raw] : []);
            kind = v[3] || '';
            href = v[4] || '';
        }
        return { id, label, sub, icons, icon: icons[0] || '', kind, href };
    }
    if (v && typeof v === 'object') {
        const icons = (v.icons && v.icons.length) ? v.icons : (v.icon ? [v.icon] : []);
        return { id, label: v.label || id, sub: v.sub || '', icons, icon: icons[0] || '', kind: v.kind || '', href: v.href || '' };
    }
    return { id, label: id, sub: '', icons: [], icon: '', kind: '', href: '' };
}

function normalize(old) {
    const spec = old || {};
    const nodes = {};

    /* nodes dan components satu kamus. */
    Object.keys(spec.nodes || {}).forEach(id => { nodes[id] = toNode(id, spec.nodes[id], false); });
    Object.keys(spec.components || {}).forEach(id => { nodes[id] = toNode(id, spec.components[id], true); });

    /* root lama jadi node biasa dengan judul diagram. */
    if (spec.root) {
        const r = Array.isArray(spec.root) ? spec.root : [];
        const id = 'root';
        nodes[id] = {
            id,
            label: r[0] || spec.title || 'Root',
            sub: r[1] || '',
            icons: r[2] ? [r[2]] : [],
            icon: r[2] || '',
            kind: r[3] || '',
            href: r[4] || ''
        };
    }

    /* Label grup: kolom yang isinya sama dengan grup pakai judul grup. */
    const groupLabel = {};
    (spec.groups || []).forEach(g => {
        if (!Array.isArray(g)) return;
        const ids = (g[1] || []).filter(id => nodes[id]);
        if (!ids.length) return;
        groupLabel[ids.slice().sort().join('|')] = g[0] || '';
    });

    const columns = [];
    (spec.columns || []).forEach(c => {
        const ids = Array.isArray(c) ? c : (c.nodes || []);
        const clean = ids.filter(id => nodes[id]);
        if (!clean.length) return;
        if (!Array.isArray(c) && c.label) {
            columns.push({ label: c.label, nodes: clean });
            return;
        }
        const lab = groupLabel[clean.slice().sort().join('|')];
        if (lab) columns.push({ label: lab, nodes: clean });
        else columns.push(clean);
    });

    /* Node yang tidak masuk kolom mana pun tetap ditampilkan.
       components yang cuma dipakai sebagai ikon (tidak disebut kolom) bukan
       node, jadi dibuang supaya tidak jadi kotak hantu. */
    const placed = {};
    columns.forEach(c => (Array.isArray(c) ? c : c.nodes).forEach(id => { placed[id] = 1; }));
    const keep = {};
    Object.keys(spec.nodes || {}).forEach(id => { keep[id] = 1; });
    if (spec.root) keep.root = 1;
    Object.keys(placed).forEach(id => { keep[id] = 1; });
    Object.keys(nodes).forEach(id => { if (!keep[id]) delete nodes[id]; });
    Object.keys(nodes).forEach(id => { if (!placed[id]) columns.push([id]); });

    const edges = [];
    (spec.edges || []).forEach(e => {
        if (Array.isArray(e)) edges.push({ from: e[0], to: e[1], label: e[2] || '', back: !!e[3] });
        else if (e && e.from && e.to) edges.push({ from: e.from, to: e.to, label: e.label || '', back: !!e.back });
    });

    const out = {
        title: spec.title || 'Topology',
        vertical: spec.vertical !== false,
        nodes, columns, edges
    };

    const legend = {};
    if (spec.legend && typeof spec.legend === 'object') {
        if (spec.legend.flow) legend.flow = spec.legend.flow;
        if (spec.legend.back) legend.back = spec.legend.back;
    }
    if (Object.keys(legend).length) out.legend = legend;
    return out;
}

let changed = 0;
process.argv.slice(2).forEach(file => {
    const abs = path.resolve(file);
    const before = fs.readFileSync(abs, 'utf8');
    let n = 0;
    const text = before.replace(/```topology[ \t]*\n([\s\S]*?)\n```/g, (whole, body) => {
        const trimmed = body.trim();
        if (trimmed.charAt(0) !== '{') return whole;
        n++;
        return '```topology\n' + Topo.stringify(normalize(JSON.parse(trimmed))) + '\n```';
    });
    if (text !== before) {
        fs.writeFileSync(abs, text);
        console.log('converted', file, '(' + n + ' blok)');
        changed += n;
    } else {
        console.log('unchanged', file);
    }
});
console.log('total blok:', changed);