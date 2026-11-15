
(function () {
  'use strict';

  var CABLES = AlurCables.catalog;
  var MOTIONS = AlurMotions.catalog;
  var COLOR_KEYS = Object.keys(AlurKit.palette);
  var CABLE_IDS = CABLES.map(function (c) { return c.id; });
  var MOTION_IDS = MOTIONS.map(function (m) { return m.id; });

  /* Scene generators ---------------------------------------------------- */

  var NODE_POOL = [
    { label: 'Client', sub: 'browser', logo: 'stack:github' },
    { label: 'Edge', sub: 'nginx', logo: 'stack:nginx' },
    { label: 'Web', sub: 'react', logo: 'programming:react' },
    { label: 'API', sub: 'node', logo: 'programming:nodejs' },
    { label: 'Worker', sub: 'python', logo: 'programming:python' },
    { label: 'Cache', sub: 'redis', logo: 'stack:redis' },
    { label: 'Queue', sub: 'kafka', logo: 'stack:apachekafka' },
    { label: 'DB', sub: 'postgres', logo: 'stack:postgresql' },
    { label: 'Search', sub: 'elastic', logo: 'stack:elasticsearch' },
    { label: 'Metrics', sub: 'prometheus', logo: 'stack:prometheus' },
    { label: 'Dash', sub: 'grafana', logo: 'stack:grafana' },
    { label: 'Deploy', sub: 'docker', logo: 'stack:docker' },
    { label: 'Orbit', sub: 'k8s', logo: 'stack:kubernetes' }
  ];

  var BACKEND_POOL = [
    { label: 'API', sub: 'node', logo: 'programming:nodejs' },
    { label: 'Worker', sub: 'python', logo: 'programming:python' },
    { label: 'Service', sub: 'go', logo: 'programming:go' },
    { label: 'Legacy', sub: 'java', logo: 'programming:java' },
    { label: 'Web', sub: 'php', logo: 'programming:php' },
    { label: 'Cache', sub: 'redis', logo: 'stack:redis' },
    { label: 'DB', sub: 'postgres', logo: 'stack:postgresql' },
    { label: 'Search', sub: 'elastic', logo: 'stack:elasticsearch' }
  ];

  function makeCanvas() {
    return {
      module: 'canvas',
      title: 'My canvas',
      grid: true,
      width: 900,
      height: 520,
      cable: 'solid',
      motion: 'flow',
      speed: 1,
      nodes: {},
      edges: []
    };
  }

  function clampInt(v, lo, hi, dflt) {
    v = parseInt(v, 10);
    if (isNaN(v)) return dflt;
    return Math.max(lo, Math.min(hi, v));
  }

  function makeFlow(cols, perCol, pattern) {
    cols = clampInt(cols, 1, 5, 4);
    perCol = clampInt(perCol, 1, 4, 1);
    pattern = pattern || 'bipartite';
    var columns = [], nodes = {}, edges = [], id = 0;
    for (var c = 0; c < cols; c++) {
      var col = [];
      for (var r = 0; r < perCol; r++) {
        var p = NODE_POOL[id % NODE_POOL.length];
        var nid = 'n' + id;
        nodes[nid] = {
          label: p.label, sub: p.sub, logo: p.logo,
          color: COLOR_KEYS[id % COLOR_KEYS.length]
        };
        col.push(nid);
        id++;
      }
      columns.push(col);
    }
    for (var c2 = 0; c2 < cols - 1; c2++) {
      var a = columns[c2], b = columns[c2 + 1];
      if (pattern === 'fan') {
        for (var r2 = 1; r2 < b.length; r2++) edges.push({ from: a[0], to: b[r2] });
      } else if (pattern === 'chain' && a.length === b.length) {
        for (var r3 = 0; r3 < a.length; r3++) edges.push({ from: a[r3], to: b[r3] });
      } else {
        a.forEach(function (x) {
          b.forEach(function (y) { edges.push({ from: x, to: y }); });
        });
      }
    }
    return {
      module: 'flow',
      title: 'Flow — ' + cols + '×' + perCol,
      cable: 'solid', motion: 'flow', speed: 1,
      columns: columns, nodes: nodes, edges: edges,
      pattern: pattern
    };
  }

  function makeProxy(count) {
    count = clampInt(count, 1, 8, 3);
    var nodes = {
      client: { label: 'Client', sub: 'browser', logo: 'stack:github', color: 'blue' },
      proxy: { label: 'Reverse Proxy', sub: 'edge layer', logo: 'stack:nginx', color: 'cyan' }
    };
    for (var i = 0; i < count; i++) {
      var p = BACKEND_POOL[i % BACKEND_POOL.length];
      nodes['backend' + (i + 1)] = {
        label: p.label + ' ' + (i + 1), sub: p.sub, logo: p.logo,
        color: COLOR_KEYS[(i + 2) % COLOR_KEYS.length]
      };
    }
    return {
      module: 'reverse-proxy',
      title: 'Reverse proxy — ' + count + ' backends',
      speed: 1, backends: count, nodes: nodes
    };
  }

  function rnd(lo, hi) {
    return Math.round(lo + Math.random() * (hi - lo));
  }

  function chartPreset(type, seriesCount, points) {
    type = type || 'bar';
    seriesCount = clampInt(seriesCount, 1, 4, 2);
    points = clampInt(points, 3, 12, 7);

    var labels = [];
    for (var i = 0; i < points; i++) labels.push('P' + (i + 1));
    var p = {
      module: 'chart',
      type: type,
      title: 'Alur chart — ' + type,
      height: 320,
      color: 'blue',
      _series: seriesCount,
      _points: points
    };

    function makeSeries(count, lo, hi) {
      var out = [];
      for (var s = 0; s < count; s++) {
        out.push({
          name: 'series ' + (s + 1),
          data: labels.map(function () { return rnd(lo, hi); }),
          color: COLOR_KEYS[s % COLOR_KEYS.length]
        });
      }
      return out;
    }

    function values(lo, hi) {
      return labels.map(function () { return rnd(lo, hi); });
    }

    if (type === 'line' || type === 'stacked' || type === 'stackedArea' || type === 'density') {
      p.series = makeSeries(seriesCount, 3, 30);
    } else if (type === 'donut') {
      var dn = Math.min(8, points);
      p.labels = labels.slice(0, dn);
      p.data = values(5, 40).slice(0, dn);
      p.colors = COLOR_KEYS.slice(0, dn);
      p.centerLabel = 'total';
    } else if (type === 'gauge') {
      p.data = [rnd(20, 90)]; p.max = 100; p.unit = '%'; p.label = 'usage';
    } else if (type === 'kpi') {
      p.data = [rnd(50, 500)]; p.label = 'requests / sec';
      p.delta = (rnd(-20, 30) > 0 ? '+' : '') + rnd(-20, 30) + '%';
    } else if (type === 'scatter') {
      p.data = labels.map(function () { return [rnd(2, 20), rnd(2, 20)]; });
      p.xLabel = 'latency (ms)'; p.yLabel = 'throughput';
    } else if (type === 'waterfall') {
      var wn = Math.min(5, points);
      p.labels = labels.slice(0, wn);
      p.data = values(-15, 30).slice(0, wn);
    } else if (type === 'funnel') {
      p.labels = ['Visit', 'Signup', 'Active', 'Paid'];
      p.data = [100, rnd(40, 70), rnd(20, 40), rnd(5, 20)];
      p.colors = ['blue', 'cyan', 'green', 'amber'];
    } else if (type === 'bell') {
      p.mean = 0; p.sigma = 1; p.marker = 0.6; p.markerLabel = 'p95';
    } else if (type === 'histogram') {
      p.bins = Math.min(10, points);
      p.data = [];
      for (var h = 0; h < 16; h++) p.data.push(rnd(1, 12));
    } else if (type === 'treemap') {
      var tn = Math.min(6, points);
      p.labels = labels.slice(0, tn);
      p.data = values(5, 40).slice(0, tn);
      p.colors = COLOR_KEYS.slice(0, tn);
    } else if (type === 'box') {
      p.boxes = [];
      for (var b = 0; b < Math.min(4, points); b++) {
        var lo = rnd(2, 10), q1 = lo + rnd(2, 6), med = q1 + rnd(1, 5),
            q3 = med + rnd(1, 5), hi = q3 + rnd(2, 7);
        p.boxes.push({ label: 'S' + (b + 1), min: lo, q1: q1, median: med, q3: q3, max: hi });
      }
    } else if (type === 'range') {
      p.items = labels.slice(0, Math.min(4, points)).map(function (l) {
        var a = rnd(1, 5), b = a + rnd(2, 6);
        return { label: l, from: a, to: b };
      });
      p.xLabel = 'confidence';
    } else if (type === 'slope') {
      p.items = labels.slice(0, Math.min(5, points)).map(function (l) {
        return { label: l, before: rnd(5, 30), after: rnd(5, 30) };
      });
      p.aLabel = 'before'; p.bLabel = 'after';
    } else if (type === 'combo') {
      p.labels = labels;
      p.bars = values(20, 120);
      p.line = values(2, 60);
      p.barLabel = 'requests'; p.lineLabel = 'p95 (ms)';
    } else if (type === 'timeline') {
      p.events = labels.map(function (l, i) {
        return { label: l, at: points > 1 ? i / (points - 1) : 0 };
      });
    } else if (type === 'bubble') {
      p.data = labels.map(function () { return [rnd(2, 20), rnd(2, 20), rnd(2, 8)]; });
      p.xLabel = 'latency'; p.yLabel = 'throughput';
    } else if (type === 'dumbbell') {
      p.items = labels.slice(0, Math.min(5, points)).map(function (l) {
        return { label: l, a: rnd(5, 30), b: rnd(5, 30) };
      });
      p.aLabel = 'before'; p.bLabel = 'after';
    } else if (type === 'quadrant') {
      p.q1 = 'scale'; p.q2 = 'invest'; p.q3 = 'watch'; p.q4 = 'drop';
      p.data = labels.map(function () { return [rnd(1, 10), rnd(1, 10)]; });
    } else if (type === 'process' || type === 'cycle') {
      p.steps = labels.slice(0, Math.min(5, points));
    } else if (type === 'progress') {
      p.items = labels.slice(0, Math.min(4, points)).map(function (l) {
        var a = rnd(20, 80);
        return { label: l, parts: [{ value: a, color: 'green' }, { value: 100 - a, color: 'slate' }] };
      });
    } else if (type === 'table') {
      p.columns = ['Stage', 'p50', 'p95', 'Error'];
      p.rows = labels.slice(0, Math.min(6, points)).map(function (l) {
        return [l, rnd(3, 40) + ' ms', rnd(10, 90) + ' ms', (rnd(0, 9) / 10) + '%'];
      });
    } else if (type === 'bar' || type === 'hbar' || type === 'area') {
      p.labels = labels;
      p.data = values(5, 40);
    } else {
      p.labels = labels;
      p.data = values(5, 40);
    }
    return p;
  }

  function makePipeline(n) {
    n = clampInt(n, 2, 8, 4);
    var stages = [];
    for (var i = 0; i < n; i++) {
      var p = NODE_POOL[i % NODE_POOL.length];
      stages.push({ label: p.label, sub: p.sub, logo: p.logo });
    }
    return {
      module: 'pipeline',
      title: 'Pipeline — ' + n + ' stages',
      stages: stages,
      color: 'cyan',
      cable: 'solid',
      motion: 'packets',
      speed: 1,
      items: Math.max(2, n)
    };
  }

  function makeGraph(n, pattern) {
    n = clampInt(n, 3, 12, 8);
    pattern = pattern || 'tree';
    var nodes = [], edges = [];
    var perRow = Math.ceil(Math.sqrt(n));
    for (var i = 0; i < n; i++) {
      nodes.push({
        id: 'n' + i,
        x: 100 + (i % perRow) * 220,
        y: 70 + Math.floor(i / perRow) * 105,
        label: String.fromCharCode(65 + i),
        logo: i === 0 ? 'stack:docker' : null
      });
    }
    if (pattern === 'line') {
      for (var k = 0; k < n - 1; k++) {
        edges.push({ from: 'n' + k, to: 'n' + (k + 1), w: (k % 5) + 1 });
      }
    } else if (pattern === 'random') {
      for (var r = 1; r < n; r++) {
        edges.push({ from: 'n' + r, to: 'n' + Math.floor(Math.random() * r), w: (r % 6) + 1 });
      }
      for (var e = 0; e < Math.max(1, Math.floor(n / 3)); e++) {
        var a = Math.floor(Math.random() * n);
        var b = Math.floor(Math.random() * n);
        if (a !== b && !edges.some(function (x) {
          return (x.from === 'n' + a && x.to === 'n' + b) || (x.from === 'n' + b && x.to === 'n' + a);
        })) edges.push({ from: 'n' + a, to: 'n' + b, w: (e % 5) + 1 });
      }
    } else {
      for (var t = 1; t < n; t++) {
        edges.push({ from: 'n' + Math.floor((t - 1) / 2), to: 'n' + t, w: (t % 6) + 1 });
      }
    }
    return {
      module: 'graph',
      title: 'Graph — ' + n + ' nodes',
      color: 'green',
      start: 'n0',
      nodes: nodes,
      edges: edges,
      pattern: pattern
    };
  }

  var PRESETS = {
    flow: [
      ['stack4', 'Stack 4 — chain', function () { return makeFlow(4, 1, 'bipartite'); }],
      ['solo', 'Solo — 1 node', function () { return makeFlow(1, 1, 'bipartite'); }],
      ['chain2', 'Chain ×2', function () { return makeFlow(2, 1, 'chain'); }],
      ['chain3', 'Chain ×3', function () { return makeFlow(3, 1, 'chain'); }],
      ['fan', 'Fan-out 1→3', function () { return makeFlow(2, 3, 'fan'); }],
      ['layered', 'Layered 4×2', function () { return makeFlow(4, 2, 'bipartite'); }],
      ['vertical', 'Vertical 3', function () { var s = makeFlow(3, 1, 'chain'); s.vertical = true; return s; }],
      ['flow-logos', 'Request path with logos', function () { return JSON.parse(JSON.stringify({"module":"flow","title":"Request path with logos","cable":"neon","motion":"comet","columns":[["client"],["edge"],["app1","app2"],["db"],["sec1","sec2"]],"nodes":{"client":{"label":"Client","sub":"browser","logo":"stack:github","color":"blue"},"edge":{"label":"Edge","sub":"nginx","logo":"stack:nginx","color":"cyan"},"app1":{"label":"App A","sub":"node","logo":"programming:nodejs","color":"green"},"app2":{"label":"App B","sub":"python","logo":"programming:python","color":"amber"},"db":{"label":"Data","sub":"postgres + redis","logos":["stack:postgresql","stack:redis"],"color":"purple"},"sec1":{"label":"Wireshark","sub":"capture","logo":"security:wireshark","color":"lime"},"sec2":{"label":"Nmap","sub":"scan","logo":"security:nmap","color":"amber"}},"edges":[["client","edge","TLS"],["edge","app1"],["edge","app2"],["app1","db"],["app2","db"],["app1","sec1"],["app2","sec2"]]})); }],
      ['cable-styles', 'Cable styles', function () { return JSON.parse(JSON.stringify({"module":"flow","title":"Cable styles","cable":"solid","columns":[["a","b","c"],["d","e","f"]],"nodes":{"a":{"label":"Alpha","color":"blue"},"b":{"label":"Beta","color":"green"},"c":{"label":"Gamma","color":"amber"},"d":{"label":"Delta","color":"purple"},"e":{"label":"Epsilon","color":"cyan"},"f":{"label":"Zeta","color":"pink"}},"edges":[{"from":"a","to":"d","cable":"neon","motion":"none"},{"from":"b","to":"e","cable":"bundle","motion":"none"},{"from":"c","to":"f","cable":"relay","motion":"none"},{"from":"a","to":"d","cable":"ribbon","motion":"none"},{"from":"b","to":"e","cable":"dashed","motion":"none"},{"from":"c","to":"f","cable":"circuit","motion":"none"}]})); }],
      ['motion-effects', 'Motion effects', function () { return JSON.parse(JSON.stringify({"module":"flow","title":"Motion effects","cable":"solid","columns":[["a","b","c"],["d","e","f"]],"nodes":{"a":{"label":"Alpha","color":"blue"},"b":{"label":"Beta","color":"green"},"c":{"label":"Gamma","color":"amber"},"d":{"label":"Delta","color":"purple"},"e":{"label":"Epsilon","color":"cyan"},"f":{"label":"Zeta","color":"pink"}},"edges":[{"from":"a","to":"d","motion":"comet"},{"from":"b","to":"e","motion":"packets"},{"from":"c","to":"f","motion":"flowMany"},{"from":"a","to":"d","motion":"dash"},{"from":"b","to":"e","motion":"draw"},{"from":"c","to":"f","motion":"relay"}]})); }]
    ],
    'reverse-proxy': [
      ['triple', '3 backends', function () { return makeProxy(3); }],
      ['solo', '1 backend', function () { return makeProxy(1); }],
      ['pair', '2 backends', function () { return makeProxy(2); }],
      ['five', '5 backends', function () { return makeProxy(5); }],
      ['eight', '8 backends', function () { return makeProxy(8); }],
      ['proxy-doc', 'Reverse proxy — one front, many backends', function () { return JSON.parse(JSON.stringify({"module":"reverse-proxy","title":"Reverse Proxy: Single Front, Many Backends","speed":1})); }]
    ],
    chart: [
      ['single', 'Single series', function () { return chartPreset('line', 1, 7); }],
      ['dual', 'Dual series', function () { return chartPreset('line', 2, 7); }],
      ['ranking', 'Ranking 8', function () { return chartPreset('hbar', 1, 8); }],
      ['trend', 'Trend 12', function () { return chartPreset('area', 1, 12); }],
      ['mix', 'Donut 5', function () { return chartPreset('donut', 1, 5); }],
      ['bar-1', 'Bar', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"bar","title":"Bar","labels":["Jan","Feb","Mar","Apr","May"],"data":[12,18,15,22,28],"color":"blue"})); }],
      ['hbar-2', 'Horizontal bar ranking', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"hbar","title":"Horizontal bar ranking","labels":["Nginx","Postgres","Redis","PHP","Go"],"data":[42,31,24,18,12],"color":"cyan"})); }],
      ['line-3', 'Multi-series line', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"line","title":"Multi-series line","labels":["Mon","Tue","Wed","Thu","Fri"],"series":[{"name":"web","data":[12,18,15,22,28],"color":"blue"},{"name":"api","data":[8,11,14,12,18],"color":"green"}]})); }],
      ['area-4', 'Area', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"area","title":"Area","labels":["Mon","Tue","Wed","Thu","Fri"],"data":[8,12,10,16,20],"color":"cyan"})); }],
      ['stacked-5', 'Stacked bar composition', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"stacked","title":"Stacked bar composition","labels":["Mon","Tue","Wed","Thu"],"series":[{"name":"web","data":[12,14,10,16],"color":"blue"},{"name":"api","data":[8,9,12,11],"color":"green"},{"name":"job","data":[5,6,4,7],"color":"amber"}]})); }],
      ['donut-6', 'Donut percent breakdown', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"donut","title":"Donut percent breakdown","labels":["Web","API","DB","Cache"],"data":[38,27,21,14],"colors":["blue","green","amber","purple"],"centerLabel":"requests"})); }],
      ['gauge-7', 'Single-value percent gauge', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"gauge","title":"Single-value percent gauge","data":[68],"max":100,"unit":"%","label":"cache hit","color":"cyan"})); }],
      ['spark-8', 'Spark line', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"spark","title":"Spark line","data":[3,5,4,7,6,9,8,11],"color":"green"})); }],
      ['kpi-9', 'KPI callout', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"kpi","title":"KPI callout","data":[128],"label":"requests / sec","delta":"+12.4%"})); }],
      ['scatter-10', 'Scatter plot', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"scatter","title":"Scatter plot","data":[[3,5],[5,8],[8,7],[11,12],[14,13],[17,18],[20,17]],"color":"purple"})); }],
      ['waterfall-11', 'Waterfall', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"waterfall","title":"Waterfall","labels":["Start","Add","Cache","Drop","End"],"data":[40,18,12,-9,21],"color":"blue"})); }],
      ['funnel-12', 'Funnel conversion', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"funnel","title":"Funnel conversion","labels":["Visit","Signup","Active","Paid"],"data":[100,62,38,17],"colors":["blue","cyan","green","amber"]})); }],
      ['bell-13', 'Bell curve with marker', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"bell","title":"Bell curve with marker","mean":0,"sigma":1,"marker":0.6,"markerLabel":"p95","color":"blue"})); }],
      ['histogram-14', 'Histogram', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"histogram","title":"Histogram","bins":8,"data":[1,2,2,3,3,3,4,4,4,5,5,6],"color":"cyan"})); }],
      ['stackedarea-15', 'Stacked area trend', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"stackedArea","title":"Stacked area trend","labels":["Mon","Tue","Wed","Thu","Fri"],"series":[{"name":"web","data":[8,10,9,12,14],"color":"blue"},{"name":"api","data":[5,6,7,6,9],"color":"green"},{"name":"job","data":[3,4,3,5,6],"color":"amber"}]})); }],
      ['treemap-16', 'Treemap', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"treemap","title":"Treemap","labels":["Web","API","DB","Cache","Queue"],"data":[38,27,18,11,6],"colors":["blue","green","amber","purple","pink"]})); }],
      ['box-17', 'Box plot', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"box","title":"Box plot","boxes":[{"label":"Web","min":2,"q1":5,"median":8,"q3":11,"max":14},{"label":"API","min":3,"q1":6,"median":9,"q3":12,"max":16},{"label":"DB","min":1,"q1":4,"median":7,"q3":10,"max":13}]})); }],
      ['range-18', 'Range bar with thresholds', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"range","title":"Range bar with thresholds","items":[{"label":"p50","from":20,"to":60},{"label":"p95","from":70,"to":140},{"label":"p99","from":150,"to":260}],"color":"amber"})); }],
      ['density-19', 'Density curve', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"density","title":"Density curve","series":[{"name":"web","data":[0.05,0.2,0.6,0.9,0.6,0.2,0.05],"color":"blue"},{"name":"api","data":[0.1,0.3,0.5,0.7,0.5,0.3,0.1],"color":"amber"}]})); }],
      ['slope-20', 'Slope chart', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"slope","title":"Slope chart","items":[{"label":"Web","before":20,"after":48},{"label":"API","before":35,"after":28},{"label":"DB","before":12,"after":26}],"color":"cyan"})); }],
      ['combo-21', 'Two-axis combo', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"combo","title":"Two-axis combo","labels":["Mon","Tue","Wed","Thu","Fri"],"bars":[120,140,130,160,180],"line":[3,4,3.5,5,6],"color":"blue"})); }],
      ['timeline-22', 'Annotated timeline', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"timeline","title":"Annotated timeline","events":[{"label":"deploy","at":0.1},{"label":"cache warm","at":0.35},{"label":"peak","at":0.6},{"label":"rollback drill","at":0.85}],"color":"green"})); }],
      ['bubble-23', 'Bubble chart', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"bubble","title":"Bubble chart","data":[[3,4,2],[5,7,4],[8,6,3],[11,9,5],[14,12,6],[17,11,4]],"color":"purple"})); }],
      ['dumbbell-24', 'Dumbbell plot', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"dumbbell","title":"Dumbbell plot","items":[{"label":"Web","a":20,"b":48},{"label":"API","a":35,"b":28},{"label":"DB","a":12,"b":26}]})); }],
      ['quadrant-25', 'Quadrant matrix', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"quadrant","title":"Quadrant matrix","q1":"scale","q2":"invest","q3":"fix","q4":"watch","data":[[2,8],[5,6],[7,3],[9,7],[4,4]],"color":"cyan"})); }],
      ['process-26', 'Process flow steps', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"process","title":"Process flow steps","steps":["plan","build","test","ship"],"color":"green"})); }],
      ['cycle-27', 'Cycle loop stages', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"cycle","title":"Cycle loop stages","steps":["plan","build","test","ship"],"color":"purple"})); }],
      ['progress-28', 'Progress bar stack', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"progress","title":"Progress bar stack","items":[{"label":"Web","parts":[{"value":60,"color":"blue"},{"value":25,"color":"green"},{"value":15,"color":"amber"}]},{"label":"API","parts":[{"value":40,"color":"cyan"},{"value":35,"color":"purple"},{"value":25,"color":"pink"}]}]})); }],
      ['table-29', 'Comparison table', function () { return JSON.parse(JSON.stringify({"module":"chart","type":"table","title":"Comparison table","columns":["Tool","Speed","Cost","Use"],"rows":[["Nginx","fast","low","edge"],["Postgres","medium","medium","data"],["Redis","fast","high","cache"]]})); }],
    ],
    pipeline: [
      ['duo', '2 stages', function () { return makePipeline(2); }],
      ['triple', '3 stages', function () { return makePipeline(3); }],
      ['quad', '4 stages', function () { return makePipeline(4); }],
      ['six', '6 stages', function () { return makePipeline(6); }],
      ['eight', '8 stages', function () { return makePipeline(8); }],
      ['pipeline-doc', 'Request pipeline', function () { return JSON.parse(JSON.stringify({"module":"pipeline","title":"Request pipeline","stages":[{"label":"Client","logo":"stack:github"},{"label":"Edge","logo":"stack:nginx"},{"label":"App","logo":"programming:nodejs"},{"label":"DB","logo":"stack:postgresql"}],"color":"cyan","items":4})); }]
    ],
    canvas: [
      ['blank', 'Blank canvas', makeCanvas],
      ['starter', 'Starter — 3 boxes', function () {
        var s = makeCanvas();
        s.nodes = {
          n1: { id: 'n1', x: 90, y: 110, w: 160, h: 60, shape: 'box', label: 'Client', sub: 'browser', color: 'blue', logo: 'stack:github' },
          n2: { id: 'n2', x: 370, y: 110, w: 160, h: 60, shape: 'box', label: 'API', sub: 'node', color: 'green', logo: 'programming:nodejs' },
          n3: { id: 'n3', x: 650, y: 110, w: 160, h: 60, shape: 'box', label: 'DB', sub: 'postgres', color: 'purple', logo: 'stack:postgresql' }
        };
        s.edges = [
          { from: 'n1', to: 'n2' },
          { from: 'n2', to: 'n3' }
        ];
        return s;
      }]
    ],
    graph: [
      ['tree', 'Tree 7', function () { return makeGraph(7, 'tree'); }],
      ['line', 'Line 5', function () { return makeGraph(5, 'line'); }],
      ['random', 'Random 9', function () { return makeGraph(9, 'random'); }],
      ['wide', 'Wide 12', function () { return makeGraph(12, 'tree'); }],
      ['graph-doc', 'BFS traversal', function () { return JSON.parse(JSON.stringify({"module":"graph","title":"BFS traversal","color":"green","start":"a","nodes":[{"id":"a","x":140,"y":90,"label":"A","logo":"stack:docker"},{"id":"b","x":330,"y":60,"label":"B"},{"id":"c","x":330,"y":150,"label":"C"},{"id":"d","x":520,"y":40,"label":"D"},{"id":"e","x":520,"y":120,"label":"E","logo":"stack:kubernetes"},{"id":"f","x":520,"y":200,"label":"F"},{"id":"g","x":710,"y":80,"label":"G","logo":"stack:prometheus"},{"id":"h","x":710,"y":170,"label":"H","logo":"stack:grafana"}],"edges":[{"from":"a","to":"b","w":4},{"from":"a","to":"c","w":2},{"from":"b","to":"d","w":5},{"from":"b","to":"e","w":3},{"from":"c","to":"e","w":2},{"from":"c","to":"f","w":6},{"from":"d","to":"g","w":4},{"from":"e","to":"g","w":2},{"from":"e","to":"h","w":5},{"from":"f","to":"h","w":3}]})); }]
    ]
  };

  function presetFor(id) {
    var list = PRESETS[id] || PRESETS.flow;
    return list[0][2]();
  }

  function presetById(module, id) {
    var list = PRESETS[module] || [];
    var out = null;
    list.forEach(function (p) { if (p[0] === id) out = p[2](); });
    return out;
  }

  /* Ukuran awal blok modul saat masuk kanvas. */
  var MODULE_DIMS = {
    flow: [420, 260],
    chart: [380, 240],
    pipeline: [440, 200],
    graph: [380, 260],
    'reverse-proxy': [460, 280],
    table: [440, 220]
  };

  var SAVE_KEY = 'ruang.scene.v1';
  var MODULE_IDS = ['canvas', 'flow', 'reverse-proxy', 'chart', 'pipeline', 'graph'];
  /* First visit opens on the editable three-box starter, not an empty page.
     The blank canvas is still one click away in the Scene panel. */
  var state = { spec: PRESETS.canvas[1][2]() };

  try {
    var savedScene = localStorage.getItem(SAVE_KEY);
    if (savedScene) {
      var parsedScene = JSON.parse(savedScene);
      if (parsedScene && MODULE_IDS.indexOf(parsedScene.module) >= 0) state.spec = parsedScene;
    }
  } catch (err) {}

  var stage = document.getElementById('stage');
  /* The raw JSON editor is gone — the canvas is the only source of truth.
     A stub keeps the remaining sync helpers working without a textarea. */
  var specBox = { value: '' };

  function fillSelect(sel, items) {
    items.forEach(function (it) {
      var o = document.createElement('option');
      o.value = it.id;
      o.textContent = it.label;
      sel.appendChild(o);
    });
  }

  fillSelect(document.getElementById('cable'), CABLES);
  fillSelect(document.getElementById('motion'), MOTIONS);

  /* Logo picker ---------------------------------------------------------- */

  var LOGOS = window.AlurLogos;
  var logoState = { cat: 'all', q: '', limit: 96, target: null };

  function logoTargets() {
    var s = state.spec;
    if (s.module === 'flow') {
      return Object.keys(s.nodes || {}).map(function (id) {
        return { id: id, node: s.nodes[id] };
      });
    }
    if (s.module === 'pipeline') {
      return (s.stages || []).map(function (st, i) {
        return { id: String(i), node: st };
      });
    }
    if (s.module === 'graph') {
      return (s.nodes || []).map(function (n) {
        return { id: n.id, node: n };
      });
    }
    if (s.module === 'canvas') {
      return Object.keys(s.nodes || {}).map(function (id) {
        return { id: id, node: s.nodes[id] };
      }).filter(function (t) {
        return t.node && t.node.shape !== 'image' && t.node.shape !== 'table' && t.node.shape !== 'module';
      });
    }
    if (s.module === 'reverse-proxy') {
      s.nodes = s.nodes || {};
      var list = [];
      ['client', 'proxy'].forEach(function (key) {
        if (!s.nodes[key]) {
          s.nodes[key] = { label: key === 'client' ? 'Client' : 'Reverse Proxy' };
        }
        list.push({ id: key, node: s.nodes[key] });
      });
      var count = s.backends || 3;
      for (var i = 1; i <= count; i++) {
        var bkey = 'backend' + i;
        if (!s.nodes[bkey]) s.nodes[bkey] = { label: 'Backend ' + i };
        list.push({ id: bkey, node: s.nodes[bkey] });
      }
      return list;
    }
    return [];
  }

  function logoTarget() {
    var targets = logoTargets();
    var ids = selectionIds();
    if (ids.length === 1) {
      for (var j = 0; j < targets.length; j++) {
        if (targets[j].id === ids[0]) return targets[j];
      }
    }
    for (var i = 0; i < targets.length; i++) {
      if (targets[i].id === logoState.target) return targets[i];
    }
    return targets[0] || null;
  }

  function logoIdsOf(node) {
    var ids = [];
    if (!node) return ids;
    if (node.logo) ids.push(node.logo);
    (node.logos || []).forEach(function (id) { ids.push(id); });
    return ids;
  }

  function logoThumb(id, cls) {
    var res = LOGOS.resolve(id);
    var img = document.createElement('img');
    img.alt = id;
    img.loading = 'eager';
    if (res && res.kind === 'file') {
      img.src = res.href;
    } else {
      /* sprite id: show a neutral placeholder tile */
      img.removeAttribute('src');
      img.style.display = 'none';
    }
    var wrap = document.createElement('div');
    wrap.className = 'thumb' + (cls ? ' ' + cls : '');
    wrap.appendChild(img);
    if (!res || res.kind !== 'file') wrap.textContent = '◆';
    return wrap;
  }

  function renderLogoPreview() {
    var host = document.getElementById('logoPreview');
    host.innerHTML = '';
    var cur = logoTarget();
    var node = cur && cur.node;
    var ids = logoIdsOf(node);
    if (!ids.length) {
      host.innerHTML = '';
      return;
    }
    ids.forEach(function (id) {
      var res = LOGOS.resolve(id);
      var thumb = logoThumb(id, LOGOS.isDark(id) ? 'dark' : '');
      thumb.title = id;
      host.appendChild(thumb);
    });
  }

  function syncLogoCats() {
    var host = document.getElementById('logoCats');
    host.innerHTML = '';
    var cats = [{ id: 'all', label: 'All', count: LOGOS.total }].concat(LOGOS.categories());
    cats.forEach(function (c) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'chip' + (logoState.cat === c.id ? ' is-on' : '');
      b.textContent = c.label + ' · ' + c.count;
      b.addEventListener('click', function () {
        logoState.cat = c.id;
        logoState.limit = 96;
        syncLogoCats();
        renderLogoGrid(true);
      });
      host.appendChild(b);
    });
  }

  /* Template: satu daftar, satu aksi. Klik = sisipkan sebagai blok yang bisa
     diedit. Tidak ada lagi "Add to canvas" vs "Replace scene" yang bikin
     bingung dan menghapus kerjaan. */
  function renderTemplateList() {
    var host = document.getElementById('templateList');
    if (!host) return;
    host.innerHTML = '';
    TEMPLATE_GROUPS.forEach(function (group) {
      var module = group[0];
      var head = document.createElement('div');
      head.className = 'tpl-group';
      head.textContent = group[1];
      host.appendChild(head);
      (PRESETS[module] || []).forEach(function (p) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'block-item';
        b.setAttribute('data-template-module', module);
        b.setAttribute('data-template-id', p[0]);
        b.title = p[1];
        b.innerHTML = '<span class="blk-text"><b>' + p[1] + '</b></span>';
        host.appendChild(b);
      });
    });
    Array.prototype.forEach.call(host.querySelectorAll('[data-template-module]'), function (btn) {
      btn.addEventListener('click', function () {
        insertTemplateBlock(btn.getAttribute('data-template-module'),
          btn.getAttribute('data-template-id'));
      });
    });
  }

  /* Satu sumber untuk daftar blok. Tambah jenis baru = tambah satu baris di
     sini; nomornya dihitung sendiri, tidak ada tombol "+" yang aneh. */
  var BLOCK_TYPES = [
    { id: 'flow', label: 'Flow', hint: 'boxes and arrows' },
    { id: 'chart', label: 'Chart', hint: 'bar, line, donut, kpi …' },
    { id: 'pipeline', label: 'Pipeline', hint: 'ordered stages' },
    { id: 'graph', label: 'Graph', hint: 'nodes and frontier' },
    { id: 'reverse-proxy', label: 'Reverse Proxy', hint: 'one front, many backends' },
    { id: 'table', label: 'Table', hint: 'editable rows' }
  ];

  /* Panel 3 saat belum ada blok chart dipilih: daftar jenis untuk ditambah.
     Tidak ada data contoh — blok baru lahir kosong dan membaca objek canvas. */
  var QUICK_CHART_TYPES = ['bar', 'line', 'donut', 'kpi', 'gauge', 'table'];

  function renderChartQuickList() {
    var host = document.getElementById('chartQuickList');
    if (!host) return;
    host.innerHTML = '';
    QUICK_CHART_TYPES.forEach(function (t) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'block-item';
      b.title = 'Add ' + t + ' block';
      b.innerHTML = '<span class="blk-text"><b>' + t + '</b></span>';
      b.addEventListener('click', function () { insertChartBlock(t); });
      host.appendChild(b);
    });
  }

  /* Start from what is already on the canvas so a fresh chart is never empty
     and never a flat row of 1s. */
  function defaultChartData() {
    var nodes = chartSourceNodes();
    return nodes.slice(0, 12).map(function (nd, i) {
      return (nd.label || nd.id || 'node ' + (i + 1)) + ' = 1';
    }).join('\n');
  }

  /* Chart is a canvas object like every other block: a real node that is
     selected, moved, resized and deleted the same way. Not a module card. */
  function insertChartBlock(type) {
    pushHistory();
    ensureCanvasForBlock();
    var d = MODULE_DIMS.chart || [380, 240];
    var s = state.spec;
    var sr = stage.getBoundingClientRect();
    var svg = stage.querySelector('svg');
    var scale = Math.min(1, Math.max(0.55, (sr.width - 48) / d[0]));
    var w = Math.round(d[0] * scale);
    var h = Math.round(d[1] * scale);
    var same = Object.keys(s.nodes || {}).filter(function (k) {
      return s.nodes[k] && s.nodes[k].shape === 'chart';
    }).length;
    var free = freeViewport();
    var anchor = svg ? svgPoint(svg, {
      clientX: free.left + (free.right - free.left) / 2 - w / 2 + (same % 3) * 28,
      clientY: free.top + (free.bottom - free.top) / 2 - h / 2 + (same % 3) * 24
    }) : viewportSceneCenter();
    var ax = (anchor && anchor.x) || 0;
    var ay = (anchor && anchor.y) || 0;
    s.nodes = s.nodes || {};
    var nid;
    do { nid = 'n' + (++nodeSeq); } while (s.nodes[nid]);
    s.nodes[nid] = {
      id: nid,
      x: snapGrid(ax + (same % 3) * 28),
      y: snapGrid(ay + (same % 3) * 24),
      w: w,
      h: h,
      shape: 'chart',
      chartType: type || 'bar',
      dataSource: 'manual',
      chartData: defaultChartData(),
      agg: 'count',
      groupBy: 'sub',
      label: '',
      color: COLOR_KEYS[Object.keys(s.nodes).length % COLOR_KEYS.length]
    };
    s.selected = nid;
    s.selectedEdge = null;
    s.selectedEdges = [];
    s.selectedDrawing = null;
    refreshCanvasChartSpecs();
    touchSpec();
    syncControls();
    syncChartDataPanel();
    render();
  }

  function renderBlockList() {
    var host = document.getElementById('blockList');
    if (!host) return;
    host.innerHTML = '';
    BLOCK_TYPES.forEach(function (t) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'block-item';
      b.setAttribute('data-scene-module', t.id);
      b.title = t.label + ' — ' + t.hint;
      b.innerHTML = '<span class="blk-text"><b>' + t.label + '</b></span>';
      host.appendChild(b);
    });
    Array.prototype.forEach.call(host.querySelectorAll('[data-scene-module]'), function (btn) {
      btn.addEventListener('click', function () {
        var id = btn.getAttribute('data-scene-module');
        if (id === 'table') insertTableBlock();
        else insertModule(id);
      });
    });
  }

  function renderLogoGrid(resetScroll) {
    var grid = document.getElementById('logoGrid');
    var keepScroll = resetScroll ? 0 : grid.scrollTop;
    var hits = LOGOS.search(logoState.q, logoState.cat);
    var shown = hits.slice(0, logoState.limit);
    var cur = logoTarget();
    var on = {};
    logoIdsOf(cur && cur.node).forEach(function (id) { on[id] = true; });

    grid.innerHTML = '';
    shown.forEach(function (e) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'logo-tile' + (e.dark ? ' dark' : '') + (on[e.id] ? ' is-on' : '');
      b.title = e.id;
      var art = document.createElement('span');
      art.className = 'lg-art';
      var img = document.createElement('img');
      img.loading = 'eager';
      img.alt = e.name;
      img.draggable = false;
      var res = LOGOS.resolve(e.id);
      if (res && res.kind === 'file') img.src = res.href;
      art.appendChild(img);
      b.appendChild(art);
      var cap = document.createElement('span');
      cap.className = 'lg-name';
      cap.textContent = e.name;
      b.appendChild(cap);
      b.addEventListener('click', function (ev) {
        if (editor.suppressLogoClick) { editor.suppressLogoClick = false; return; }
        applyLogo(e.id, ev.shiftKey);
      });
      b.addEventListener('pointerdown', function (ev) {
        if (ev.button !== 0) return;
        var logoId = e.id;
        var startX = ev.clientX;
        var startY = ev.clientY;
        var dragging = false;
        var ghost = null;
        var pointerId = ev.pointerId;

        function move(e) {
          if (!dragging && Math.hypot(e.clientX - startX, e.clientY - startY) < 6) return;
          if (!dragging) {
            dragging = true;
            editor.suppressLogoClick = true;
            ghost = document.createElement('div');
            ghost.className = 'logo-drag-ghost';
            var gi = document.createElement('img');
            gi.src = img.src;
            gi.alt = '';
            ghost.appendChild(gi);
            document.body.appendChild(ghost);
            b.classList.add('is-dragging');
          }
          ghost.style.left = e.clientX + 'px';
          ghost.style.top = e.clientY + 'px';
          var under = document.elementFromPoint(e.clientX, e.clientY);
          var over = !!(under && under.closest && under.closest('#stage'));
          ghost.classList.toggle('is-over', over);
        }

        function cleanup() {
          window.removeEventListener('pointermove', move);
          window.removeEventListener('pointerup', up);
          window.removeEventListener('pointercancel', cancel);
          b.classList.remove('is-dragging');
          if (ghost && ghost.parentNode) ghost.parentNode.removeChild(ghost);
          if (dragging) setTimeout(function () { editor.suppressLogoClick = false; }, 250);
        }

        function up(e) {
          var wasDragging = dragging;
          var over = false;
          if (wasDragging) {
            var under = document.elementFromPoint(e.clientX, e.clientY);
            over = !!(under && under.closest && under.closest('#stage'));
          }
          cleanup();
          if (!wasDragging || !over) return;
          var svg = stage.querySelector('svg');
          if (!svg) return;
          var pt = svgPoint(svg, e);
          dropLogo(logoId, pt.x, pt.y);
        }

        function cancel() { cleanup(); }

        window.addEventListener('pointermove', move);
        window.addEventListener('pointerup', up);
        window.addEventListener('pointercancel', cancel);
      });
      grid.appendChild(b);
    });

    document.getElementById('logoStatus').textContent =
      hits.length + ' logo' + (hits.length === 1 ? '' : 's') +
      (hits.length > shown.length ? ' · showing ' + shown.length : '');
    grid.scrollTop = keepScroll;
  }

  function addImageNode(src, w, h, x, y) {
    if (!isCanvas()) switchModule('canvas');
    pushHistory();
    var s = state.spec;
    s.nodes = s.nodes || {};
    var id;
    do { id = 'n' + (++nodeSeq); } while (s.nodes[id]);
    s.nodes[id] = {
      id: id,
      x: Math.round(x),
      y: Math.round(y),
      w: Math.max(24, Math.round(w)),
      h: Math.max(24, Math.round(h)),
      shape: 'image',
      src: src,
      label: '',
      sub: '',
      color: '#e6edf3'
    };
    s.selected = id;
    s.selectedEdge = null;
    s.selectedEdges = [];
    s.selectedDrawing = null;
    touchSpec();
    syncControls();
    syncEditor();
    render();
    return id;
  }

  function addImageFile(file, clientX, clientY) {
    if (!file || !/^image\//.test(file.type || '')) return;
    if (!isCanvas()) switchModule('canvas');
    var reader = new FileReader();
    reader.onload = function () {
      var img = new Image();
      img.onload = function () {
        var maxW = 960, maxH = 640;
        var ratio = Math.min(1, maxW / Math.max(1, img.naturalWidth),
                                maxH / Math.max(1, img.naturalHeight));
        var w = Math.max(80, Math.round(img.naturalWidth * ratio));
        var h = Math.max(60, Math.round(img.naturalHeight * ratio));
        var src = reader.result;
        if (file.size > 1200000) {
          try {
            var cv = document.createElement('canvas');
            cv.width = w; cv.height = h;
            var cx = cv.getContext('2d');
            cx.drawImage(img, 0, 0, w, h);
            src = file.type === 'image/png' || file.type === 'image/webp'
              ? cv.toDataURL('image/png')
              : cv.toDataURL('image/jpeg', 0.86);
          } catch (err) {}
        }
        var svg = stage.querySelector('svg');
        var pt = (svg && typeof clientX === 'number')
          ? svgPoint(svg, { clientX: clientX, clientY: clientY })
          : viewportSceneCenter();
        addImageNode(src, w, h, pt.x - w / 2, pt.y - h / 2);
      };
      img.onerror = function () { alert('That image could not be read.'); };
      img.src = reader.result;
    };
    reader.readAsDataURL(file);
  }

  function dropLogo(id, x, y) {
    if (!isCanvas()) switchModule('canvas');
    var target = nodeAtPoint(x, y);
    if (target && state.spec.nodes[target]) {
      pushHistory();
      var node = state.spec.nodes[target];
      node.logo = id;
      delete node.logos;
      state.spec.selected = target;
      state.spec.selectedEdge = null;
      state.spec.selectedEdges = [];
      state.spec.selectedDrawing = null;
      logoState.last = id;
      syncControls();
      syncLogoPanel();
      render();
      return;
    }
    pushHistory();
    var nid = addNode('none', x - 48, y - 48, 96, 96);
    var s = state.spec;
    if (nid && s.nodes[nid]) {
      s.nodes[nid].logo = id;
      s.nodes[nid].logoSize = 64;
      delete s.nodes[nid].logos;
    }
    logoState.last = id;
    syncControls();
    syncLogoPanel();
    render();
  }

  function insertTableBlock() {
    pushHistory();
    ensureCanvasForBlock();
    var c = viewportSceneCenter();
    var id = addNode('table', c.x - 210, c.y - 120, 420, 240);
    var n = state.spec.nodes && state.spec.nodes[id];
    if (n) {
      ensureTableData(n);
      n.color = n.color || 'blue';
      revealScene();
      touchSpec();
      syncControls();
      syncEditor();
      render();
    }
  }

  /* Templates and blocks are merged as ordinary nodes and edges. No wrapper
     card, no locked module: everything lands editable, cables included. */
  var NODE_W = 136, NODE_H = 66, GAP_X = 78, GAP_Y = 22;
  /* The canvas grid is minor 22 / major 110 (AlurKit.grid). Everything that
     lands on the canvas snaps to it, so grid is the only mode. */
  var GRID = 22;
  var DRAG_THRESHOLD = 4;

  /* Module presets describe their own layout (or none at all). Flatten them
     into plain canvas nodes so the result is a normal, editable scene. */
  function materializeScene(spec) {
    var out = { nodes: {}, edges: [] };
    if (!spec) return out;
    var mod = spec.module;

    if (mod === 'chart') {
      /* A chart is live: it counts the objects on the canvas instead of
         carrying a frozen snapshot of sample numbers. */
      out.nodes.n0 = {
        id: 'n0', x: 0, y: 0, w: 440, h: 300, shape: 'chart',
        label: spec.title || 'Chart', color: spec.color || 'blue',
        chartType: spec.type || 'bar', dataSource: 'canvas',
        groupBy: 'sub', agg: 'count'
      };
      return out;
    }

    if (mod === 'pipeline') {
      var stages = spec.stages || [];
      stages.forEach(function (st, i) {
        out.nodes['n' + i] = {
          id: 'n' + i, x: i * (NODE_W + GAP_X), y: 0, w: NODE_W, h: NODE_H,
          shape: 'box', label: st.label || ('Stage ' + (i + 1)), sub: st.sub || '',
          logo: st.logo, color: st.color || spec.color || 'blue'
        };
        if (i) out.edges.push({ from: 'n' + (i - 1), to: 'n' + i });
      });
      return out;
    }

    if (!spec.nodes) return out;

    var raw = spec.nodes;
    var list = [];
    if (Array.isArray(raw)) {
      raw.forEach(function (nd) { if (nd) list.push(nd); });
    } else {
      Object.keys(raw).forEach(function (k) {
        if (!raw[k]) return;
        list.push(Object.assign({ __key: k }, raw[k]));
      });
    }

    list.forEach(function (src) {
      var key = src.id || src.__key;
      if (!key) return;
      var copy = Object.assign({}, src);
      delete copy.__key;
      copy.id = String(key);
      if (typeof copy.w !== 'number') copy.w = NODE_W;
      if (typeof copy.h !== 'number') copy.h = NODE_H;
      if (typeof copy.x !== 'number' || typeof copy.y !== 'number') {
        delete copy.x; delete copy.y;
      }
      copy.shape = copy.shape || 'box';
      out.nodes[copy.id] = copy;
    });

    var rawEdges = (spec.edges || []).filter(function (e) {
      return e && out.nodes[e.from] && out.nodes[e.to];
    });
    rawEdges.forEach(function (e) { out.edges.push(Object.assign({}, e)); });

    /* Reverse proxy keeps its cables as real edges: client -> proxy -> each
       backend, so the scene stays wired after it lands on the canvas. */
    if (mod === 'reverse-proxy') {
      var order = Object.keys(out.nodes);
      var client = order.filter(function (k) { return /client/i.test(k); })[0] || order[0];
      var proxy = order.filter(function (k) { return /proxy/i.test(k); })[0];
      var backends = order.filter(function (k) { return /backend/i.test(k); });
      var targets = backends.length ? backends : order.filter(function (k) { return k !== client && k !== proxy; });
      if (proxy) {
        if (client && client !== proxy) out.edges.push({ from: client, to: proxy });
        targets.forEach(function (b) {
          if (b !== proxy && b !== client) out.edges.push({ from: proxy, to: b });
        });
        /* fan out to the right of the proxy */
        if (client) { out.nodes[client].x = 0; out.nodes[client].y = -NODE_H / 2; }
        out.nodes[proxy].x = NODE_W + GAP_X;
        out.nodes[proxy].y = -NODE_H / 2;
        targets.forEach(function (b, i) {
          out.nodes[b].x = (NODE_W + GAP_X) * 2;
          out.nodes[b].y = (i - (targets.length - 1) / 2) * (NODE_H + GAP_Y) - NODE_H / 2;
        });
        return out;
      }
    }

    /* Anything still without a position gets a layered layout driven by the
       edges, so a stack of nodes never lands on top of itself. */
    var missing = Object.keys(out.nodes).filter(function (k) {
      return typeof out.nodes[k].x !== 'number';
    });
    if (missing.length) layoutScene(out);
    return out;
  }

  function layoutScene(scene) {
    var nodes = scene.nodes;
    var ids = Object.keys(nodes);
    var depth = {};
    ids.forEach(function (id) { depth[id] = 0; });
    for (var pass = 0; pass < ids.length + 1; pass++) {
      var moved = false;
      scene.edges.forEach(function (e) {
        if (depth[e.from] == null || depth[e.to] == null) return;
        if (depth[e.to] < depth[e.from] + 1) { depth[e.to] = depth[e.from] + 1; moved = true; }
      });
      if (!moved) break;
    }
    var cols = {};
    ids.forEach(function (id) {
      var d = depth[id] || 0;
      (cols[d] = cols[d] || []).push(id);
    });
    Object.keys(cols).forEach(function (d) {
      var col = cols[d];
      var total = col.length * NODE_H + (col.length - 1) * GAP_Y;
      col.forEach(function (id, i) {
        var nd = nodes[id];
        nd.w = nd.w || NODE_W;
        nd.h = nd.h || NODE_H;
        nd.x = d * (NODE_W + GAP_X);
        nd.y = Math.round(-total / 2 + i * (NODE_H + GAP_Y));
      });
    });
  }

  function sceneBounds(spec) {
    var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    Object.keys((spec && spec.nodes) || {}).forEach(function (k) {
      var n = spec.nodes[k];
      if (!n) return;
      minX = Math.min(minX, n.x || 0);
      minY = Math.min(minY, n.y || 0);
      maxX = Math.max(maxX, (n.x || 0) + (n.w || 0));
      maxY = Math.max(maxY, (n.y || 0) + (n.h || 0));
    });
    if (minX === Infinity) return { x: 0, y: 0, w: 0, h: 0 };
    return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
  }

  function mergeScene(spec) {
    var flat = materializeScene(spec);
    /* A doc-style preset can carry no layout at all; fall back to the module's
       default scene so the insert is never a silent no-op. */
    if (!Object.keys(flat.nodes).length) flat = materializeScene(presetFor((spec && spec.module) || 'flow'));
    var s = state.spec;
    s.nodes = s.nodes || {};
    s.edges = s.edges || [];
    var b = sceneBounds(flat);
    var c = viewportSceneCenter();
    var existing = Object.keys(s.nodes).map(function (k) { return s.nodes[k]; });
    var dx, dy;
    if (existing.length) {
      /* Keep it on screen: to the right of what is already there while that
         still fits in the view, otherwise start a new row underneath. */
      var svgEl = stage.querySelector('svg');
      var vb = svgEl && svgEl.viewBox ? svgEl.viewBox.baseVal : null;
      var viewX = vb && vb.width ? vb.x : 0;
      var viewW = vb && vb.width ? vb.width : 900;
      var viewY = vb && vb.height ? vb.y : 0;
      var viewH = vb && vb.height ? vb.height : 600;
      var maxX = -Infinity, maxY = -Infinity, minY = Infinity;
      existing.forEach(function (nd) {
        maxX = Math.max(maxX, (nd.x || 0) + (nd.w || 0));
        maxY = Math.max(maxY, (nd.y || 0) + (nd.h || 0));
        minY = Math.min(minY, nd.y || 0);
      });
      if (maxX + GRID * 2 + b.w <= viewX + viewW - GRID) {
        dx = snapGrid(maxX + GRID * 2 - b.x);
        dy = snapGrid(minY - b.y);
      } else {
        dx = snapGrid(viewX + GRID - b.x);
        dy = snapGrid(maxY + GRID * 2 - b.y);
      }
    } else {
      dx = snapGrid(c.x - b.w / 2 - b.x);
      dy = snapGrid(c.y - b.h / 2 - b.y);
    }
    var map = {};
    var first = null;
    Object.keys(flat.nodes).forEach(function (k) {
      var src = flat.nodes[k];
      var nid;
      do { nid = 'n' + (++nodeSeq); } while (s.nodes[nid]);
      var copy = Object.assign({}, src);
      copy.id = nid;
      copy.x = snapGrid((src.x || 0) + dx);
      copy.y = snapGrid((src.y || 0) + dy);
      copy.w = snapGrid(src.w || NODE_W);
      copy.h = snapGrid(src.h || NODE_H);
      s.nodes[nid] = copy;
      map[k] = nid;
      if (!first) first = nid;
    });
    flat.edges.forEach(function (e) {
      if (!map[e.from] || !map[e.to]) return;
      s.edges.push(Object.assign({}, e, { from: map[e.from], to: map[e.to] }));
    });
    if (first) {
      s.selected = first;
      s.selectedEdge = null;
      s.selectedEdges = [];
      s.selectedDrawing = null;
    }
    revealScene();
    return first;
  }

  /* An insert must be visible: frame everything that is now on the canvas. */
  /* Reveal only what is off screen. The zoom is left alone unless the new
     content is bigger than the viewport, so inserting never re-frames the
     canvas and never depends on Fit. */
  function revealScene(b) {
    var box = b || sceneBounds(state.spec);
    if (!box.w || !box.h) return;
    var m = viewMetrics();
    var pad = 48;
    var z = m.z;
    var vw = m.vw;
    var vh = m.vh;
    var px = state.spec.panX || 0;
    var py = state.spec.panY || 0;
    var touched = false;
    if (box.w > vw - pad * 2) {
      var zw = clampZoom((m.w - pad * 2) / box.w);
      if (zw < z) { z = zw; vw = m.w / z; vh = m.h / z; touched = true; }
    }
    if (box.h > vh - pad * 2) {
      var zh = clampZoom((m.h - pad * 2) / box.h);
      if (zh < z) { z = zh; vw = m.w / z; vh = m.h / z; touched = true; }
    }
    if (box.x < px + pad) { px = box.x - pad; touched = true; }
    else if (box.x + box.w > px + vw - pad) { px = box.x + box.w - vw + pad; touched = true; }
    if (box.y < py + pad) { py = box.y - pad; touched = true; }
    else if (box.y + box.h > py + vh - pad) { py = box.y + box.h - vh + pad; touched = true; }
    if (!touched) return;
    state.spec.zoom = z;
    state.spec.panX = px;
    state.spec.panY = py;
  }

  /* When the current scene is a module scene, open a canvas and carry the
     scene over as real nodes instead of keeping it behind a block. */
  function ensureCanvasForBlock() {
    if (isCanvas()) return;
    var prev = state.spec;
    var grid = true;
    state.spec = presetFor('canvas');
    state.spec.grid = grid;
    mergeScene(prev);
  }

  /* Scene templates land in the current canvas as plain editable nodes. */
  function insertTemplateBlock(module, id) {
    /* Template chart tidak pernah membawa data: jenisnya dipakai, isinya
       tetap kosong dan membaca objek di kanvas. */
    if (module === 'chart') {
      var preset = presetById('chart', id);
      var type = (preset && preset.type) || 'bar';
      insertChartBlock(type);
      return;
    }
    var spec = presetById(module, id);
    if (!spec) return;
    pushHistory();
    ensureCanvasForBlock();
    mergeScene(spec);
    touchSpec();
    syncControls();
    render();
  }

  function insertModule(id) {
    /* Chart tidak lagi memakai preset data contoh: bloknya kosong dan
       membaca objek di kanvas. */
    if (id === 'chart') { insertChartBlock('bar'); return; }
    var spec = presetFor(id);
    if (!spec) return;
    pushHistory();
    ensureCanvasForBlock();
    mergeScene(spec);
    touchSpec();
    syncControls();
    render();
  }

  function addModuleBlock(id, spec) {
    var d = MODULE_DIMS[id] || [380, 240];
    var s = state.spec;
    var moduleCount = Object.keys(s.nodes || {}).filter(function (k) {
      return s.nodes[k] && s.nodes[k].shape === 'module';
    }).length;
    var sr = stage.getBoundingClientRect();
    var svg = stage.querySelector('svg');
    var scale = Math.min(1, Math.max(0.55, (sr.width - 48) / d[0]));
    var w = Math.round(d[0] * scale);
    var h = Math.round(d[1] * scale);
    var free = freeViewport();
    var screenX = free.left + (free.right - free.left) / 2 - w / 2 + (moduleCount % 3) * 28;
    var screenY = free.top + (free.bottom - free.top) / 2 - h / 2 + (moduleCount % 3) * 24;
    var c = svg ? svgPoint(svg, { clientX: screenX, clientY: screenY }) : viewportSceneCenter();
    s.nodes = s.nodes || {};
    var nid;
    do { nid = 'n' + (++nodeSeq); } while (s.nodes[nid]);
    s.nodes[nid] = {
      id: nid,
      x: Math.round(c.x),
      y: Math.round(c.y),
      w: w,
      h: h,
      shape: 'module',
      module: id,
      moduleSpec: spec,
      dataSource: id === 'chart' ? 'canvas' : undefined,
      groupBy: id === 'chart' ? 'sub' : undefined,
      agg: id === 'chart' ? 'count' : undefined,
      chartType: id === 'chart' ? 'bar' : undefined,
      label: '',
      color: COLOR_KEYS[Object.keys(s.nodes).length % COLOR_KEYS.length]
    };
    s.selected = nid;
    s.selectedEdge = null;
    s.selectedEdges = [];
    s.selectedDrawing = null;
    return nid;
  }

  function toggleModuleBlock(id) {
    var n = state.spec.nodes && state.spec.nodes[id];
    if (!n || n.shape !== 'module') return;
    pushHistory();
    if (!n._baseSize) {
      n._baseSize = {
        w: n.w || 420, h: n.h || 260,
        x: n.x || 0, y: n.y || 0
      };
    }
    if (n.expanded) {
      n.w = n._baseSize.w;
      n.h = n._baseSize.h;
      n.x = n._baseSize.x;
      n.y = n._baseSize.y;
      n.expanded = false;
    } else {
      n.w = Math.max(620, Math.round(n._baseSize.w * 1.55));
      n.h = Math.max(400, Math.round(n._baseSize.h * 1.55));
      n.x = Math.round(n._baseSize.x - (n.w - n._baseSize.w) / 2);
      n.y = Math.round(n._baseSize.y - (n.h - n._baseSize.h) / 2);
      n.expanded = true;
    }
    touchSpec();
    syncControls();
    render();
  }

  function applyLogo(id, additive) {
    /* A normal click always creates a clean logo object. Shift-click (or a
       drag onto a box) is the explicit way to use an existing box as the frame. */
    var cur = additive ? logoTarget() : null;
    if (!cur) {
      /* Assets work on an empty canvas too: pick a logo -> create a node in the
         center of the view, then attach the logo. */
      if (!isCanvas()) switchModule('canvas');
      var c = viewportSceneCenter();
      pushHistory();
      var nid = addNode('none', c.x - 48, c.y - 48, 96, 96);
      var s = state.spec;
      if (nid && s.nodes[nid]) {
        s.nodes[nid].logo = id;
        s.nodes[nid].logoSize = 64;
        delete s.nodes[nid].logos;
      }
      logoState.last = id;
      syncControls();
      syncLogoPanel();
      render();
      return;
    }
    pushHistory();
    var node = cur.node;
    logoState.last = id;
    if (additive) {
      node.logos = node.logos || [];
      if (node.logo) {
        node.logos.push(node.logo);
        delete node.logo;
      }
      var at = node.logos.indexOf(id);
      if (at >= 0) node.logos.splice(at, 1);
      else node.logos.push(id);
    } else if (node.logo === id && !node.logos) {
      delete node.logo;
    } else {
      node.logo = id;
      delete node.logos;
    }
    syncControls();
    render();
  }

  function syncLogoPanel() {
    var panel = document.getElementById('logoPanel');
    var assets = document.getElementById('panelAssets');
    var assetsOpen = !!(assets && assets.classList.contains('is-open'));
    var targets = logoTargets();
    panel.style.display = '';

    var sel = document.getElementById('logoNode');
    if (!targets.length) {
      logoState.target = null;
      sel.innerHTML = '<option value="">— add a node first —</option>';
      renderLogoPreview();
      if (assetsOpen) renderLogoGrid();
      document.getElementById('logoStatus').textContent = 'Add a node first';
      return;
    }
    var cur = logoTarget();
    logoState.target = cur ? cur.id : null;
    sel.innerHTML = '';
    targets.forEach(function (t) {
      var o = document.createElement('option');
      o.value = t.id;
      o.textContent = t.node.label || t.id;
      if (t.id === logoState.target) o.selected = true;
      sel.appendChild(o);
    });

    var node = cur && cur.node;
    renderLogoPreview();
    if (assetsOpen) renderLogoGrid();
  }

  /* Scene controls ------------------------------------------------------ */

  function sceneSlider(label, min, max, value, onChange) {
    var wrap = document.createElement('label');
    var head = document.createElement('span');
    head.className = 'scene-head';
    head.textContent = label + ' ';
    var val = document.createElement('b');
    val.textContent = value;
    head.appendChild(val);
    var input = document.createElement('input');
    input.type = 'range';
    input.min = min; input.max = max; input.step = 1; input.value = value;
    input.addEventListener('input', function () { val.textContent = input.value; });
    input.addEventListener('change', function () { onChange(parseInt(input.value, 10)); });
    wrap.appendChild(head);
    wrap.appendChild(input);
    return wrap;
  }

  function sceneSelect(label, options, value, onChange) {
    var wrap = document.createElement('label');
    wrap.textContent = label;
    var sel = document.createElement('select');
    options.forEach(function (o) {
      var opt = document.createElement('option');
      opt.value = o[0]; opt.textContent = o[1];
      if (o[0] === value) opt.selected = true;
      sel.appendChild(opt);
    });
    sel.addEventListener('change', function () { onChange(sel.value); });
    wrap.appendChild(sel);
    return wrap;
  }

  function sceneButton(label, onClick) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'ghost';
    b.textContent = label;
    b.addEventListener('click', onClick);
    return b;
  }

  function regenFlow(cols, per, pattern) {
    var base = makeFlow(cols, per, pattern);
    base.cable = state.spec.cable || 'solid';
    base.motion = state.spec.motion || 'flow';
    base.speed = state.spec.speed || 1;
    base.vertical = !!state.spec.vertical;
    base.grid = true;
    base._preset = 'custom';
    state.spec = base;
    syncScene();
    syncControls();
    render();
  }

  function regenPipeline(n) {
    var base = makePipeline(n);
    base.cable = state.spec.cable || 'solid';
    base.motion = state.spec.motion || 'packets';
    base.speed = state.spec.speed || 1;
    base.color = state.spec.color || 'cyan';
    base.grid = true;
    base._preset = 'custom';
    state.spec = base;
    syncScene();
    syncControls();
    render();
  }

  function regenGraph(n, pattern) {
    var base = makeGraph(n, pattern);
    base.grid = true;
    base._preset = 'custom';
    state.spec = base;
    syncScene();
    syncControls();
    render();
  }

  function regenProxy(n) {
    var base = makeProxy(n);
    base.grid = true;
    base._preset = 'custom';
    state.spec = base;
    syncScene();
    syncControls();
    render();
  }

  function regenChart(series, points) {
    var base = chartPreset(state.spec.type || 'bar', series, points);
    base.grid = true;
    base._preset = 'custom';
    state.spec = base;
    syncScene();
    syncControls();
    render();
  }

  var TEMPLATE_GROUPS = [
    ['canvas', 'Canvas'],
    ['flow', 'Flow'],
    ['reverse-proxy', 'Reverse proxy'],
    ['chart', 'Chart'],
    ['pipeline', 'Pipeline'],
    ['graph', 'Graph']
  ];

  /* One canvas, always: a template is added to the canvas you are on. The
     page never swaps scene, never re-renders a different module, and keeps the
     grid exactly as it was. */
  function loadPreset(module, id) {
    var def = (PRESETS[module] || []).filter(function (p) { return p[0] === id; })[0];
    if (!def) return;
    var s = state.spec;
    s._preset = def[0];
    /* Blank canvas empties the canvas you are on: same page, same grid, same
       view. Undo brings the scene back. */
    if (module === 'canvas' && id === 'blank') {
      pushHistory();
      s.nodes = {};
      s.edges = [];
      s.drawings = [];
      s.zoom = 1;
      s.panX = 0;
      s.panY = 0;
      s.selected = null;
      s.selectedEdge = null;
      s.selectedEdges = [];
      s.selectedDrawing = null;
      touchSpec();
      syncControls();
      render();
      return;
    }
    insertTemplateBlock(module, id);
  }

  function chartSourceNodes() {
    var nodes = state.spec.nodes || {};
    return Object.keys(nodes).map(function (id) { return nodes[id]; }).filter(function (n) {
      return n && n.shape !== 'module' && n.shape !== 'chart';
    });
  }

  function chartGroupValue(n, groupBy) {
    var raw = n[groupBy];
    if (raw == null || raw === '') raw = n.category;
    if (raw == null || raw === '') raw = n.label;
    if (raw == null || raw === '') raw = n.shape || 'node';
    return String(raw);
  }

  function buildChartSpecFromTable(n) {
    var table = state.spec.nodes && state.spec.nodes[n.sourceTable];
    if (!table || table.shape !== 'table') {
      return {
        module: 'chart', type: 'table', title: n.label || 'Table data',
        columns: ['Table', 'Status'], rows: [['No table selected', '']]
      };
    }
    var cols = table.columns || [];
    var rows = table.rows || [];
    if (!cols.length) cols = ['Column 1', 'Column 2', 'Column 3'];
    var agg = n.agg || 'count';
    var kind = n.chartType || 'bar';
    var labels = [];
    var counts = {};
    var values = [];
    rows.forEach(function (row) {
      var label = row[0];
      if (label == null || label === '') return;
      label = String(label);
      labels.push(label);
      counts[label] = (counts[label] || 0) + 1;
      var v = Number(row[1]);
      values.push(isFinite(v) ? v : 0);
    });
    var data;
    if (agg === 'count') {
      labels = Object.keys(counts).sort();
      data = labels.map(function (k) { return counts[k]; });
    } else {
      data = values.slice();
    }
    var spec = {
      module: 'chart', type: kind, title: n.label || 'Table data',
      labels: labels, data: data, color: n.color || 'blue'
    };
    if (kind === 'donut') {
      spec.colors = labels.map(function (_, i) { return COLOR_KEYS[i % COLOR_KEYS.length]; });
      spec.centerLabel = agg === 'count' ? 'rows' : agg;
    } else if (kind === 'table') {
      spec.columns = ['Group', agg === 'count' ? 'Count' : agg];
      spec.rows = labels.map(function (k, i) { return [k, String(data[i])]; });
      delete spec.labels;
      delete spec.data;
    } else if (kind === 'hbar') {
      spec.xLabel = agg === 'count' ? 'Rows' : agg;
    } else if (kind === 'line' || kind === 'area') {
      spec.series = [{ name: agg, data: data }];
    }
    return spec;
  }

  function parseChartData(text) {
    return String(text || '').split('\n').map(function (line) {
      var raw = line.trim();
      if (!raw) return null;
      var m = /^(.+?)\s*[:=]\s*(-?[\d.,]+)\s*$/.exec(raw);
      if (!m) return null;
      var value = Number(String(m[2]).replace(/,/g, ''));
      if (!isFinite(value)) return null;
      return { label: m[1].trim(), value: value };
    }).filter(Boolean);
  }

  function buildChartSpecFromCanvas(n) {
    if (n.dataSource === 'table') return buildChartSpecFromTable(n);
    if (n.dataSource === 'manual') {
      var rows = parseChartData(n.chartData);
      var kindM = n.chartType || 'bar';
      var specM = {
        module: 'chart', type: kindM, title: n.label || 'Chart data',
        labels: rows.map(function (r) { return r.label; }),
        data: rows.map(function (r) { return r.value; }),
        color: n.color || 'blue'
      };
      if (!rows.length) {
        specM.type = 'table';
        specM.columns = ['Label', 'Value'];
        specM.rows = [['No data yet', '']];
        delete specM.labels;
        delete specM.data;
        return specM;
      }
      if (kindM === 'kpi') {
        var sum = rows.reduce(function (a, r) { return a + r.value; }, 0);
        specM.labels = ['total'];
        specM.data = [sum];
        specM.label = 'total';
      } else if (kindM === 'gauge') {
        var sumG = rows.reduce(function (a, r) { return a + r.value; }, 0);
        specM.labels = ['total'];
        specM.data = [sumG];
        specM.max = Math.max(1, sumG);
        specM.label = 'total';
      } else if (kindM === 'scatter') {
        specM.data = rows.map(function (r, i) { return [i, r.value]; });
      } else if (kindM === 'donut') {
        specM.colors = rows.map(function (_, i) { return COLOR_KEYS[i % COLOR_KEYS.length]; });
        specM.centerLabel = 'total';
      } else if (kindM === 'table') {
        specM.columns = ['Label', 'Value'];
        specM.rows = rows.map(function (r) { return [r.label, String(r.value)]; });
        delete specM.labels;
        delete specM.data;
      }
      return specM;
    }
    var groupBy = n.groupBy || 'sub';
    var agg = n.agg || 'count';
    var kind = n.chartType || 'bar';
    var nodes = chartSourceNodes();
    var counts = {};
    var totals = {};
    var numeric = 0;
    nodes.forEach(function (node) {
      var key = chartGroupValue(node, groupBy);
      counts[key] = (counts[key] || 0) + 1;
      var v = Number(node.value);
      if (isFinite(v)) {
        totals[key] = (totals[key] || 0) + v;
        numeric++;
      }
    });
    var labels = Object.keys(counts).sort();
    if (agg !== 'count' && !numeric) {
      return {
        module: 'chart', type: 'table', title: n.label || 'Canvas data',
        columns: ['Group', 'Numeric value'],
        rows: labels.length ? labels.map(function (k) { return [k, 'no numeric value']; }) : [['No canvas objects', '']]
      };
    }
    var data = labels.map(function (k) {
      if (agg === 'sum') return totals[k] || 0;
      if (agg === 'avg') return counts[k] ? (totals[k] || 0) / counts[k] : 0;
      return counts[k];
    });
    var spec = {
      module: 'chart', type: kind, title: n.label || 'Canvas data',
      labels: labels, data: data, color: n.color || 'blue'
    };
    if (kind === 'kpi' || kind === 'gauge') {
      /* These two show one number, not a series: collapse the groups into a
         single total so the value is the aggregate of the canvas. */
      var total = data.reduce(function (a, b) { return a + (isFinite(b) ? b : 0); }, 0);
      spec.labels = [agg === 'count' ? 'objects' : agg];
      spec.data = [total];
      if (kind === 'gauge') spec.max = Math.max(1, total);
      spec.label = agg === 'count' ? 'objects' : agg;
    } else if (kind === 'scatter') {
      /* Scatter wants [x, y] pairs. Flat counts become (index, value). */
      spec.data = data.map(function (v, i) { return [i, v]; });
      spec.xLabel = 'index';
      spec.yLabel = agg === 'count' ? 'count' : agg;
    } else if (kind === 'donut') {
      spec.colors = labels.map(function (_, i) { return COLOR_KEYS[i % COLOR_KEYS.length]; });
      spec.centerLabel = agg === 'count' ? 'objects' : agg;
    } else if (kind === 'table') {
      spec.columns = ['Group', agg === 'count' ? 'Count' : agg];
      spec.rows = labels.map(function (k, i) { return [k, String(data[i])]; });
      delete spec.labels;
      delete spec.data;
    } else if (kind === 'hbar') {
      spec.xLabel = agg === 'count' ? 'Count' : agg;
    } else if (kind === 'line' || kind === 'area') {
      spec.series = [{ name: agg, data: data }];
    }
    return spec;
  }

  function refreshCanvasChartSpecs() {
    var nodes = state.spec.nodes || {};
    Object.keys(nodes).forEach(function (id) {
      var n = nodes[id];
      if (!n) return;
      var derived = n.dataSource === 'canvas' || n.dataSource === 'table' ||
        n.dataSource === 'manual';
      if (n.shape === 'chart' && derived) {
        n.staticSpec = buildChartSpecFromCanvas(n);
      } else if (n.shape === 'module' && n.module === 'chart' && derived) {
        n.moduleSpec = buildChartSpecFromCanvas(n);
      }
    });
  }

  /* Panel 3 mengikuti blok chart yang dipilih. Tidak ada data contoh:
     sumbernya objek canvas, dan kalau kosong ya kosong. */
  function syncChartDataPanel(keepSource) {
    var fm = focusedBlock();
    var n = fm.node;
    var section = document.getElementById('chartSection');
    if (!section) return;
    var hint = document.getElementById('chartHint');
    var quick = document.getElementById('chartQuickAdd');
    /* Panel 4 hanya soal blok chart. Kalau tidak ada blok chart terpilih,
       isinya cuma daftar "tambah chart" — tidak ada kontrol scene yang
       membingungkan. */
    section.hidden = false;
    if (!section.open && n) section.open = true;
    var controls = document.getElementById('chartBlockControls');
    var headSpan = section.querySelector('.scene-step-head span');

    if (n) {
      if (quick) quick.hidden = true;
      if (controls) controls.hidden = false;
      if (headSpan) headSpan.textContent = 'selected block';
      if (hint) hint.textContent = 'Selected chart block. Changing the type redraws that block only.';
      var source = keepSource
        ? (document.getElementById('chartSource').value || n.dataSource || 'canvas')
        : (n.dataSource || 'canvas');
      document.getElementById('chartSource').value = source;
      document.getElementById('chartGroupBy').value = n.groupBy || 'sub';
      document.getElementById('chartAgg').value = n.agg || 'count';
      var tableRow = document.getElementById('chartTableRow');
      var tableSel = document.getElementById('chartTable');
      tableRow.hidden = source !== 'table';
      var dataRow = document.getElementById('chartDataRow');
      var dataBox = document.getElementById('chartData');
      if (dataRow) dataRow.hidden = source !== 'manual';
      if (dataBox && source === 'manual' && document.activeElement !== dataBox) {
        dataBox.value = n.chartData || '';
      }
      tableSel.innerHTML = '';
      Object.keys(state.spec.nodes || {}).forEach(function (id) {
        var tn = state.spec.nodes[id];
        if (!tn || tn.shape !== 'table') return;
        var o = document.createElement('option');
        o.value = id;
        o.textContent = tn.label || id;
        if (n.sourceTable === id) o.selected = true;
        tableSel.appendChild(o);
      });
      if (!tableSel.options.length) {
        var o = document.createElement('option');
        o.value = '';
        o.textContent = '— add a table block first —';
        tableSel.appendChild(o);
      }
      var count = source === 'table' ? 0 : chartSourceNodes().length;
      var status = document.getElementById('chartDataStatus');
      if (status) {
        status.textContent = source === 'table'
          ? 'Reads one table block. Empty table = empty chart.'
          : (count + (count === 1 ? ' object on this canvas.' : ' objects on this canvas.') +
             (count ? '' : ' Add objects, or pick a Table block as the source.'));
      }
      return;
    }

    /* Belum ada blok chart dipilih: tawarkan tambah, jangan paksa apa pun. */
    if (quick) quick.hidden = false;
    if (controls) controls.hidden = true;
    if (headSpan) headSpan.textContent = 'add a chart';
    if (hint) hint.textContent = 'No chart block selected. Pick a type to add one.';
    renderChartQuickList();
  }

  function syncScene() {
    var body = document.querySelector('#panelAssets .dock-body');
    var keep = body ? body.scrollTop : 0;
    requestAnimationFrame(function () { if (body) body.scrollTop = keep; });
    var s = state.spec;
    var m = s.module || 'flow';
    renderTemplateList();

    var host = document.getElementById('sceneControls');
    host.innerHTML = '';

    if (m === 'flow') {
      var cols = (s.columns && s.columns.length) || 4;
      var per = 1;
      (s.columns || []).forEach(function (c) { if (c.length > per) per = c.length; });
      host.appendChild(sceneSlider('Columns', 1, 5, cols, function (v) { regenFlow(v, per, s.pattern || 'bipartite'); }));
      host.appendChild(sceneSlider('Nodes / column', 1, 4, per, function (v) { regenFlow(cols, v, s.pattern || 'bipartite'); }));
      host.appendChild(sceneSelect('Edges', [['bipartite', 'Full'], ['fan', 'Fan'], ['chain', 'Chain']], s.pattern || 'bipartite', function (v) { regenFlow(cols, per, v); }));
    } else if (m === 'reverse-proxy') {
      host.appendChild(sceneSlider('Backends', 1, 8, s.backends || 3, function (v) { regenProxy(v); }));
    } else if (m === 'chart') {
      /* Tidak ada slider Points dan tidak ada Randomize: chart tidak pernah
         mengarang data. Semua diatur di panel 3. */
    } else if (m === 'pipeline') {
      host.appendChild(sceneSlider('Stages', 2, 8, (s.stages || []).length || 4, function (v) { regenPipeline(v); }));
      host.appendChild(sceneSlider('Items', 2, 8, s.items || 4, function (v) {
        state.spec.items = v;
        specBox.value = JSON.stringify(state.spec, null, 2);
        render();
      }));
    } else if (m === 'graph') {
      host.appendChild(sceneSlider('Nodes', 3, 12, (s.nodes || []).length || 8, function (v) { regenGraph(v, s.pattern || 'tree'); }));
      host.appendChild(sceneSelect('Edges', [['tree', 'Tree'], ['line', 'Line'], ['random', 'Random']], s.pattern || 'tree', function (v) { regenGraph((s.nodes || []).length || 8, v); }));
    }
  }

  /* Canvas editor ------------------------------------------------------- */

  var editor = {
    tool: 'select',
    keepTool: false,
    snap: true,
    from: null,
    drag: null,
    history: [],
    future: [],
    clipboard: null,
    panelPos: {},
    panelSize: {},
    textStyle: {
      fontFamily: 'Excalifont',
      fontSize: 16,
      color: '#e6edf3',
      bold: false,
      italic: false,
      align: 'left',
      lineHeight: 1.35,
      opacity: 1
    },
    penStyle: {
      color: '#e6edf3',
      width: 2,
      strokeStyle: 'solid',
      opacity: 1
    }
  };

  try {
    var savedPanels = JSON.parse(localStorage.getItem('ruang.panels.v1') || '{}');
    if (savedPanels && typeof savedPanels === 'object') editor.panelPos = savedPanels;
    var savedSizes = JSON.parse(localStorage.getItem('ruang.panelSize.v1') || '{}');
    if (savedSizes && typeof savedSizes === 'object') editor.panelSize = savedSizes;
    var savedTextStyle = JSON.parse(localStorage.getItem('ruang.textStyle.v1') || 'null');
    if (savedTextStyle && typeof savedTextStyle === 'object') {
      Object.keys(editor.textStyle).forEach(function (k) {
        if (savedTextStyle[k] !== undefined) editor.textStyle[k] = savedTextStyle[k];
      });
    }
    var savedPenStyle = JSON.parse(localStorage.getItem('ruang.penStyle.v1') || 'null');
    if (savedPenStyle && typeof savedPenStyle === 'object') {
      Object.keys(editor.penStyle).forEach(function (k) {
        if (savedPenStyle[k] !== undefined) editor.penStyle[k] = savedPenStyle[k];
      });
    }
  } catch (err) {}
  var nodeSeq = 0;
  var drawSeq = 0;
  var spaceDown = false;
  var saveTimer = null;

  function isCanvas() { return (state.spec.module || 'flow') === 'canvas'; }

  function closestNode(el) {
    while (el && el !== stage) {
      if (el.classList && el.classList.contains('alur-canvas-node')) return el;
      el = el.parentNode;
    }
    return null;
  }

  function closestModuleDelete(el) {
    while (el && el !== stage) {
      if (el.getAttribute && el.getAttribute('data-module-delete') != null) return el;
      el = el.parentNode;
    }
    return null;
  }

  function closestHandle(el) {
    while (el && el !== stage) {
      if (el.getAttribute && el.getAttribute('data-handle')) return el;
      el = el.parentNode;
    }
    return null;
  }

  function closestEdge(el) {
    while (el && el !== stage) {
      if (el.getAttribute && el.getAttribute('data-edge') != null) return el;
      el = el.parentNode;
    }
    return null;
  }

  function closestDrawing(el) {
    while (el && el !== stage) {
      if (el.getAttribute && el.getAttribute('data-drawing')) return el;
      el = el.parentNode;
    }
    return null;
  }

  function svgPoint(svg, ev) {
    var pt = svg.createSVGPoint();
    pt.x = ev.clientX;
    pt.y = ev.clientY;
    var ctm = svg.getScreenCTM();
    if (!ctm) return { x: 0, y: 0 };
    return pt.matrixTransform(ctm.inverse());
  }

  /* Infinite canvas model: panX/panY is the world point under the viewport's
     top-left corner, zoom is screen pixels per world unit. The view is a free
     window into the plane, so pan and zoom never depend on each other and no
     artboard edge is ever re-centered by a zoom change. */
  /* Aturan zoom: 10% sampai 100%, tidak lebih. Kanvas digeser, bukan
     diperbesar tanpa batas. Zoom is clamped to 10%–100%: pan, don't magnify. */
  var MIN_ZOOM = 0.1;
  var MAX_ZOOM = 30;

  function clampZoom(z) {
    var v = typeof z === 'number' ? z : parseFloat(z);
    if (!isFinite(v) || v <= 0) v = 1;
    return Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, v));
  }

  function viewMetrics() {
    var svg = stage.querySelector('svg');
    var rect = svg && svg.getBoundingClientRect ? svg.getBoundingClientRect() :
      { left: 0, top: 0, width: 900, height: 520 };
    var w = rect.width || 900;
    var h = rect.height || 520;
    var z = clampZoom(state.spec.zoom);
    return { left: rect.left || 0, top: rect.top || 0, w: w, h: h, z: z, vw: w / z, vh: h / z };
  }

  /* Keep a world box centred without touching the zoom level. */
  function centerBox(b, z) {
    var m = viewMetrics();
    var scale = z || m.z;
    state.spec.panX = (b.x + b.w / 2) - (m.w / scale) / 2;
    state.spec.panY = (b.y + b.h / 2) - (m.h / scale) / 2;
  }

  /* Fit a world box: the largest zoom that still shows it whole. */
  function fitBox(b, maxZoom) {
    var m = viewMetrics();
    if (!b || !b.w || !b.h) return null;
    var pad = 80;
    var z = Math.min((m.w - pad) / b.w, (m.h - pad) / b.h);
    z = clampZoom(Math.min(z, maxZoom || 1));
    state.spec.zoom = z;
    centerBox(b, z);
    return z;
  }

  function viewportSceneCenter() {
    var svg = stage.querySelector('svg');
    if (!svg) return { x: 370, y: 200 };
    var r = svg.getBoundingClientRect();
    if (!r.width || !r.height) return { x: 370, y: 200 };
    var free = freeViewport();
    var cx = (free.left + free.right) / 2;
    var cy = (free.top + free.bottom) / 2;
    if (!cx || !cy) { cx = r.left + r.width / 2; cy = r.top + r.height / 2; }
    return svgPoint(svg, { clientX: cx, clientY: cy });
  }

  /* The part of the stage a panel is not sitting on. New blocks are dropped
     in the middle of this area, like Excalidraw drops them in the middle of
     the visible canvas, so they are never born underneath the inspector. */
  function freeViewport() {
    var svg = stage.querySelector('svg');
    var r = svg ? svg.getBoundingClientRect() : { left: 0, top: 0, width: 0, height: 0 };
    var left = r.left || 0;
    var top = r.top || 0;
    var right = left + (r.width || window.innerWidth);
    var bottom = top + (r.height || window.innerHeight);
    var panels = [document.getElementById('shapePanel')];
    Object.keys(PANELS).forEach(function (n) {
      var el = panelEl(n);
      if (el && el.classList.contains('is-open')) panels.push(el);
    });
    panels.forEach(function (el) {
      if (!el || el.hidden) return;
      var b = el.getBoundingClientRect();
      if (!b.width || !b.height) return;
      var overLeft = b.left - left < right - b.right;
      if (overLeft) left = Math.max(left, b.right + 8);
      else right = Math.min(right, b.left - 8);
    });
    if (right - left < 260 || bottom - top < 200) {
      left = r.left || 0;
      right = left + (r.width || window.innerWidth);
      top = r.top || 0;
      bottom = top + (r.height || window.innerHeight);
    }
    return { left: left, top: top, right: right, bottom: bottom };
  }

  function saveScene() {
    /* Simpan zoom dalam rentang sah supaya sesi berikutnya tidak pernah
       memuat 257% atau angka liar lain dari spec lama. */
    state.spec.zoom = clampZoom(state.spec.zoom);
    try { localStorage.setItem(SAVE_KEY, JSON.stringify(state.spec)); } catch (err) {}
  }

  function queueSave() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(saveScene, 250);
  }

  var specTextTimer = null;

  function touchSpec() {
    queueSave();
    if (editor.drag) return;
    if (specTextTimer) return;
    specTextTimer = setTimeout(function () {
      specTextTimer = null;
      specBox.value = JSON.stringify(state.spec, null, 2);
    }, 120);
  }

  function overlayLayer() {
    var svg = stage.querySelector('svg');
    if (!svg) return null;
    var g = svg.querySelector('.alur-layer-overlay');
    if (!g) g = AlurKit.g(svg, 'alur-layer-overlay');
    return g;
  }

  function pointsToPath(points) {
    return points.map(function (p, i) {
      return (i ? 'L ' : 'M ') + p[0].toFixed(1) + ' ' + p[1].toFixed(1);
    }).join(' ');
  }

  var viewRaf = 0;

  function applyView(skipMinimap) {
    if (viewRaf) return;
    viewRaf = requestAnimationFrame(function () {
      viewRaf = 0;
      applyViewNow(skipMinimap);
    });
  }

  function applyViewNow(skipMinimap) {
    if (!isCanvas()) {
      var mmOff = document.getElementById('minimap');
      if (mmOff) mmOff.hidden = true;
      return;
    }
    var svg = stage.querySelector('svg');
    if (!svg) return;
    var rect = svg.getBoundingClientRect();
    /* The stage already starts below the floating topbar, so the whole stage is
       usable canvas. No hidden band, no reserved strip. */
    var availableH = Math.max(120, rect.height);
    /* Kanvas tanpa batas: halaman hanya penanda, bukan pagar. Ukurannya tetap
       (dipakai bingkai + ekspor) tapi isi di luarnya tetap bisa disentuh.
       The page is a marker, not a fence: its size is kept for the frame and
       for export, but nothing outside it is clipped or blocked. */
    if (!state.spec.width) { state.spec.width = 1600; queueSave(); }
    if (!state.spec.height) { state.spec.height = 900; queueSave(); }
    var z = clampZoom(state.spec.zoom);
    state.spec.zoom = z;
    var vw = rect.width / z;
    var vh = rect.height / z;
    var vx = state.spec.panX || 0;
    var vy = state.spec.panY || 0;
    svg.setAttribute('viewBox', vx + ' ' + vy + ' ' + vw + ' ' + vh);
    var gridRect = svg.querySelector('.alur-canvas-grid');
    if (gridRect) {
      gridRect.setAttribute('x', vx);
      gridRect.setAttribute('y', vy);
      gridRect.setAttribute('width', vw);
      gridRect.setAttribute('height', vh);
    }
    /* Keep the mounted spec in step with the view so a re-mount (or any
       external reader) never sees the pre-pan zoom. */
    if (!editor.drag) stage.setAttribute('data-spec', JSON.stringify(state.spec));
    var pct = Math.round(z * 100) + '%';
    var zv = document.getElementById('zoomVal');
    if (zv) zv.textContent = pct;
    var top = document.getElementById('topStatus');
    if (top && /\d+%$/.test(top.textContent)) top.textContent = top.textContent.replace(/\d+%$/, pct);
    if (editor && editor.textEdit) positionInlineText();
    if (!skipMinimap) renderMinimap();
  }

  function setZoom(z) {
    var m = viewMetrics();
    var target = clampZoom(z);
    var ax = m.left + m.w / 2;
    var ay = m.top + m.h / 2;
    var sx = (state.spec.panX || 0) + (ax - m.left) / m.z;
    var sy = (state.spec.panY || 0) + (ay - m.top) / m.z;
    state.spec.zoom = target;
    state.spec.panX = sx - (ax - m.left) / target;
    state.spec.panY = sy - (ay - m.top) / target;
    applyView();
    touchSpec();
  }

  function updateStatus() {
    var counts = document.getElementById('statusCounts');
    var tool = document.getElementById('statusTool');
    var zv = document.getElementById('zoomVal');
    var top = document.getElementById('topStatus');
    var summary = '';
    if (counts) {
      var n = Object.keys(state.spec.nodes || {}).length;
      var e = (state.spec.edges || []).length;
      var d = (state.spec.drawings || []).length;
      summary = n + ' nodes · ' + e + ' edges' + (d ? ' · ' + d + ' drawings' : '');
      counts.textContent = summary;
    }
    /* Label selalu dari nilai yang sudah dijepit: spec lama bisa menyimpan
       zoom liar, dan itu tidak boleh tampil di layar. Sekalian menormalkan
       state supaya ekspor dan simpan ikut nilai yang sah. */
    var zc = clampZoom(state.spec.zoom || 1);
    if (zc !== state.spec.zoom) { state.spec.zoom = zc; queueSave(); }
    if (top) top.textContent = summary + ' · ' + Math.round(state.spec.zoom * 100) + '%';
    if (tool) tool.textContent = 'tool: ' + editor.tool;
    var ss = document.getElementById('statusSelection');
    if (ss) {
      var sel = selectionIds();
      ss.textContent = sel.length > 1 ? sel.length + ' selected' : '';
    }
    var eh = document.getElementById('emptyHint');
    if (eh) {
      var blank = isCanvas() && !Object.keys(state.spec.nodes || {}).length &&
        !(state.spec.drawings || []).length;
      eh.hidden = !blank;
    }
    if (zv) zv.textContent = Math.round(state.spec.zoom * 100) + '%';
    renderLayers();
  }

  function updateHistoryButtons() {
    var u = document.getElementById('undoBtn');
    var r = document.getElementById('redoBtn');
    if (u) u.disabled = !editor.history.length;
    if (r) r.disabled = !editor.future.length;
    var has = selectionIds().length > 0;
    var d = document.getElementById('dupBtn');
    var c = document.getElementById('copyBtn');
    var p = document.getElementById('pasteBtn');
    if (d) d.disabled = !has;
    if (c) c.disabled = !has;
    if (p) p.disabled = !(editor.clipboard && editor.clipboard.nodes.length);
  }

  function pushHistory() {
    editor.history.push(JSON.stringify(state.spec));
    if (editor.history.length > 80) editor.history.shift();
    editor.future.length = 0;
    updateHistoryButtons();
  }

  function undo() {
    if (!editor.history.length) return;
    editor.future.push(JSON.stringify(state.spec));
    state.spec = JSON.parse(editor.history.pop());
    syncControls();
    syncEditor();
    render();
    updateHistoryButtons();
  }

  function redo() {
    if (!editor.future.length) return;
    editor.history.push(JSON.stringify(state.spec));
    state.spec = JSON.parse(editor.future.pop());
    syncControls();
    syncEditor();
    render();
    updateHistoryButtons();
  }

  /* Workspace UI ------------------------------------------------------- */

  var PANELS = {
    tools: 'panelTools',
    scene: 'panelScene',
    properties: 'panelProperties',
    assets: 'panelAssets',
    layers: 'panelLayers'
  };
  var PANEL_SIDE = { tools: 'left', scene: 'left', properties: 'right', assets: 'right', layers: 'right' };
  var PANEL_LOCKED = {};
  var PANEL_RESIZABLE = { scene: true, assets: true, layers: true, tools: true };
  var SVG_NS = 'http://www.w3.org/2000/svg';

  function panelEl(name) { return document.getElementById(PANELS[name]); }

  function savePanels() {
    try { localStorage.setItem('ruang.panels.v1', JSON.stringify(editor.panelPos || {})); } catch (err) {}
  }

  function savePanelSize() {
    try { localStorage.setItem('ruang.panelSize.v1', JSON.stringify(editor.panelSize || {})); } catch (err) {}
  }

  function applyPanelSize(name) {
    var el = panelEl(name);
    if (!el || PANEL_LOCKED[name]) return;
    var size = editor.panelSize && editor.panelSize[name];
    if (!size) return;
    var gutter = window.innerWidth <= 760 ? 16 : 24;
    var maxW = Math.min(620, window.innerWidth - gutter);
    var w = Math.max(280, Math.min(maxW, size.w || 360));
    var h = Math.max(200, Math.min(window.innerHeight - 150, size.h || 360));
    el.style.width = w + 'px';
    el.style.height = h + 'px';
    el.style.maxHeight = 'none';
  }

  function applyPanelPos(name) {
    var el = panelEl(name);
    if (!el || PANEL_LOCKED[name]) return;
    var pos = editor.panelPos && editor.panelPos[name];
    if (pos && window.innerWidth > 760) {
      var w = el.offsetWidth || 330;
      var h = el.offsetHeight || 200;
      var x = Math.max(8, Math.min(window.innerWidth - w - 8, pos.left));
      var y = Math.max(8, Math.min(window.innerHeight - h - 8, pos.top));
      el.style.left = x + 'px';
      el.style.top = y + 'px';
      el.style.right = 'auto';
      el.style.bottom = 'auto';
      el.style.transform = 'none';
    } else {
      el.style.left = '';
      el.style.top = '';
      el.style.right = '';
      el.style.bottom = '';
      el.style.transform = '';
    }
  }

  function initDockDrag(name) {
    var el = panelEl(name);
    if (!el || PANEL_LOCKED[name]) return;
    var head = el.querySelector('.dock-head');
    if (!head) return;
    head.addEventListener('pointerdown', function (ev) {
      if (ev.target.closest && ev.target.closest('[data-close]')) return;
      if (ev.button !== 0 || window.innerWidth <= 760) return;
      var r = el.getBoundingClientRect();
      var offX = ev.clientX - r.left;
      var offY = ev.clientY - r.top;
      var dragging = true;
      el.classList.add('is-dragging');
      document.body.classList.add('is-panel-dragging');
      el.style.right = 'auto';
      el.style.bottom = 'auto';
      el.style.left = r.left + 'px';
      el.style.top = r.top + 'px';
      el.style.transform = 'none';
      el.style.willChange = 'left, top';
      try { head.setPointerCapture(ev.pointerId); } catch (err) {}

      function move(e) {
        if (!dragging) return;
        var w = el.offsetWidth;
        var h = el.offsetHeight;
        var x = Math.max(8, Math.min(window.innerWidth - w - 8, e.clientX - offX));
        var y = Math.max(8, Math.min(window.innerHeight - h - 8, e.clientY - offY));
        el.style.left = x + 'px';
        el.style.top = y + 'px';
      }

      function up() {
        if (!dragging) return;
        dragging = false;
        document.removeEventListener('pointermove', move);
        document.removeEventListener('pointerup', up);
        document.removeEventListener('pointercancel', up);
        el.classList.remove('is-dragging');
        document.body.classList.remove('is-panel-dragging');
        el.style.willChange = '';
        var r2 = el.getBoundingClientRect();
        editor.panelPos[name] = { left: Math.round(r2.left), top: Math.round(r2.top) };
        savePanels();
      }

      document.addEventListener('pointermove', move, { passive: false });
      document.addEventListener('pointerup', up, { once: true });
      document.addEventListener('pointercancel', up, { once: true });
      ev.preventDefault();
    });
  }

  function initDockResize(name) {
    var el = panelEl(name);
    if (!el || !PANEL_RESIZABLE[name]) return;
    var handle = el.querySelector('[data-resize="' + name + '"]');
    if (!handle) return;
    handle.addEventListener('pointerdown', function (ev) {
      if (ev.button !== 0) return;
      var r = el.getBoundingClientRect();
      var startW = r.width;
      var startH = r.height;
      var startX = ev.clientX;
      var startY = ev.clientY;
      el.classList.add('is-resizing');
      try { handle.setPointerCapture(ev.pointerId); } catch (err) {}

      function move(e) {
        var w = Math.max(420, Math.min(window.innerWidth - 24, startW + e.clientX - startX));
        var h = Math.max(220, Math.min(window.innerHeight - 150, startH + e.clientY - startY));
        el.style.width = w + 'px';
        el.style.height = h + 'px';
        el.style.maxHeight = 'none';
      }

      function up() {
        handle.removeEventListener('pointermove', move);
        handle.removeEventListener('pointerup', up);
        handle.removeEventListener('pointercancel', up);
        el.classList.remove('is-resizing');
        var r2 = el.getBoundingClientRect();
        editor.panelSize[name] = { w: Math.round(r2.width), h: Math.round(r2.height) };
        savePanelSize();
      }

      handle.addEventListener('pointermove', move);
      handle.addEventListener('pointerup', up);
      handle.addEventListener('pointercancel', up);
      ev.preventDefault();
      ev.stopPropagation();
    });
  }

  /* The canvas is the free area. A floating panel must never sit on top of a
     region where the drawing tools would otherwise work, so the stage is inset
     by whatever chrome is actually open. */
  var stageRO = ('ResizeObserver' in window) ? new ResizeObserver(function () {
    var r = stage.getBoundingClientRect();
    if (!r.width || !r.height) return;
    var prev = stageRO.last;
    stageRO.last = { w: r.width, h: r.height };
    if (!prev || !prev.w || !prev.h) { applyViewNow(true); return; }
    /* Keep the same world point in the middle of the view when the canvas is
       resized, so insetting never looks like the view jumped. */
    var z = clampZoom(state.spec.zoom);
    var cx = (state.spec.panX || 0) + prev.w / (2 * z);
    var cy = (state.spec.panY || 0) + prev.h / (2 * z);
    state.spec.panX = cx - r.width / (2 * z);
    state.spec.panY = cy - r.height / (2 * z);
    applyViewNow(true);
  }) : null;
  /* Tanpa observe(), callback di atas tidak pernah jalan: ukuran stage
     berubah (mis. bilah alamat mobile) tapi viewBox tetap yang lama. */
  if (stageRO && stage) stageRO.observe(stage);

  function syncStageInsets() {
    if (!stage) return;
    stage.style.left = '';
    stage.style.right = '';
    stage.style.bottom = '';
  }

  function setPanel(name, open) {
    var el = panelEl(name);
    if (!el) return;
    var isOpen = !!open && !el.classList.contains('is-open');
    if (isOpen) {
      var side = PANEL_SIDE[name];
      Object.keys(PANELS).forEach(function (n) {
        if (n !== name && PANEL_SIDE[n] === side) setPanel(n, false);
      });
    }
    el.classList.toggle('is-open', !!open);
    el.setAttribute('aria-hidden', open ? 'false' : 'true');
    syncStageInsets();
    Array.prototype.forEach.call(document.querySelectorAll('[data-panel="' + name + '"]'), function (btn) {
      btn.classList.toggle('is-on', !!open);
    });
    if (open) {
      applyPanelPos(name);
      applyPanelSize(name);
      if (name === 'assets') { syncLogoPanel(); renderLogoGrid(); syncScene(); }
      if (name === 'layers') renderLayers();
      if (name === 'properties') { renderNodeInspector(); renderEdgeInspector(); }
    }
    editor.panels = editor.panels || {};
    editor.panels[name] = !!open;
  }

  function togglePanel(name) {
    var el = panelEl(name);
    setPanel(name, !(el && el.classList.contains('is-open')));
  }

  function closePanels() {
    Object.keys(PANELS).forEach(function (n) { setPanel(n, false); });
    var sp = document.getElementById('shapePanel');
    if (sp) sp.hidden = true;
    syncStageInsets();
  }

  function syncTitle() {
    var input = document.getElementById('docTitle');
    if (!input) return;
    if (document.activeElement !== input) input.value = state.spec.title || 'Untitled diagram';
  }

  function renderLayers() {
    var host = document.getElementById('layerList');
    if (!host) return;
    var body = document.querySelector('#panelLayers .dock-body');
    var keep = body ? body.scrollTop : 0;
    requestAnimationFrame(function () { if (body) body.scrollTop = keep; });
    host.innerHTML = '';
    if (!isCanvas()) {
      var note = document.createElement('p');
      note.className = 'layer-empty';
      note.textContent = 'Switch to canvas to edit layers.';
      host.appendChild(note);
      return;
    }
    var s = state.spec;
    var nodes = s.nodes || {};
    var ids = Object.keys(nodes);
    var edges = s.edges || [];
    var drawings = s.drawings || [];
    if (!ids.length && !edges.length && !drawings.length) {
      var empty = document.createElement('p');
      empty.className = 'layer-empty';
      empty.textContent = 'Nothing on the canvas yet.';
      host.appendChild(empty);
      return;
    }

    function addRow(label, sub, active, onClick, kind, id) {
      var b = document.createElement('button');
      b.type = 'button';
      b.draggable = true;
      b.className = 'layer-row' + (active ? ' is-on' : '');
      b.dataset.kind = kind;
      b.dataset.id = id;
      b.title = 'Drag to reorder layer';
      b.textContent = label;
      if (sub) {
        var span = document.createElement('span');
        span.textContent = sub;
        b.appendChild(span);
      }
      b.addEventListener('click', onClick);
      b.addEventListener('dragstart', function (ev) {
        editor.layerDrag = { kind: kind, id: id };
        b.classList.add('is-dragging');
        try {
          ev.dataTransfer.effectAllowed = 'move';
          ev.dataTransfer.setData('text/plain', kind + ':' + id);
        } catch (err) {}
      });
      b.addEventListener('dragend', function () {
        editor.layerDrag = null;
        b.classList.remove('is-dragging');
        Array.prototype.forEach.call(host.querySelectorAll('.layer-row.is-drop'), function (x) {
          x.classList.remove('is-drop');
        });
      });
      b.addEventListener('dragover', function (ev) {
        if (!editor.layerDrag || editor.layerDrag.kind !== kind) return;
        ev.preventDefault();
        ev.dataTransfer.dropEffect = 'move';
        b.classList.add('is-drop');
      });
      b.addEventListener('dragleave', function () { b.classList.remove('is-drop'); });
      b.addEventListener('drop', function (ev) {
        if (!editor.layerDrag || editor.layerDrag.kind !== kind) return;
        ev.preventDefault();
        b.classList.remove('is-drop');
        var drag = editor.layerDrag;
        editor.layerDrag = null;
        reorderLayer(kind, drag.id, id);
      });
      host.appendChild(b);
    }

    var sel = selectionIds();
    ids.forEach(function (id) {
      var n = nodes[id];
      addRow(n.label || id, n.shape || 'box', sel.indexOf(id) >= 0, function () {
        selectNode(id);
      }, 'node', id);
    });
    edges.forEach(function (e, i) {
      var label = e.points ? ('Arrow · ' + e.points.length + ' pt') :
        ((e.from || '?') + ' → ' + (e.to || '?'));
      addRow(label, e.cable || 'edge', edgeIsSelected(i), function () {
        selectEdge(i);
      }, 'edge', String(i));
    });
    drawings.forEach(function (d) {
      addRow('Drawing', d.id || '', s.selectedDrawing === d.id, function () {
        selectDrawing(d.id);
      }, 'drawing', d.id || '');
    });
  }

  function renderMinimap() {
    var wrap = document.getElementById('minimap');
    var svg = document.getElementById('minimapSvg');
    if (!wrap || !svg) return;
    if (!isCanvas()) { wrap.hidden = true; return; }
    wrap.hidden = false;
    wrap.classList.toggle('is-collapsed', minimapCollapsed);

    var s = state.spec;
    var nodes = s.nodes || {};
    var ids = Object.keys(nodes);
    var minX = 0, minY = 0, maxX = s.width || 900, maxY = s.height || 520;
    if (ids.length) {
      minX = Infinity; minY = Infinity; maxX = -Infinity; maxY = -Infinity;
      ids.forEach(function (id) {
        var n = nodes[id];
        var x = n.x || 0, y = n.y || 0;
        var w = n.w || 160, h = n.h || 60;
        minX = Math.min(minX, x);
        minY = Math.min(minY, y);
        maxX = Math.max(maxX, x + w);
        maxY = Math.max(maxY, y + h);
      });
    }
    var pad = 30;
    var x = minX - pad, y = minY - pad;
    var w = Math.max(1, maxX - minX + pad * 2);
    var h = Math.max(1, maxY - minY + pad * 2);
    svg.setAttribute('viewBox', x + ' ' + y + ' ' + w + ' ' + h);
    svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
    svg.innerHTML = '';

    ids.forEach(function (id) {
      var n = nodes[id];
      var r = document.createElementNS(SVG_NS, 'rect');
      r.setAttribute('x', n.x || 0);
      r.setAttribute('y', n.y || 0);
      r.setAttribute('width', n.w || 160);
      r.setAttribute('height', n.h || 60);
      r.setAttribute('rx', 4);
      r.setAttribute('class', 'mm-node');
      svg.appendChild(r);
    });

    var main = stage.querySelector('svg');
    if (main && main.viewBox && main.viewBox.baseVal && main.viewBox.baseVal.width) {
      var vb = main.viewBox.baseVal;
      var v = document.createElementNS(SVG_NS, 'rect');
      v.setAttribute('x', vb.x);
      v.setAttribute('y', vb.y);
      v.setAttribute('width', vb.width);
      v.setAttribute('height', vb.height);
      v.setAttribute('class', 'mm-view');
      svg.appendChild(v);
    }
  }

  var paletteState = { open: false, index: 0, items: [] };

  function switchModule(id) {
    /* Grid is a view preference, not part of a module preset. Keep it when
       switching between flow, chart, canvas, and every other page. */
    var grid = true;
    state.spec = presetFor(id);
    state.spec.grid = grid;
    syncScene();
    syncControls();
    render();
  }

  function paletteCommands() {
    var list = [];
    [['select', 'Select', 'V'], ['pan', 'Pan', 'H'], ['box', 'Box', 'R'],
     ['diamond', 'Diamond', 'D'], ['circle', 'Circle', 'O'], ['arrow', 'Arrow', 'A'],
     ['line', 'Line', 'L'], ['draw', 'Draw', 'P'], ['text', 'Text', 'T'],
     ['eraser', 'Eraser', 'E'], ['laser', 'Laser', 'K']
    ].forEach(function (tool) {
      list.push({
        label: 'Tool · ' + tool[1],
        hint: tool[2],
        run: function () { setTool(tool[0]); }
      });
    });
    list.push({ label: 'Panel · Properties', hint: 'Alt+/', run: function () { setInspector(true); } });
    list.push({ label: 'Panel · Assets', hint: 'L', run: function () { setPanel('assets', true); } });
    list.push({ label: 'Panel · Layers', hint: 'Y', run: function () { setPanel('layers', true); } });
    list.push({ label: 'Insert module · Flow', hint: 'canvas block', run: function () { insertModule('flow'); } });
    list.push({ label: 'Insert module · Reverse proxy', hint: 'canvas block', run: function () { insertModule('reverse-proxy'); } });
    list.push({ label: 'Insert module · Chart', hint: 'canvas block', run: function () { insertModule('chart'); } });
    list.push({ label: 'Insert module · Pipeline', hint: 'canvas block', run: function () { insertModule('pipeline'); } });
    list.push({ label: 'Insert module · Graph', hint: 'canvas block', run: function () { insertModule('graph'); } });
    list.push({ label: 'Action · Add box', hint: 'center', run: function () {
      var c = viewportSceneCenter();
      addNode('box', c.x - 80, c.y - 30, 160, 60);
    } });
    list.push({ label: 'Action · Add text', hint: 'center', run: function () {
      var c = viewportSceneCenter();
      addNode('plain', c.x - 80, c.y - 20, 160, 40);
    } });
    list.push({ label: 'Action · Duplicate', hint: 'Ctrl+D', run: duplicateSelection });
    list.push({ label: 'Action · Copy', hint: 'Ctrl+C', run: copySelection });
    list.push({ label: 'Action · Paste', hint: 'Ctrl+V', run: pasteClipboard });
    list.push({ label: 'Action · Delete selection', hint: 'Del', run: deleteSelected });
    list.push({ label: 'Action · Select all', hint: '', run: selectAllNodes });
    list.push({ label: 'Action · Zoom to fit', hint: '', run: function () { document.getElementById('zoomFit').click(); } });
    list.push({ label: 'Action · Undo', hint: 'Ctrl+Z', run: undo });
    list.push({ label: 'Action · Redo', hint: 'Ctrl+Shift+Z', run: redo });
    list.push({ label: 'Action · Export JSON', hint: '', run: function () { document.getElementById('exportJson').click(); } });
    list.push({ label: 'Action · Export SVG', hint: '', run: function () { document.getElementById('exportSvg').click(); } });
    list.push({ label: 'Action · Focus mode', hint: 'Ctrl+.', run: function () { toggleFocus(); } });
    return list;
  }

  function highlightPalette() {
    var list = document.getElementById('paletteList');
    if (!list) return;
    Array.prototype.forEach.call(list.querySelectorAll('.palette-item'), function (el, i) {
      el.classList.toggle('is-active', i === paletteState.index);
      if (i === paletteState.index && el.scrollIntoView) el.scrollIntoView({ block: 'nearest' });
    });
  }

  function renderPalette() {
    var input = document.getElementById('paletteInput');
    var list = document.getElementById('paletteList');
    if (!input || !list) return;
    var q = input.value.trim().toLowerCase();
    var items = paletteCommands().filter(function (c) {
      return !q || c.label.toLowerCase().indexOf(q) >= 0;
    });
    paletteState.items = items;
    paletteState.index = 0;
    list.innerHTML = '';
    if (!items.length) {
      var empty = document.createElement('div');
      empty.className = 'palette-empty';
      empty.textContent = 'No matching command.';
      list.appendChild(empty);
      return;
    }
    items.forEach(function (c, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'palette-item';
      b.textContent = c.label;
      if (c.hint) {
        var h = document.createElement('small');
        h.textContent = c.hint;
        b.appendChild(h);
      }
      b.addEventListener('mouseenter', function () { paletteState.index = i; highlightPalette(); });
      b.addEventListener('click', function () { runPalette(i); });
      list.appendChild(b);
    });
    highlightPalette();
  }

  function openPalette(query) {
    var box = document.getElementById('palette');
    var input = document.getElementById('paletteInput');
    if (!box || !input) return;
    paletteState.open = true;
    box.hidden = false;
    input.value = query || '';
    renderPalette();
    input.focus();
    input.select();
  }

  function closePalette() {
    var box = document.getElementById('palette');
    var input = document.getElementById('paletteInput');
    paletteState.open = false;
    if (box) box.hidden = true;
    if (input) input.blur();
  }

  function togglePalette() {
    if (paletteState.open) closePalette();
    else openPalette('');
  }

  function runPalette(i) {
    var item = paletteState.items[i];
    if (!item) return;
    closePalette();
    item.run();
  }

  var ctxState = { open: false, x: 0, y: 0, point: null };

  function closeCtx() {
    var menu = document.getElementById('ctxMenu');
    ctxState.open = false;
    if (menu) menu.hidden = true;
  }

  function openCtx(ev) {
    var menu = document.getElementById('ctxMenu');
    if (!menu) return;
    ctxState.open = true;
    ctxState.x = ev.clientX;
    ctxState.y = ev.clientY;
    menu.hidden = false;
    menu.style.left = '0px';
    menu.style.top = '0px';
    var w = menu.offsetWidth;
    var h = menu.offsetHeight;
    menu.style.left = Math.max(8, Math.min(ev.clientX, window.innerWidth - w - 8)) + 'px';
    menu.style.top = Math.max(8, Math.min(ev.clientY, window.innerHeight - h - 8)) + 'px';
  }

  function ctxCommand(cmd) {
    var p = ctxState.point;
    closeCtx();
    if (cmd === 'add-box') addNode('box', (p ? p.x : 400) - 80, (p ? p.y : 260) - 30, 160, 60);
    if (cmd === 'add-text') addNode('plain', (p ? p.x : 400) - 80, (p ? p.y : 260) - 20, 160, 40);
    if (cmd === 'paste') pasteClipboard();
    if (cmd === 'duplicate') duplicateSelection();
    if (cmd === 'delete') deleteSelected();
    if (cmd === 'select-all') selectAllNodes();
    if (cmd === 'fit') document.getElementById('zoomFit').click();
  }

  function toggleFocus(force) {
    var on = force === undefined ? !document.body.classList.contains('focus-mode') : !!force;
    document.body.classList.toggle('focus-mode', on);
    if (on) closePanels();
  }

  function isTypingTarget(el) {
    if (!el) return false;
    var tag = (el.tagName || '').toLowerCase();
    return tag === 'input' || tag === 'textarea' || tag === 'select' || el.isContentEditable;
  }

  function setTool(tool) {
    editor.tool = tool;
    editor.from = null;
    Array.prototype.forEach.call(document.querySelectorAll('.alur-canvas-node.is-connect-from'), function (el) {
      el.classList.remove('is-connect-from');
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-tool]'), function (b) {
      b.classList.toggle('is-on', b.getAttribute('data-tool') === tool);
    });
    syncEditor();
  }

  function selectionIds() {
    var s = state.spec.selected;
    if (Array.isArray(s)) return s.filter(function (id) { return state.spec.nodes && state.spec.nodes[id]; });
    return s && state.spec.nodes && state.spec.nodes[s] ? [s] : [];
  }

  function drawSelectionBoxes() {
    var overlay = overlayLayer();
    if (!overlay) return;
    Array.prototype.forEach.call(overlay.querySelectorAll('.alur-selection-box'), function (el) {
      if (el.parentNode) el.parentNode.removeChild(el);
    });
    var ids = selectionIds();
    if (!ids.length) return;
    var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    ids.forEach(function (id) {
      var n = state.spec.nodes[id];
      if (!n) return;
      var w = n.w || 160;
      var h = n.h || 60;
      var x = n.x || 0;
      var y = n.y || 0;
      AlurKit.rect(overlay, x, y, w, h, 'alur-selection-box', {
        'data-select-box': id
      });
      minX = Math.min(minX, x);
      minY = Math.min(minY, y);
      maxX = Math.max(maxX, x + w);
      maxY = Math.max(maxY, y + h);
    });
    if (ids.length > 1 && maxX > minX && maxY > minY) {
      AlurKit.rect(overlay, minX, minY, maxX - minX, maxY - minY, 'alur-selection-box is-group', {
        'data-select-group': '1'
      });
    }
  }

  function drawSelectionHandles() {
    drawSelectionBoxes();
    var layer = stage.querySelector('.alur-layer-handles');
    if (!layer) return;
    layer.innerHTML = '';
    var ids = selectionIds();
    if (ids.length !== 1) return;
    var n = state.spec.nodes[ids[0]];
    if (!n) return;
    var w = n.w || 160;
    var h = n.h || 60;
    var x = n.x || 0;
    var y = n.y || 0;
    [['nw', 0, 0], ['n', w / 2, 0], ['ne', w, 0], ['e', w, h / 2],
     ['se', w, h], ['s', w / 2, h], ['sw', 0, h], ['w', 0, h / 2]
    ].forEach(function (spec) {
      var r = AlurKit.rect(layer, x + spec[1] - 4, y + spec[2] - 4, 8, 8, 'alur-handle', {
        'data-handle': spec[0],
        'data-node-id': n.id
      });
      r.setAttribute('stroke-width', '1.5');
    });
  }

  function updateSelectionVisual() {
    var s = state.spec;
    var ids = selectionIds();
    var on = {};
    ids.forEach(function (id) { on[id] = true; });
    Array.prototype.forEach.call(stage.querySelectorAll('.alur-canvas-node'), function (el) {
      el.classList.toggle('is-selected', !!on[el.getAttribute('data-node-id')]);
    });
    Array.prototype.forEach.call(stage.querySelectorAll('.alur-canvas-edge'), function (el) {
      var i = parseInt(el.getAttribute('data-edge'), 10);
      el.classList.toggle('is-selected', edgeIsSelected(i));
      var e = (s.edges || [])[i];
      el.classList.toggle('is-linked', !!(e && (on[e.from] || on[e.to])));
    });
    Array.prototype.forEach.call(stage.querySelectorAll('.alur-drawing'), function (el) {
      el.classList.toggle('is-selected', s.selectedDrawing === el.getAttribute('data-drawing'));
    });
    drawSelectionHandles();
  }

  function edgeIsSelected(i) {
    var s = state.spec;
    if (s.selectedEdge === i) return true;
    return !!(s.selectedEdges && s.selectedEdges.indexOf(i) >= 0);
  }

  function setSelection(ids) {
    var s = state.spec;
    ids = (ids || []).filter(function (id) { return s.nodes && s.nodes[id]; });
    s.selected = ids.length === 1 ? ids[0] : (ids.length ? ids : null);
    s.selectedEdge = null;
    s.selectedEdges = [];
    s.selectedDrawing = null;
    touchSpec();
    syncEditor();
    updateSelectionVisual();
    renderLayers();
    /* Panel 4 (Chart) mengikuti blok yang dipilih. */
    syncControls();
  }

  function selectAllNodes() {
    if (!isCanvas()) return;
    var s = state.spec;
    var nodeIds = Object.keys(s.nodes || {});
    var edgeIds = (s.edges || []).map(function (e, i) { return i; });
    s.selected = nodeIds.length ? nodeIds : null;
    s.selectedEdges = edgeIds;
    s.selectedEdge = null;
    s.selectedDrawing = null;
    touchSpec();
    syncEditor();
    updateSelectionVisual();
    renderLayers();
  }

  function selectNode(id, additive) {
    if (!id) { setSelection([]); return; }
    var ids = selectionIds();
    if (additive) {
      if (ids.indexOf(id) >= 0) return;
      ids = ids.concat([id]);
    } else if (ids.length === 1 && ids[0] === id) {
      return;
    } else {
      ids = [id];
    }
    setSelection(ids);
  }

  function selectEdge(i) {
    var s = state.spec;
    var list = s.selectedEdges || [];
    var wasOn = list.indexOf(i) >= 0;
    s.selectedEdges = wasOn ? [] : [i];
    s.selectedEdge = wasOn ? null : i;
    s.selected = null;
    s.selectedDrawing = null;
    touchSpec();
    syncEditor();
    render();
  }

  function selectDrawing(id) {
    state.spec.selectedDrawing = (state.spec.selectedDrawing === id) ? null : id;
    state.spec.selected = null;
    state.spec.selectedEdge = null;
    state.spec.selectedEdges = [];
    touchSpec();
    syncEditor();
    render();
  }

  function ensureTableData(n) {
    if (!n.columns || !n.columns.length) n.columns = ['Column 1', 'Column 2', 'Column 3'];
    if (!n.rows || !n.rows.length) n.rows = [['', '', ''], ['', '', ''], ['', '', '']];
    n.rows.forEach(function (row) {
      while (row.length < n.columns.length) row.push('');
      row.length = n.columns.length;
    });
  }

  function snapGrid(v) { return Math.round((v || 0) / GRID) * GRID; }

  function addNode(shape, x, y, w, h) {
    if (!isCanvas()) switchModule('canvas');
    var s = state.spec;
    s.nodes = s.nodes || {};
    var id, n = 1;
    do { id = 'n' + (++nodeSeq); } while (s.nodes[id]);
    var isText = shape === 'text';
    var nodeShape = isText ? 'plain' : shape;
    s.nodes[id] = {
      id: id,
      x: snapGrid(x),
      y: snapGrid(y),
      w: Math.max(GRID, snapGrid(w)),
      h: Math.max(GRID, snapGrid(h)),
      shape: nodeShape,
      label: '',
      sub: '',
      color: isText ? editor.textStyle.color : COLOR_KEYS[Object.keys(s.nodes).length % COLOR_KEYS.length]
    };
    if (shape === 'table') ensureTableData(s.nodes[id]);
    if (isText) {
      s.nodes[id].isText = true;
      s.nodes[id].textRole = 'text';
      s.nodes[id].fontFamily = editor.textStyle.fontFamily;
      s.nodes[id].fontSize = editor.textStyle.fontSize;
      s.nodes[id].fontWeight = editor.textStyle.bold ? 700 : 400;
      s.nodes[id].fontStyle = editor.textStyle.italic ? 'italic' : 'normal';
      s.nodes[id].textAlign = editor.textStyle.align;
      s.nodes[id].lineHeight = editor.textStyle.lineHeight;
      s.nodes[id].opacity = editor.textStyle.opacity;
    }
    s.selected = id;
    s.selectedEdge = null;
    s.selectedDrawing = null;
    touchSpec();
    syncControls();
    syncEditor();
    render();
    return id;
  }

  function deleteSelected() {
    var s = state.spec;
    var ids = selectionIds();
    var eids = (s.selectedEdges || []).slice();
    if (s.selectedEdge != null && eids.indexOf(s.selectedEdge) < 0) eids.push(s.selectedEdge);
    if (!s.selectedDrawing && !eids.length && !ids.length) return;
    pushHistory();
    if (s.selectedDrawing) {
      s.drawings = (s.drawings || []).filter(function (d) { return d.id !== s.selectedDrawing; });
      s.selectedDrawing = null;
    }
    if (eids.length) {
      eids.sort(function (a, b) { return b - a; }).forEach(function (i) {
        if (s.edges && s.edges[i]) s.edges.splice(i, 1);
      });
    }
    if (ids.length) {
      ids.forEach(function (id) { delete s.nodes[id]; });
      s.edges = (s.edges || []).filter(function (e) {
        return ids.indexOf(e.from) < 0 && ids.indexOf(e.to) < 0;
      });
    }
    s.selected = null;
    s.selectedEdge = null;
    s.selectedEdges = [];
    touchSpec();
    syncControls();
    syncEditor();
    render();
  }

  function snapshotSelection() {
    var s = state.spec;
    var ids = selectionIds();
    var nodes = ids.map(function (id) {
      var copy = {};
      Object.keys(s.nodes[id]).forEach(function (k) { copy[k] = s.nodes[id][k]; });
      return copy;
    });
    var edges = (s.edges || []).filter(function (e) {
      return ids.indexOf(e.from) >= 0 && ids.indexOf(e.to) >= 0;
    }).map(function (e) {
      var copy = {};
      Object.keys(e).forEach(function (k) { copy[k] = e[k]; });
      return copy;
    });
    return { nodes: nodes, edges: edges };
  }

  function pasteNodes(snapshot, dx, dy) {
    var s = state.spec;
    var map = {};
    var newIds = [];
    var created = {};
    snapshot.nodes.forEach(function (n) {
      var id;
      do { id = 'n' + (++nodeSeq); } while (s.nodes[id]);
      map[n.id] = id;
      var copy = {};
      Object.keys(n).forEach(function (k) { copy[k] = n[k]; });
      copy.id = id;
      copy.x = Math.round((n.x || 0) + dx);
      copy.y = Math.round((n.y || 0) + dy);
      created[id] = copy;
      newIds.push(id);
    });
    Object.keys(created).forEach(function (id) { s.nodes[id] = created[id]; });
    s.edges = s.edges || [];
    snapshot.edges.forEach(function (e) {
      var from = map[e.from];
      var to = map[e.to];
      if (!from || !to) return;
      var copy = {};
      Object.keys(e).forEach(function (k) { copy[k] = e[k]; });
      copy.from = from;
      copy.to = to;
      s.edges.push(copy);
    });
    s.selected = newIds.length === 1 ? newIds[0] : newIds;
    s.selectedEdge = null;
    s.selectedDrawing = null;
    touchSpec();
    syncControls();
    syncEditor();
    render();
  }

  function duplicateSelection() {
    var snap = snapshotSelection();
    if (!snap.nodes.length) return;
    pushHistory();
    pasteNodes(snap, 26, 26);
  }

  function copySelection() {
    var snap = snapshotSelection();
    if (!snap.nodes.length) return;
    editor.clipboard = snap;
  }

  function pasteClipboard() {
    if (!editor.clipboard || !editor.clipboard.nodes.length) return;
    pushHistory();
    pasteNodes(editor.clipboard, 26, 26);
  }

  function alignSelection(mode) {
    var ids = selectionIds();
    if (ids.length < 2) return;
    var s = state.spec;
    var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    ids.forEach(function (id) {
      var n = s.nodes[id];
      minX = Math.min(minX, n.x || 0);
      minY = Math.min(minY, n.y || 0);
      maxX = Math.max(maxX, (n.x || 0) + (n.w || 160));
      maxY = Math.max(maxY, (n.y || 0) + (n.h || 60));
    });
    pushHistory();
    ids.forEach(function (id) {
      var n = s.nodes[id];
      var w = n.w || 160;
      var h = n.h || 60;
      if (mode === 'left') n.x = minX;
      if (mode === 'right') n.x = maxX - w;
      if (mode === 'center') n.x = Math.round((minX + maxX) / 2 - w / 2);
      if (mode === 'top') n.y = minY;
      if (mode === 'bottom') n.y = maxY - h;
      if (mode === 'middle') n.y = Math.round((minY + maxY) / 2 - h / 2);
    });
    touchSpec();
    syncEditor();
    render();
  }

  function nudgeSelection(dx, dy) {
    var ids = selectionIds();
    if (!ids.length) return;
    pushHistory();
    ids.forEach(function (id) {
      var n = state.spec.nodes[id];
      n.x = Math.round((n.x || 0) + dx);
      n.y = Math.round((n.y || 0) + dy);
    });
    touchSpec();
    syncEditor();
    render();
  }

  function field(labelText, input) {
    var l = document.createElement('label');
    l.textContent = labelText;
    l.appendChild(input);
    return l;
  }

  function textField(labelText, value, onInput) {
    var input = document.createElement('input');
    input.type = 'text';
    input.value = value || '';
    input.addEventListener('input', function () {
      onInput(input.value);
      touchSpec();
      render();
    });
    return field(labelText, input);
  }

  function selectField(labelText, options, value, onChange) {
    var sel = document.createElement('select');
    options.forEach(function (o) {
      var opt = document.createElement('option');
      opt.value = o[0];
      opt.textContent = o[1];
      if (o[0] === value) opt.selected = true;
      sel.appendChild(opt);
    });
    sel.addEventListener('change', function () {
      onChange(sel.value);
      touchSpec();
      render();
    });
    return field(labelText, sel);
  }

  function plainHint(text) {
    var p = document.createElement('p');
    p.className = 'hint';
    p.style.margin = '0';
    p.textContent = text;
    return p;
  }

  function renderMultiInspector(host, ids) {
    var p = document.createElement('p');
    p.className = 'hint';
    p.style.margin = '0';
    p.textContent = ids.length + ' nodes selected. Drag any of them to move the group.';
    host.appendChild(p);

    var row = document.createElement('div');
    row.className = 'align-row';
    [['left', 'Left'], ['center', 'Center'], ['right', 'Right'],
     ['top', 'Top'], ['middle', 'Middle'], ['bottom', 'Bottom']
    ].forEach(function (a) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'tool';
      b.textContent = a[1];
      b.title = 'Align ' + a[1].toLowerCase();
      b.addEventListener('click', function () { alignSelection(a[0]); });
      row.appendChild(b);
    });
    host.appendChild(row);

    var dup = document.createElement('button');
    dup.type = 'button';
    dup.className = 'ghost';
    dup.textContent = 'Duplicate selection';
    dup.addEventListener('click', duplicateSelection);
    host.appendChild(dup);
  }

  function renderNodeInspector() {
    var host = document.getElementById('nodeInspector');
    host.innerHTML = '';
    var ids = selectionIds();
    var id = ids.length === 1 ? ids[0] : null;
    var n = id && state.spec.nodes[id];
    if (!n) {
      if (ids.length > 1) { renderMultiInspector(host, ids); return; }
      host.innerHTML = '<p class="hint">No node selected.</p>';
      return;
    }

    host.appendChild(textField('Label', n.label, function (v) { n.label = v; }));
    host.appendChild(textField('Sub', n.sub, function (v) { n.sub = v; }));
    /* Tables and charts own their rendering; switching the shape would break
       them, so the shape picker stays out of their way. */
    if (n.shape !== 'table' && n.shape !== 'chart') {
      host.appendChild(selectField('Shape', [
        ['box', 'Box'], ['pill', 'Pill'], ['circle', 'Circle'], ['plain', 'Plain (no box)']
      ], n.shape || 'box', function (v) { n.shape = v; }));
    }
    host.appendChild(textField('Color hex', AlurKit.color(n.color || 'blue'), function (v) {
      if (/^#([0-9a-f]{3}|[0-9a-f]{6})$/i.test(v)) n.color = v;
    }));

    var grid = document.createElement('div');
    grid.className = 'editor-grid';
    [['x', 'X'], ['y', 'Y'], ['w', 'W'], ['h', 'H']].forEach(function (p) {
      var input = document.createElement('input');
      input.type = 'number';
      input.value = n[p[0]];
      input.addEventListener('input', function () {
        n[p[0]] = parseFloat(input.value) || 0;
        touchSpec();
        render();
      });
      var l = document.createElement('label');
      l.textContent = p[1];
      l.appendChild(input);
      grid.appendChild(l);
    });
    host.appendChild(field('Position & size', grid));

    if (n.logo || (n.logos && n.logos.length)) {
      var clear = document.createElement('button');
      clear.type = 'button';
      clear.className = 'ghost';
      clear.textContent = 'Remove logo';
      clear.addEventListener('click', function () {
        pushHistory();
        delete n.logo;
        delete n.logos;
        touchSpec();
        syncControls();
        syncEditor();
        render();
      });
      host.appendChild(clear);
    } else {
      host.appendChild(plainHint('Pick a logo in the Logo library →'));
    }
  }

  function renderEdgeInspector() {
    var host = document.getElementById('edgeInspector');
    host.innerHTML = '';
    var i = state.spec.selectedEdge;
    var e = (i != null) ? state.spec.edges[i] : null;
    if (!e) { host.innerHTML = '<p class="hint">No edge selected.</p>'; return; }

    host.appendChild(selectField('Cable',
      CABLES.map(function (c) { return [c.id, c.label]; }),
      e.cable || state.spec.cable || 'solid',
      function (v) { e.cable = v; }));
    host.appendChild(selectField('Motion',
      MOTIONS.map(function (m) { return [m.id, m.label]; }),
      e.motion || state.spec.motion || 'flow',
      function (v) { e.motion = v; }));
    host.appendChild(textField('Color hex', AlurKit.color(e.color || 'blue'), function (v) {
      if (/^#([0-9a-f]{3}|[0-9a-f]{6})$/i.test(v)) e.color = v;
    }));
    host.appendChild(textField('Label', e.label, function (v) { e.label = v; }));
  }

  var SHAPE_COLORS = ['transparent', 'blue', 'green', 'amber', 'red', 'purple', 'cyan', 'pink', 'lime', 'slate', 'white'];
  var SHAPE_STROKES = ['solid', 'dashed', 'dotted'];
  var SHAPE_SLOP = [['architect', 'Architect'], ['artist', 'Artist'], ['cartoonist', 'Cartoonist']];
  var SHAPE_EDGES = [['sharp', 'Sharp'], ['round', 'Round']];
  var SHAPE_FILLS = [['hachure', 'Hachure'], ['cross-hatch', 'Cross-hatch'], ['solid', 'Solid']];
  var ARROW_TYPES = [['arrow', 'Arrow'], ['triangle', 'Triangle'], ['circle', 'Circle'], ['diamond', 'Diamond'], ['bar', 'Bar'], ['none', 'None']];

  function selectionInfo() {
    var s = state.spec;
    if (s.selectedEdge != null && s.edges && s.edges[s.selectedEdge]) {
      return { kind: 'edge', edge: s.edges[s.selectedEdge], index: s.selectedEdge };
    }
    if (s.selectedDrawing && s.drawings) {
      var drawing = s.drawings.find(function (d) { return d.id === s.selectedDrawing; });
      if (drawing) return { kind: 'drawing', drawing: drawing, id: s.selectedDrawing };
    }
    var ids = selectionIds();
    if (ids.length === 1 && s.nodes && s.nodes[ids[0]]) {
      return { kind: 'node', node: s.nodes[ids[0]], id: ids[0] };
    }
    if (ids.length > 1) return { kind: 'multi', ids: ids };
    return null;
  }

  function shapeSwatches(value, onPick, colors) {
    var wrap = document.createElement('div');
    wrap.className = 'swatches';
    (colors || SHAPE_COLORS).forEach(function (c) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'swatch' + (AlurKit.color(value) === AlurKit.color(c) ? ' is-on' : '');
      b.dataset.color = c;
      b.title = c;
      if (c !== 'transparent') b.style.background = AlurKit.color(c);
      b.addEventListener('click', function () { onPick(c); });
      wrap.appendChild(b);
    });

    var hex = document.createElement('input');
    hex.type = 'text';
    hex.className = 'color-hex';
    hex.value = value === 'transparent' ? 'transparent' : AlurKit.color(value);
    hex.title = 'Hex color';
    hex.setAttribute('aria-label', 'Hex color');
    function commitHex() {
      var v = hex.value.trim().toLowerCase();
      if (v === 'transparent') { onPick('transparent'); return; }
      if (/^#([0-9a-f]{3}|[0-9a-f]{6})$/.test(v)) {
        onPick(v);
      } else {
        hex.value = value === 'transparent' ? 'transparent' : AlurKit.color(value);
      }
    }
    hex.addEventListener('change', commitHex);
    hex.addEventListener('keydown', function (ev) {
      if (ev.key === 'Enter') { ev.preventDefault(); commitHex(); }
    });
    wrap.appendChild(hex);
    return wrap;
  }

  function shapeRange(label, min, max, step, value, suffix, onInput, onStart) {
    var wrap = document.createElement('label');
    wrap.className = 'shape-group';
    var head = document.createElement('span');
    head.className = 'shape-label';
    head.textContent = label + ' · ' + value + (suffix || '');
    wrap.appendChild(head);
    var input = document.createElement('input');
    input.type = 'range';
    input.min = min; input.max = max; input.step = step; input.value = value;
    var started = false;
    function start() {
      if (started) return;
      started = true;
      if (onStart) onStart();
    }
    input.addEventListener('pointerdown', start);
    input.addEventListener('keydown', start);
    input.addEventListener('input', function () {
      head.textContent = label + ' · ' + input.value + (suffix || '');
      if (onInput) onInput(parseFloat(input.value));
    });
    input.addEventListener('change', function () {
      if (!started) start();
      started = false;
    });
    wrap.appendChild(input);
    return wrap;
  }

  function shapeSelect(label, options, value, onChange) {
    var wrap = document.createElement('label');
    wrap.className = 'shape-group';
    var span = document.createElement('span');
    span.className = 'shape-label';
    span.textContent = label;
    wrap.appendChild(span);
    var sel = document.createElement('select');
    options.forEach(function (o) {
      var opt = document.createElement('option');
      opt.value = o[0]; opt.textContent = o[1];
      if (o[0] === value) opt.selected = true;
      sel.appendChild(opt);
    });
    sel.addEventListener('change', function () { onChange(sel.value); });
    wrap.appendChild(sel);
    return wrap;
  }

  function shapeCheck(label, value, onChange) {
    var wrap = document.createElement('label');
    wrap.className = 'checkline';
    var input = document.createElement('input');
    input.type = 'checkbox';
    input.checked = !!value;
    input.addEventListener('change', function () { onChange(input.checked); });
    wrap.appendChild(input);
    var span = document.createElement('span');
    span.textContent = label;
    wrap.appendChild(span);
    return wrap;
  }

  function shapeButtonRow(items) {
    var row = document.createElement('div');
    row.className = 'shape-row';
    items.forEach(function (it) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'ghost';
      b.textContent = it[0];
      b.title = it[1] || it[0];
      b.addEventListener('click', it[2]);
      row.appendChild(b);
    });
    return row;
  }

  function shapeOptionRow(label, options, value, onChange) {
    var wrap = document.createElement('div');
    wrap.className = 'shape-group';
    var span = document.createElement('span');
    span.className = 'shape-label';
    span.textContent = label;
    wrap.appendChild(span);
    var row = document.createElement('div');
    row.className = 'shape-row';
    options.forEach(function (o) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'ghost' + (o[0] === value ? ' is-on' : '');
      b.textContent = o[1];
      b.title = o[1];
      b.addEventListener('click', function () { onChange(o[0]); });
      row.appendChild(b);
    });
    wrap.appendChild(row);
    return wrap;
  }

  var TEXT_SIZES = [['S', 12], ['M', 16], ['L', 20], ['XL', 28]];

  function textSizeRow(value, onChange) {
    var wrap = document.createElement('div');
    wrap.className = 'shape-group';
    var span = document.createElement('span');
    span.className = 'shape-label';
    span.textContent = 'Size';
    wrap.appendChild(span);
    var row = document.createElement('div');
    row.className = 'shape-row text-size-row';
    TEXT_SIZES.forEach(function (it) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'ghost' + (Number(value) === it[1] ? ' is-on' : '');
      b.textContent = it[0];
      b.title = it[0] + ' · ' + it[1] + 'px';
      b.setAttribute('aria-label', it[0] + ' ' + it[1] + ' pixels');
      b.addEventListener('click', function () { onChange(it[1]); });
      row.appendChild(b);
    });
    wrap.appendChild(row);
    return wrap;
  }

  function reorderLayer(kind, fromId, toId) {
    var s = state.spec;
    if (fromId === toId) return;
    if (kind === 'edge') {
      var ei = parseInt(fromId, 10);
      var ti = parseInt(toId, 10);
      if (isNaN(ei) || isNaN(ti) || !s.edges || !s.edges[ei]) return;
      pushHistory();
      var edge = s.edges.splice(ei, 1)[0];
      s.edges.splice(ti, 0, edge);
      var movedAt = s.edges.indexOf(edge);
      s.selectedEdge = movedAt;
      s.selectedEdges = [movedAt];
      s.selected = null;
      s.selectedDrawing = null;
      touchSpec();
      syncControls();
      render();
      return;
    }
    pushHistory();
    if (kind === 'node') {
      var entries = Object.keys(s.nodes || {}).map(function (k) { return [k, s.nodes[k]]; });
      var from = entries.findIndex(function (x) { return x[0] === fromId; });
      var to = entries.findIndex(function (x) { return x[0] === toId; });
      if (from < 0 || to < 0) return;
      var moved = entries.splice(from, 1)[0];
      entries.splice(to, 0, moved);
      var copy = {};
      entries.forEach(function (x) { copy[x[0]] = x[1]; });
      s.nodes = copy;
    } else if (kind === 'drawing') {
      var arr = s.drawings || [];
      var fi = arr.findIndex(function (d) { return d.id === fromId; });
      var di = arr.findIndex(function (d) { return d.id === toId; });
      if (fi < 0 || di < 0) return;
      var drawing = arr.splice(fi, 1)[0];
      arr.splice(di, 0, drawing);
      s.drawings = arr;
    }
    touchSpec();
    syncControls();
    render();
  }

  function moveNodeLayer(id, dir) {
    var nodes = state.spec.nodes || {};
    if (!nodes[id]) return;
    var copy = {};
    var ids = Object.keys(nodes).filter(function (k) { return k !== id; });
    if (dir === 'front') ids.push(id);
    else ids.unshift(id);
    ids.forEach(function (k) { copy[k] = nodes[k]; });
    state.spec.nodes = copy;
    pushHistory();
    touchSpec();
    syncControls();
    render();
  }

  function moveEdgeLayer(index, dir) {
    var edges = state.spec.edges || [];
    if (!edges[index]) return;
    var e = edges.splice(index, 1)[0];
    if (dir === 'front') edges.push(e);
    else edges.unshift(e);
    state.spec.edges = edges;
    state.spec.selectedEdge = edges.indexOf(e);
    pushHistory();
    touchSpec();
    syncControls();
    render();
  }

  function applyNodePatch(patch) {
    var info = selectionInfo();
    if (!info || info.kind !== 'node') return;
    pushHistory();
    Object.keys(patch).forEach(function (k) { info.node[k] = patch[k]; });
    touchSpec();
    syncControls();
    render();
  }

  function applyEdgePatch(patch) {
    var info = selectionInfo();
    if (!info || info.kind !== 'edge') return;
    pushHistory();
    Object.keys(patch).forEach(function (k) { info.edge[k] = patch[k]; });
    touchSpec();
    syncControls();
    render();
  }

  function liveNodePatch(patch) {
    var info = selectionInfo();
    if (!info || info.kind !== 'node') return;
    Object.keys(patch).forEach(function (k) { info.node[k] = patch[k]; });
    var el = stage.querySelector('.alur-canvas-node[data-node-id="' + info.id + '"]');
    if (el) {
      if (patch.opacity != null) el.setAttribute('opacity', patch.opacity);
      if (patch.strokeWidth != null) {
        var box = el.querySelector('.alur-node-box');
        if (box) {
          box.setAttribute('stroke-width', patch.strokeWidth);
          box.style.strokeWidth = patch.strokeWidth;
        }
        var rough = el.querySelector('.alur-node-rough');
        if (rough) rough.setAttribute('stroke-width', Math.max(0.6, patch.strokeWidth * 0.55));
      }
    }
    touchSpec();
  }

  function liveEdgePatch(patch) {
    var info = selectionInfo();
    if (!info || info.kind !== 'edge') return;
    Object.keys(patch).forEach(function (k) { info.edge[k] = patch[k]; });
    var main = stage.querySelector('.alur-canvas-edge[data-edge="' + info.index + '"]');
    if (main) {
      var group = main.parentNode;
      if (patch.width != null && group && group.querySelectorAll) {
        Array.prototype.forEach.call(group.querySelectorAll('path'), function (p) {
          p.setAttribute('stroke-width', patch.width);
        });
      }
      if (patch.opacity != null && group) group.setAttribute('opacity', patch.opacity);
    }
    touchSpec();
  }

  function saveTextStyle() {
    try { localStorage.setItem('ruang.textStyle.v1', JSON.stringify(editor.textStyle)); } catch (err) {}
  }

  function savePenStyle() {
    try { localStorage.setItem('ruang.penStyle.v1', JSON.stringify(editor.penStyle)); } catch (err) {}
  }

  function applyDrawingPatch(patch) {
    var info = selectionInfo();
    if (!info || info.kind !== 'drawing') return;
    pushHistory();
    Object.keys(patch).forEach(function (k) { info.drawing[k] = patch[k]; });
    touchSpec();
    syncControls();
    render();
  }

  function liveDrawingPatch(patch) {
    var info = selectionInfo();
    if (!info || info.kind !== 'drawing') return;
    Object.keys(patch).forEach(function (k) { info.drawing[k] = patch[k]; });
    var el = stage.querySelector('.alur-drawing[data-drawing="' + info.id + '"]');
    if (el) {
      if (patch.color != null) el.setAttribute('stroke', AlurKit.color(patch.color));
      if (patch.width != null) el.setAttribute('stroke-width', patch.width);
      if (patch.strokeStyle != null) {
        el.setAttribute('stroke-dasharray', patch.strokeStyle === 'dashed' ? '7 5' :
          (patch.strokeStyle === 'dotted' ? '2 4' : ''));
      }
      if (patch.opacity != null) el.setAttribute('opacity', patch.opacity);
    }
    touchSpec();
  }

  function liveTextNodePatch(patch, n) {
    var info = selectionInfo();
    var target = (info && info.kind === 'node') ? info.node : n;
    if (!target) return;
    var el = info && info.id ? stage.querySelector('.alur-canvas-node[data-node-id="' + info.id + '"]') : null;
    if (patch.opacity !== undefined) {
      target.opacity = patch.opacity;
      if (el) el.setAttribute('opacity', patch.opacity);
    }
    if (patch.lineHeight !== undefined) {
      target.lineHeight = patch.lineHeight;
      var label = el && el.querySelector('.alur-node-label');
      var spans = label ? label.querySelectorAll('tspan') : [];
      if (spans.length) {
        var size = target.fontSize || 16;
        var lh = Math.max(1, target.lineHeight || 1.35);
        var baseY = parseFloat(spans[0].getAttribute('y')) || 0;
        for (var i = 0; i < spans.length; i++) {
          spans[i].setAttribute('y', baseY + i * size * lh);
        }
        var sub = el.querySelector('.alur-node-sub');
        if (sub) sub.setAttribute('y', baseY + size * lh + 2);
      }
    }
    touchSpec();
  }

  function updateTextStyle(patch, n, isDefault) {
    if (!isDefault && n) {
      var nodePatch = {};
      if (patch.fontFamily !== undefined) nodePatch.fontFamily = patch.fontFamily;
      if (patch.fontSize !== undefined) nodePatch.fontSize = patch.fontSize;
      if (patch.color !== undefined) nodePatch.color = patch.color;
      if (patch.bold !== undefined) nodePatch.fontWeight = patch.bold ? 700 : 400;
      if (patch.italic !== undefined) nodePatch.fontStyle = patch.italic ? 'italic' : 'normal';
      if (patch.align !== undefined) nodePatch.textAlign = patch.align;
      if (patch.textDecoration !== undefined) nodePatch.textDecoration = patch.textDecoration;
      if (patch.lineHeight !== undefined) nodePatch.lineHeight = patch.lineHeight;
      if (patch.opacity !== undefined) nodePatch.opacity = patch.opacity;
      var liveOnly = (patch.lineHeight !== undefined || patch.opacity !== undefined) &&
        patch.fontSize === undefined && patch.color === undefined &&
        patch.bold === undefined && patch.italic === undefined && patch.align === undefined &&
        patch.textDecoration === undefined;
      if (liveOnly) liveTextNodePatch(nodePatch, n);
      else applyNodePatch(nodePatch);
    }
    Object.keys(patch).forEach(function (k) { editor.textStyle[k] = patch[k]; });
    saveTextStyle();
    if (isDefault) {
      var structural = patch.fontFamily !== undefined || patch.fontSize !== undefined ||
        patch.color !== undefined || patch.bold !== undefined ||
        patch.italic !== undefined || patch.align !== undefined;
      if (structural) syncShapePanel();
    }
  }

  function updatePenStyle(patch, d, isDefault, live) {
    if (!isDefault && d) {
      if (live) liveDrawingPatch(patch);
      else applyDrawingPatch(patch);
    }
    Object.keys(patch).forEach(function (k) { editor.penStyle[k] = patch[k]; });
    savePenStyle();
    if (isDefault && (patch.color !== undefined || patch.strokeStyle !== undefined)) syncShapePanel();
  }

  function renderTextStyle(host, n, isDefault) {
    var st = n || editor.textStyle;
    var bold = n ? (n.fontWeight || 400) >= 700 : !!st.bold;
    var italic = n ? n.fontStyle === 'italic' : !!st.italic;
    var align = n ? (n.textAlign || 'left') : (st.align || 'left');
    var size = n ? (n.fontSize || 16) : (st.fontSize || 16);
    var lineHeight = n ? (n.lineHeight || 1.35) : (st.lineHeight || 1.35);
    var opacity = n ? (n.opacity == null ? 1 : n.opacity) : (st.opacity == null ? 1 : st.opacity);
    var color = n ? (n.color || '#e6edf3') : (st.color || '#e6edf3');

    if (isDefault) {
      host.appendChild(plainHint('Rules for the next text block.'));
    } else {
      host.appendChild(plainHint('Double-click text to write. Enter saves, Shift+Enter adds a line.'));
    }

    host.appendChild(textSizeRow(size, function (v) {
      updateTextStyle({ fontSize: v }, n, isDefault);
    }));

    var colorGroup = document.createElement('div');
    colorGroup.className = 'shape-group';
    var colorLabel = document.createElement('span');
    colorLabel.className = 'shape-label';
    colorLabel.textContent = 'Text color';
    colorGroup.appendChild(colorLabel);
    colorGroup.appendChild(shapeSwatches(color, function (c) {
      updateTextStyle({ color: c }, n, isDefault);
    }, SHAPE_COLORS.filter(function (c) { return c !== 'transparent'; })));
    host.appendChild(colorGroup);

    var styleRow = document.createElement('div');
    styleRow.className = 'shape-row';
    var underline = n ? n.textDecoration === 'underline' : !!st.underline;
    var strike = n ? n.textDecoration === 'line-through' : !!st.strike;
    [['B', bold, 'bold'], ['I', italic, 'italic'], ['U', underline, 'underline'],
     ['S', strike, 'strike']].forEach(function (it) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'ghost' + (it[1] ? ' is-on' : '');
      b.textContent = it[0];
      b.title = it[2];
      b.addEventListener('click', function () {
        var patch = {};
        if (it[2] === 'underline') patch.textDecoration = underline ? 'none' : 'underline';
        else if (it[2] === 'strike') patch.textDecoration = strike ? 'none' : 'line-through';
        else patch[it[2]] = !it[1];
        updateTextStyle(patch, n, isDefault);
      });
      styleRow.appendChild(b);
    });
    host.appendChild(styleRow);

    var family = n ? (n.fontFamily || 'Excalifont, sans-serif')
      : (st.fontFamily || 'Excalifont, sans-serif');
    host.appendChild(shapeOptionRow('Font', [
      ['Excalifont, sans-serif', 'Hand'],
      ['Helvetica, Arial, sans-serif', 'Normal'],
      ['Cascadia, monospace', 'Code']
    ], family, function (v) {
      updateTextStyle({ fontFamily: v }, n, isDefault);
    }));
    host.appendChild(shapeOptionRow('Align', [['left', 'Left'], ['center', 'Center'], ['right', 'Right']], align, function (v) {
      updateTextStyle({ align: v }, n, isDefault);
    }));
    host.appendChild(shapeRange('Line height', 1, 2, 0.05, lineHeight, '', function (v) {
      updateTextStyle({ lineHeight: v }, n, isDefault);
    }, function () { if (!isDefault) pushHistory(); }));
    host.appendChild(shapeRange('Opacity', 10, 100, 5, Math.round(opacity * 100), '%', function (v) {
      updateTextStyle({ opacity: v / 100 }, n, isDefault);
    }, function () { if (!isDefault) pushHistory(); }));
    host.appendChild(styleRow);
  }

  function renderPenStyle(host, d, isDefault) {
    var st = d || editor.penStyle;
    if (isDefault) {
      host.appendChild(plainHint('Rules for the next pen stroke.'));
    } else {
      host.appendChild(plainHint('Hand-drawn stroke. Pick color, width, and line style.'));
    }

    var colorGroup = document.createElement('div');
    colorGroup.className = 'shape-group';
    var colorLabel = document.createElement('span');
    colorLabel.className = 'shape-label';
    colorLabel.textContent = 'Pen color';
    colorGroup.appendChild(colorLabel);
    colorGroup.appendChild(shapeSwatches(st.color || '#e6edf3', function (c) {
      updatePenStyle({ color: c }, d, isDefault, false);
    }, SHAPE_COLORS.filter(function (c) { return c !== 'transparent'; })));
    host.appendChild(colorGroup);

    host.appendChild(shapeRange('Width', 1, 16, 0.5, st.width || 2, 'px', function (v) {
      updatePenStyle({ width: v }, d, isDefault, true);
    }, function () { if (!isDefault) pushHistory(); }));
    host.appendChild(shapeSelect('Style', SHAPE_STROKES.map(function (v) { return [v, v]; }), st.strokeStyle || 'solid', function (v) {
      updatePenStyle({ strokeStyle: v }, d, isDefault, false);
    }));
    host.appendChild(shapeRange('Opacity', 10, 100, 5, Math.round((st.opacity == null ? 1 : st.opacity) * 100), '%', function (v) {
      updatePenStyle({ opacity: v / 100 }, d, isDefault, true);
    }, function () { if (!isDefault) pushHistory(); }));
  }

  function shapeSelectionKey() {
    if (!isCanvas()) return 'view';
    if (editor.tool === 'text') return 'new:text';
    if (editor.tool === 'draw') return 'new:pen';
    var s = state.spec;
    if (s.selectedDrawing) return 'drawing:' + s.selectedDrawing;
    if (s.selectedEdge != null) return 'edge:' + s.selectedEdge;
    var ids = selectionIds();
    if (ids.length === 1) return 'node:' + ids[0];
    if (ids.length > 1) return 'multi:' + ids.join(',');
    return 'none';
  }

  /* Panel properti (bentuk, warna, teks) terbuka secara baku di layar lebar.
     Pilihan pengguna yang tersimpan selalu menang; tanpa preferensi, desktop
     = buka, ponsel = tutup supaya kanvas tidak tertutup.
     The properties panel defaults to open on wide screens; a stored choice
     always wins, and phones start closed to keep the canvas clear. */
  var inspectorPref = (function () {
    try { return localStorage.getItem('ruang.inspector.v1'); } catch (err) { return null; }
  })();
  var inspectorOpen = inspectorPref
    ? inspectorPref === 'open'
    : (window.innerWidth >= 900);

  function setInspector(open) {
    inspectorOpen = !!open;
    try { localStorage.setItem('ruang.inspector.v1', inspectorOpen ? 'open' : 'closed'); } catch (err) {}
    syncShapePanel();
  }

  function syncInspectorToggle() {
    var btn = document.getElementById('inspectorToggle');
    if (!btn) return;
    btn.classList.toggle('is-on', !!inspectorOpen);
    btn.setAttribute('aria-pressed', inspectorOpen ? 'true' : 'false');
    var sp = document.getElementById('shapePanel');
    var shown = !!(sp && !sp.hidden);
    btn.title = shown
      ? 'Hide properties panel (Alt+/)'
      : 'Show properties panel — shape, colour, text (Alt+/)';
  }

  function syncShapePanel() {
    syncShapePanelInner();
    syncInspectorToggle();
    syncStageInsets();
  }

  function syncShapePanelInner() {
    var panel = document.getElementById('shapePanel');
    var body = document.getElementById('shapePanelBody');
    var title = document.getElementById('shapePanelTitle');
    if (!panel || !body || !title) return;

    /* Rebuilding the inspector must not throw away the user's scroll position.
       A color tap or a range nudge re-renders the same selection, so keep the
       scroll offset unless the selected object actually changed. */
    var key = shapeSelectionKey();
    var same = panel.getAttribute('data-sel-key') === key;
    var keepBody = same ? body.scrollTop : 0;
    var keepPanel = same ? panel.scrollTop : 0;
    panel.setAttribute('data-sel-key', key);
    requestAnimationFrame(function () {
      body.scrollTop = keepBody;
      panel.scrollTop = keepPanel;
    });

    var info = (isCanvas() && !document.body.classList.contains('view-mode')) ? selectionInfo() : null;

    /* While a connection is pending, keep the canvas clear so the target is
       visible and tappable on a phone. */
    if (editor.from) {
      panel.hidden = true;
      body.innerHTML = '';
      return;
    }

    /* While wiring on a phone the inspector would sit on the nodes the user
       is trying to connect, so it steps aside. On a desktop it stays: the
       arrow/line colours are edited right there. */
    if ((editor.tool === 'arrow' || editor.tool === 'line') && window.innerWidth < 900) {
      panel.hidden = true;
      body.innerHTML = '';
      return;
    }

    if (!inspectorOpen) {
      panel.hidden = true;
      body.innerHTML = '';
      return;
    }

    if (isCanvas() && !document.body.classList.contains('view-mode') &&
        (editor.tool === 'text' || editor.tool === 'draw')) {
      panel.hidden = false;
      body.innerHTML = '';
      if (editor.tool === 'text') {
        title.textContent = 'Text · new';
        renderTextStyle(body, null, true);
      } else {
        title.textContent = 'Pen · new';
        renderPenStyle(body, null, true);
      }
      return;
    }

    if (!info || info.kind === 'multi') {
      /* Tool arrow/line tanpa seleksi: tetap tampilkan gaya yang akan dipakai
         supaya warna bisa diubah sebelum menggambar. */
      if (isCanvas() && !document.body.classList.contains('view-mode') &&
          (editor.tool === 'arrow' || editor.tool === 'line') && window.innerWidth >= 900) {
        panel.hidden = false;
        body.innerHTML = '';
        title.textContent = (editor.tool === 'arrow' ? 'Arrow' : 'Line') + ' · new';
        renderEdgeDefaults(body);
        return;
      }
      panel.hidden = true;
      body.innerHTML = '';
      return;
    }
    panel.hidden = false;
    body.innerHTML = '';

    if (info.kind === 'node') {
      var n = info.node;
      title.textContent = (n.shape || 'box') + ' · ' + (n.id || 'node');
      if (n.shape === 'module') {
        title.textContent = (n.module || 'module') + ' card';
        body.appendChild(textField('Label', n.label || '', function (v) { n.label = v; }));
        body.appendChild(shapeButtonRow([
          [n.expanded ? 'Collapse' : 'Expand', 'Toggle module size', function () { toggleModuleBlock(info.id); }],
          ['Delete', 'Delete module block', deleteSelected],
          ['Front', 'Bring to front', function () { moveNodeLayer(info.id, 'front'); }],
          ['Back', 'Send to back', function () { moveNodeLayer(info.id, 'back'); }]
        ]));
        return;
      }

      if (n.isText) {
        title.textContent = 'Text · ' + (n.id || 'node');
        renderTextStyle(body, n, false);
        body.appendChild(shapeButtonRow([
          ['Front', 'Bring to front', function () { moveNodeLayer(info.id, 'front'); }],
          ['Back', 'Send to back', function () { moveNodeLayer(info.id, 'back'); }],
          ['Delete', 'Delete text', deleteSelected]
        ]));
        return;
      }

      body.appendChild(shapeButtonRow([
        ['Connect', 'Connect this node to another node', function () { startConnect(info.id); }]
      ]));

      var stroke = document.createElement('div');
      stroke.className = 'shape-group';
      var sl = document.createElement('span');
      sl.className = 'shape-label';
      sl.textContent = 'Stroke';
      stroke.appendChild(sl);
      stroke.appendChild(shapeSwatches(n.color || 'blue', function (c) {
        applyNodePatch({ color: c });
      }));
      body.appendChild(stroke);

      var fill = document.createElement('div');
      fill.className = 'shape-group';
      var fl = document.createElement('span');
      fl.className = 'shape-label';
      fl.textContent = 'Fill';
      fill.appendChild(fl);
      fill.appendChild(shapeSwatches(n.fill || 'transparent', function (c) {
        applyNodePatch({ fill: c });
      }));
      body.appendChild(fill);

      if ((n.fill || 'transparent') !== 'transparent') {
        body.appendChild(shapeOptionRow('Fill style', SHAPE_FILLS, n.fillStyle || 'hachure', function (v) {
          applyNodePatch({ fillStyle: v });
        }));
      }

      body.appendChild(shapeRange('Width', 1, 8, 0.5, n.strokeWidth || 1.5, 'px', function (v) {
        liveNodePatch({ strokeWidth: v });
      }, function () { pushHistory(); }));
      body.appendChild(shapeSelect('Stroke style', SHAPE_STROKES.map(function (v) { return [v, v]; }), n.strokeStyle || 'solid', function (v) {
        applyNodePatch({ strokeStyle: v });
      }));
      body.appendChild(shapeSelect('Sloppiness', SHAPE_SLOP, n.sloppiness || 'architect', function (v) {
        applyNodePatch({ sloppiness: v });
      }));
      body.appendChild(shapeSelect('Edges', SHAPE_EDGES, n.edge || 'sharp', function (v) {
        applyNodePatch({ edge: v });
      }));

      body.appendChild(shapeRange('Opacity', 10, 100, 5, Math.round((n.opacity == null ? 1 : n.opacity) * 100), '%', function (v) {
        liveNodePatch({ opacity: v / 100 });
      }, function () { pushHistory(); }));

      body.appendChild(shapeButtonRow([
        ['Front', 'Bring to front', function () { moveNodeLayer(info.id, 'front'); }],
        ['Back', 'Send to back', function () { moveNodeLayer(info.id, 'back'); }],
        ['Delete', 'Delete node', deleteSelected]
      ]));

      if (n.logo || (n.logos && n.logos.length)) {
        body.appendChild(shapeButtonRow([
          ['Remove logo', 'Remove logo', function () {
            applyNodePatch({ logo: null, logos: [] });
          }]
        ]));
      }
      return;
    }

    if (info.kind === 'drawing') {
      title.textContent = 'Pen · ' + (info.drawing.id || 'drawing');
      renderPenStyle(body, info.drawing, false);
      body.appendChild(shapeButtonRow([
        ['Delete', 'Delete stroke', deleteSelected]
      ]));
      return;
    }

    var e = info.edge;
    title.textContent = e.points ? 'Arrow · ' + info.index : 'Edge · ' + info.index;
    var es = document.createElement('div');
    es.className = 'shape-group';
    var esl = document.createElement('span');
    esl.className = 'shape-label';
    esl.textContent = 'Stroke';
    es.appendChild(esl);
    es.appendChild(shapeSwatches(e.color || 'blue', function (c) {
      applyEdgePatch({ color: c });
    }));
    body.appendChild(es);

    body.appendChild(shapeRange('Width', 1, 8, 0.5, e.width || 2, 'px', function (v) {
      liveEdgePatch({ width: v });
    }, function () { pushHistory(); }));
    body.appendChild(shapeSelect('Style', SHAPE_STROKES.map(function (v) { return [v, v]; }), e.strokeStyle || e.cable || 'solid', function (v) {
      applyEdgePatch({ strokeStyle: v, cable: v });
    }));
    body.appendChild(shapeRange('Opacity', 10, 100, 5, Math.round((e.opacity == null ? 1 : e.opacity) * 100), '%', function (v) {
      liveEdgePatch({ opacity: v / 100 });
    }, function () { pushHistory(); }));

    var arrow = document.createElement('div');
    arrow.className = 'shape-group';
    var al = document.createElement('span');
    al.className = 'shape-label';
    al.textContent = 'Arrow heads';
    arrow.appendChild(al);
    var checks = document.createElement('div');
    checks.className = 'shape-row';
    checks.appendChild(shapeCheck('Start', e.arrowStart, function (v) { applyEdgePatch({ arrowStart: v }); }));
    checks.appendChild(shapeCheck('End', e.arrowEnd === true, function (v) { applyEdgePatch({ arrowEnd: v }); }));
    arrow.appendChild(checks);
    arrow.appendChild(shapeSelect('Type', ARROW_TYPES, e.arrowType || 'arrow', function (v) {
      applyEdgePatch({ arrowType: v });
    }));
    arrow.appendChild(shapeCheck('Curved', e.curved, function (v) { applyEdgePatch({ curved: v }); }));
    body.appendChild(arrow);

    body.appendChild(shapeButtonRow([
      ['Front', 'Bring to front', function () { moveEdgeLayer(info.index, 'front'); }],
      ['Back', 'Send to back', function () { moveEdgeLayer(info.index, 'back'); }]
    ]));
  }

  /* Gaya untuk anak panah/garis berikutnya. Disimpan di spec supaya ikut
     tersimpan, ikut ke blok draw, dan dipakai saat edge dibuat.
     Defaults for the next arrow/line: stored on the spec so they persist,
     land in the draw block, and apply when an edge is created. */
  function edgeStyle() {
    var s = state.spec;
    if (!s.edgeStyle || typeof s.edgeStyle !== 'object') s.edgeStyle = {};
    return s.edgeStyle;
  }

  function renderEdgeDefaults(host) {
    var es = edgeStyle();

    var stroke = document.createElement('div');
    stroke.className = 'shape-group';
    var sl = document.createElement('span');
    sl.className = 'shape-label';
    sl.textContent = 'Stroke';
    stroke.appendChild(sl);
    stroke.appendChild(shapeSwatches(es.color || 'blue', function (c) {
      es.color = c;
      queueSave();
    }));
    host.appendChild(stroke);

    host.appendChild(shapeRange('Width', 1, 8, 0.5, es.width || 2, 'px', function (v) {
      es.width = v;
      queueSave();
    }, function () { pushHistory(); }));

    host.appendChild(shapeSelect('Style',
      SHAPE_STROKES.map(function (v) { return [v, v]; }),
      es.strokeStyle || state.spec.cable || 'solid', function (v) {
        es.strokeStyle = v;
        state.spec.cable = v;
        syncControls();
        render();
      }));

    host.appendChild(shapeSelect('Arrow heads', ARROW_TYPES, es.arrowType || 'arrow', function (v) {
      es.arrowType = v;
      queueSave();
    }));

    var note = document.createElement('p');
    note.className = 'hint';
    note.textContent = 'Applies to the next arrow or line you draw.';
    host.appendChild(note);
  }

  function syncEditor() {
    var bar = document.getElementById('editorBar');
    var status = document.getElementById('stageStatus');
    var view = document.getElementById('viewBar');
    var canvas = isCanvas();
    document.body.classList.toggle('canvas-mode', canvas);
    if (bar) bar.style.display = canvas ? '' : 'none';
    if (status) status.style.display = canvas ? '' : 'none';
    if (view) view.style.display = canvas ? '' : 'none';
    if (!canvas) closePanels();
    var panel = document.getElementById('editorPanel');
    if (panel) panel.style.display = canvas ? '' : 'none';
    var ph = document.getElementById('propertiesHint');
    if (ph) ph.style.display = canvas ? 'none' : '';
    updateStatus();
    if (!canvas) return;

    document.getElementById('editorMode').textContent = editor.tool;

    var hints = {
      select: 'Drag to move. Shift-click or marquee to multi-select. Handles resize; arrows nudge.',
      box: 'Drag on the canvas to draw a transparent rectangle.',
      diamond: 'Drag on the canvas to draw a transparent diamond.',
      circle: 'Drag on the canvas to draw a transparent ellipse.',
      text: 'Drag to place text. Enter or double-click edits it.',
      table: 'Drag on the canvas to size a table. Handles resize it; + Row / − Row add rows.',
      arrow: 'Drag from a node to a node to connect, or drag empty space for an editable arrow.',
      line: 'Drag to draw a line. Select it, then drag its point handles.',
      draw: 'Drag to sketch a freehand stroke with the pen.',
      eraser: 'Click or drag over an object to erase it.',
      laser: 'Drag to leave a temporary laser trail.',
      pan: 'Drag to pan. Wheel pans; Ctrl/⌘ + wheel zooms (10%–100%).'
    };
    document.getElementById('editorHint').textContent = hints[editor.tool] || hints.select;

    renderNodeInspector();
    renderEdgeInspector();
    syncShapePanel();
    syncChartDataPanel();
    updateHistoryButtons();
  }

  function nodeVisualBounds(n) {
    var w = n.w || 160;
    var h = n.h || 60;
    var x = n.x || 0;
    var y = n.y || 0;
    var minX = x, minY = y, maxX = x + w, maxY = y + h;
    var ids = (n.logos && n.logos.length) ? n.logos : (n.logo ? [n.logo] : []);
    if (ids.length) {
      var size = Math.max(10, Math.min(w, h) * (ids.length > 1 ? 0.24 : 0.34));
      var total = ids.length * size + (ids.length - 1) * 2;
      var left = x + (w - total) / 2;
      var top = y + (h - size) / 2;
      minX = Math.min(minX, left);
      minY = Math.min(minY, top);
      maxX = Math.max(maxX, left + total);
      maxY = Math.max(maxY, top + size);
    }
    return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
  }

  function nodeAtPoint(x, y) {
    var nodes = state.spec.nodes || {};
    var ids = Object.keys(nodes);
    for (var i = ids.length - 1; i >= 0; i--) {
      var n = nodes[ids[i]];
      if (!n) continue;
      var b = nodeVisualBounds(n);
      var nx = b.x;
      var ny = b.y;
      var w = b.w;
      var h = b.h;
      if (n.shape === 'circle') {
        var rx = w / 2;
        var ry = h / 2;
        var dx = (x - (nx + rx)) / Math.max(1, rx);
        var dy = (y - (ny + ry)) / Math.max(1, ry);
        if (dx * dx + dy * dy <= 1) return ids[i];
      } else if (n.shape === 'diamond') {
        var qx = Math.abs(x - (nx + w / 2)) / Math.max(1, w / 2);
        var qy = Math.abs(y - (ny + h / 2)) / Math.max(1, h / 2);
        if (qx + qy <= 1) return ids[i];
      } else if (x >= nx && x <= nx + w && y >= ny && y <= ny + h) {
        return ids[i];
      }
    }
    return null;
  }

  function closestEdgePoint(el) {
    while (el && el !== stage) {
      if (el.getAttribute && el.getAttribute('data-edge-point') != null) return el;
      el = el.parentNode;
    }
    return null;
  }

  function closestEdgeMid(el) {
    while (el && el !== stage) {
      if (el.getAttribute && el.getAttribute('data-edge-mid') != null) return el;
      el = el.parentNode;
    }
    return null;
  }

  function edgeHeadData(points) {
    if (!points || points.length < 2) return '';
    var p = points[points.length - 1];
    var q = points[points.length - 2];
    var ang = Math.atan2(p[1] - q[1], p[0] - q[0]);
    var len = 9;
    var spread = 4.5;
    var x1 = p[0] - len * Math.cos(ang) + spread * Math.sin(ang);
    var y1 = p[1] - len * Math.sin(ang) - spread * Math.cos(ang);
    var x2 = p[0] - len * Math.cos(ang) - spread * Math.sin(ang);
    var y2 = p[1] - len * Math.sin(ang) + spread * Math.cos(ang);
    return 'M ' + p[0] + ' ' + p[1] + ' L ' + x1 + ' ' + y1 + ' L ' + x2 + ' ' + y2 + ' Z';
  }

  function edgePathData(points, curved) {
    if (!points || points.length < 2) return '';
    if (curved && points.length > 2) {
      var d = 'M ' + points[0][0] + ' ' + points[0][1];
      for (var i = 0; i < points.length - 1; i++) {
        var p0 = points[i - 1] || points[i];
        var p1 = points[i];
        var p2 = points[i + 1];
        var p3 = points[i + 2] || p2;
        var c1x = p1[0] + (p2[0] - p0[0]) / 6;
        var c1y = p1[1] + (p2[1] - p0[1]) / 6;
        var c2x = p2[0] - (p3[0] - p1[0]) / 6;
        var c2y = p2[1] - (p3[1] - p1[1]) / 6;
        d += ' C ' + c1x + ' ' + c1y + ', ' + c2x + ' ' + c2y + ', ' + p2[0] + ' ' + p2[1];
      }
      return d;
    }
    var d = 'M ' + points[0][0] + ' ' + points[0][1];
    for (var i = 1; i < points.length; i++) d += ' L ' + points[i][0] + ' ' + points[i][1];
    return d;
  }

  function finishLineChain() {
    var chain = editor.lineChain;
    editor.lineChain = null;
    if (!chain || chain.length < 2) return;
    var les = edgeStyle();
    state.spec.edges = state.spec.edges || [];
    state.spec.edges.push({
      points: chain.map(function (pt) { return [pt[0], pt[1]]; }),
      cable: state.spec.cable || 'solid',
      motion: 'none',
      arrowStart: false,
      arrowEnd: true,
      arrowType: les.arrowType || 'arrow',
      strokeStyle: les.strokeStyle || state.spec.cable || 'solid',
      curved: chain.length === 2,
      color: les.color || '#e6edf3',
      width: les.width || 2
    });
    state.spec.selected = null;
    state.spec.selectedEdge = state.spec.edges.length - 1;
    state.spec.selectedEdges = [state.spec.edges.length - 1];
    state.spec.selectedDrawing = null;
    touchSpec();
    syncControls();
    syncEditor();
    render();
    if (!editor.keepTool) setTool('select');
  }

  function updateEdgePath(i) {
    var e = state.spec.edges && state.spec.edges[i];
    if (!e || !e.points) return;
    var d = edgePathData(e.points, e.curved);
    var main = stage.querySelector('.alur-canvas-edge[data-edge="' + i + '"]');
    if (!main) return;
    var group = main.parentNode;
    if (group && group.querySelectorAll) {
      Array.prototype.forEach.call(group.querySelectorAll('path'), function (p) { p.setAttribute('d', d); });
    }
    main.setAttribute('d', d);
    var head = stage.querySelector('.alur-edge-head[data-edge="' + i + '"]');
    if (head) head.setAttribute('d', edgeHeadData(e.points));
    e.points.forEach(function (pt, pi) {
      var h = stage.querySelector('[data-edge="' + i + '"][data-edge-point="' + pi + '"]');
      if (h) { h.setAttribute('cx', pt[0]); h.setAttribute('cy', pt[1]); }
    });
  }

  function sceneToClient(x, y) {
    var svg = stage.querySelector('svg');
    if (!svg) return { x: x, y: y };
    var pt = svg.createSVGPoint();
    pt.x = x; pt.y = y;
    var m = svg.getScreenCTM();
    if (!m) return { x: x, y: y };
    return pt.matrixTransform(m);
  }

  function positionInlineText() {
    if (!editor || !editor.textEdit) return;
    var area = document.getElementById('inlineText');
    if (!area) return;
    var id = editor.textEdit.id;
    var n = state.spec.nodes && state.spec.nodes[id];
    if (!n) return;
    var label = stage.querySelector('.alur-canvas-node[data-node-id="' + id + '"] .alur-node-label');
    var rect = null;
    if (label && label.getBoundingClientRect) rect = label.getBoundingClientRect();
    if (!rect || (!rect.width && !rect.height)) {
      var c = sceneToClient(n.x || 0, n.y || 0);
      var zoom = state.spec.zoom || 1;
      rect = { left: c.x, top: c.y, width: Math.max(80, (n.w || 160) * zoom), height: Math.max(26, (n.h || 40) * zoom) };
    }
    var ctm = label && label.getScreenCTM ? label.getScreenCTM() : null;
    var scale = ctm ? Math.sqrt(ctm.a * ctm.a + ctm.b * ctm.b) : (state.spec.zoom || 1);
    var fs = Math.max(9, (n.fontSize || 16) * scale);
    var align = n.textAlign || ((n.logos && n.logos.length) || n.logo || n.shape === 'circle' ? 'center' : 'left');
    area.style.left = rect.left + 'px';
    area.style.top = rect.top + 'px';
    area.style.width = Math.max(48, rect.width + 4) + 'px';
    area.style.height = Math.max(20, rect.height + 2) + 'px';
    area.style.fontFamily = 'Excalifont, sans-serif';
    area.style.fontSize = fs + 'px';
    area.style.fontWeight = n.fontWeight || (n.bold ? 700 : 400);
    area.style.fontStyle = n.fontStyle || (n.italic ? 'italic' : 'normal');
    area.style.color = AlurKit.color(n.color || '#e6edf3');
    area.style.textAlign = align === 'center' ? 'center' : (align === 'right' ? 'right' : 'left');
    area.style.lineHeight = String(fs * Math.max(1, n.lineHeight || 1.35)) + 'px';
    area.style.padding = '0';
    area.style.border = '0';
    area.style.margin = '0';
    area.style.boxSizing = 'border-box';
    area.style.minWidth = '0';
    area.style.minHeight = '0';
  }

  function startTextEdit(id) {
    var n = state.spec.nodes && state.spec.nodes[id];
    if (!n) return;
    var area = document.getElementById('inlineText');
    if (!area) {
      area = document.createElement('textarea');
      area.id = 'inlineText';
      area.spellcheck = false;
      document.body.appendChild(area);
    }
    area.value = n.label || '';
    area.dataset.nodeId = id;
    editor.textEdit = { id: id, before: n.label || '' };
    positionInlineText();
    area.style.display = 'block';
    area.focus();
    area.select();
  }

  function commitTextEdit() {
    var area = document.getElementById('inlineText');
    if (!area || !editor.textEdit) return;
    var id = editor.textEdit.id;
    var n = state.spec.nodes && state.spec.nodes[id];
    if (!n) { area.style.display = 'none'; editor.textEdit = null; return; }
    var before = editor.textEdit.before;
    var value = area.value;
    area.style.display = 'none';
    editor.textEdit = null;
    /* Excalidraw: empty text is no text. */
    if (value.trim() === '' && n.isText) {
      pushHistory();
      delete state.spec.nodes[id];
      if (state.spec.selected === id) state.spec.selected = null;
      state.spec.edges = (state.spec.edges || []).filter(function (e) {
        return e.from !== id && e.to !== id;
      });
      touchSpec();
      syncControls();
      syncEditor();
      render();
      return;
    }
    if (value !== before) {
      pushHistory();
      n.label = value;
      if (n.isText) {
        var fs = n.fontSize || 16;
        var lh = Math.max(1, n.lineHeight || 1.35);
        var lines = value.split('\n').length;
        n.h = Math.max(24, Math.round(lines * fs * lh + 8));
      }
      touchSpec();
      syncControls();
      syncEditor();
      render();
    }
  }

  function cancelTextEdit() {
    var area = document.getElementById('inlineText');
    if (area) area.style.display = 'none';
    editor.textEdit = null;
  }

  function eraseAt(clientX, clientY) {
    var changed = false;
    var els = document.elementsFromPoint ? document.elementsFromPoint(clientX, clientY) : [];
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      var nodeEl = closestNode(el);
      if (!nodeEl && el.getAttribute && el.getAttribute('data-node-id')) {
        nodeEl = el;
      }
      if (nodeEl) {
        var id = nodeEl.getAttribute('data-node-id');
        if (!state.spec.nodes || !state.spec.nodes[id]) continue;
        delete state.spec.nodes[id];
        state.spec.edges = (state.spec.edges || []).filter(function (e) {
          return e.from !== id && e.to !== id;
        });
        state.spec.selected = null;
        state.spec.selectedEdge = null;
        state.spec.selectedEdges = [];
        state.spec.selectedDrawing = null;
        changed = true;
        break;
      }
      var edgeEl = closestEdge(el);
      if (edgeEl) {
        var ei = parseInt(edgeEl.getAttribute('data-edge'), 10);
        state.spec.edges.splice(ei, 1);
        state.spec.selectedEdge = null;
        state.spec.selectedEdges = [];
        changed = true;
        break;
      }
      var drawEl = closestDrawing(el);
      if (drawEl) {
        var di = drawEl.getAttribute('data-drawing');
        state.spec.drawings = (state.spec.drawings || []).filter(function (d) { return d.id !== di; });
        state.spec.selectedDrawing = null;
        changed = true;
        break;
      }
    }
    if (changed) {
      touchSpec();
      syncControls();
      syncEditor();
      render();
    }
  }

  function makeCreatePreview(shape) {
    var attrs = {
      fill: 'rgba(88,166,255,0.10)', stroke: '#58a6ff', 'stroke-width': 1.4,
      'stroke-dasharray': '4 3'
    };
    if (shape === 'circle') return AlurKit.el('ellipse', Object.assign({ cx: 0, cy: 0, rx: 0, ry: 0, class: 'alur-preview' }, attrs), overlayLayer());
    if (shape === 'diamond') return AlurKit.path(overlayLayer(), '', 'alur-preview', attrs);
    return AlurKit.rect(overlayLayer(), 0, 0, 0, 0, 'alur-preview', attrs);
  }

  function setCreatePreview(el, shape, x, y, w, h) {
    if (!el) return;
    if (shape === 'circle') {
      el.setAttribute('cx', x + w / 2);
      el.setAttribute('cy', y + h / 2);
      el.setAttribute('rx', w / 2);
      el.setAttribute('ry', h / 2);
    } else if (shape === 'diamond') {
      el.setAttribute('d', 'M ' + (x + w / 2) + ' ' + y +
        ' L ' + (x + w) + ' ' + (y + h / 2) +
        ' L ' + (x + w / 2) + ' ' + (y + h) +
        ' L ' + x + ' ' + (y + h / 2) + ' Z');
    } else {
      el.setAttribute('x', x);
      el.setAttribute('y', y);
      el.setAttribute('width', w);
      el.setAttribute('height', h);
    }
  }

  stage.addEventListener('pointerdown', function (ev) {
    if (!isCanvas()) return;
    /* Fokus yang nyangkut di input (mis. sel tabel) menelan tombol Delete.
       Klik kanvas harus memindahkan fokus, sama seperti Excalidraw. */
    var ae = document.activeElement;
    if (ae && ae !== document.body && /^(input|textarea|select)$/i.test(ae.tagName || '') &&
        !editor.textEdit && !ev.target.closest('td[data-table-node], th[data-table-node], [data-table-action]')) {
      try { ae.blur(); } catch (err) {}
    }
    if (ev.target.closest && ev.target.closest('td[data-table-node], th[data-table-node], [data-table-action]')) return;
    var svg = stage.querySelector('svg');
    if (!svg) return;
    var p = svgPoint(svg, ev);

    /* Chart marks keep their own hover/tooltip; dragging starts elsewhere. */
    if (editor.tool === 'select' && ev.target.closest &&
        ev.target.closest('.alur-module-embed[data-module="chart"] [data-tip]')) {
      return;
    }

    if (editor.tool === 'pan' || spaceDown || ev.button === 1) {
      pushHistory();
      editor.drag = {
        type: 'pan',
        clientX: ev.clientX, clientY: ev.clientY,
        panX: state.spec.panX || 0, panY: state.spec.panY || 0
      };
      ev.preventDefault();
      return;
    }

    if (editor.tool === 'draw') {
      pushHistory();
      var preview = AlurKit.path(overlayLayer(), '', 'alur-preview-path', {
        fill: 'none',
        stroke: AlurKit.color(editor.penStyle.color),
        'stroke-width': editor.penStyle.width,
        'stroke-dasharray': editor.penStyle.strokeStyle === 'dashed' ? '7 5' :
          (editor.penStyle.strokeStyle === 'dotted' ? '2 4' : null),
        opacity: editor.penStyle.opacity,
        'stroke-linecap': 'round', 'stroke-linejoin': 'round'
      });
      editor.drag = { type: 'draw', points: [[p.x, p.y]], preview: preview };
      ev.preventDefault();
      return;
    }

    if (editor.tool === 'eraser') {
      pushHistory();
      editor.drag = { type: 'erase' };
      eraseAt(ev.clientX, ev.clientY);
      ev.preventDefault();
      return;
    }

    if (editor.tool === 'laser') {
      var laser = AlurKit.path(overlayLayer(), '', 'alur-laser', {
        fill: 'none', stroke: '#ff5a5a', 'stroke-width': 2.2,
        'stroke-linecap': 'round', 'stroke-linejoin': 'round'
      });
      editor.drag = { type: 'laser', points: [[p.x, p.y]], preview: laser };
      ev.preventDefault();
      return;
    }

    if (editor.tool === 'arrow') {
      var arrowNode = closestNode(ev.target);
      var arrowId = arrowNode ? arrowNode.getAttribute('data-node-id') : nodeAtPoint(p.x, p.y);
      /* Arrow is a drag tool, like Excalidraw: press, drag, release. A simple
         tap on a node arms it for a second tap (mobile-friendly), while a drag
         from another node starts a fresh arrow instead of hijacking the armed
         source. The actual state change happens in endDrag so a tap never
         leaves a half-finished connection behind. */
      closeCtx();
      var arrowPreview = AlurKit.path(overlayLayer(), '', 'alur-preview-path', {
        fill: 'none', stroke: '#58a6ff', 'stroke-width': 2,
        'stroke-linecap': 'round', 'stroke-linejoin': 'round'
      });
      editor.drag = {
        type: 'arrow', points: [[p.x, p.y], [p.x, p.y]],
        x0: p.x, y0: p.y, x1: p.x, y1: p.y,
        downNode: arrowId && state.spec.nodes[arrowId] ? arrowId : null,
        armedFrom: editor.from || null,
        moved: false, preview: arrowPreview
      };
      ev.preventDefault();
      return;
    }

    if (editor.tool === 'line' || editor.tool === 'arrow') {
      pushHistory();
      var linePreview = AlurKit.path(overlayLayer(), '', 'alur-preview-path', {
        fill: 'none', stroke: '#58a6ff', 'stroke-width': 2,
        'stroke-dasharray': '4 3', 'stroke-linecap': 'round'
      });
      editor.drag = {
        type: 'line', x0: p.x, y0: p.y, x1: p.x, y1: p.y,
        moved: false, preview: linePreview,
        chain: editor.lineChain ? editor.lineChain.slice() : null,
        tool: editor.tool
      };
      ev.preventDefault();
      return;
    }

    if (editor.tool === 'box' || editor.tool === 'diamond' || editor.tool === 'circle' || editor.tool === 'text' || editor.tool === 'table') {
      pushHistory();
      var shape = editor.tool === 'round' ? 'pill' : editor.tool;
      var previewShape = makeCreatePreview(shape);
      editor.drag = {
        type: 'create', shape: shape,
        x0: p.x, y0: p.y, x1: p.x, y1: p.y,
        moved: false, preview: previewShape
      };
      ev.preventDefault();
      return;
    }

    var edgeMidEl = closestEdgeMid(ev.target);
    if (edgeMidEl) {
      var midIdx = parseInt(edgeMidEl.getAttribute('data-edge-mid'), 10);
      var midEdge = state.spec.edges && state.spec.edges[midIdx];
      if (midEdge && midEdge.points && midEdge.points.length >= 2) {
        pushHistory();
        var pa = midEdge.points[0];
        var pb = midEdge.points[midEdge.points.length - 1];
        var bend = [(pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2];
        midEdge.points.splice(1, 0, bend);
        state.spec.selected = null;
        state.spec.selectedDrawing = null;
        state.spec.selectedEdge = midIdx;
        state.spec.selectedEdges = [midIdx];
        editor.drag = {
          type: 'edge-point', edge: midIdx, index: 1,
          px: p.x, py: p.y,
          points: midEdge.points.map(function (pt) { return pt.slice(); })
        };
        touchSpec();
        syncControls();
        syncEditor();
        render();
        ev.preventDefault();
        return;
      }
    }

    var edgePoint = closestEdgePoint(ev.target);
    if (edgePoint) {
      var epi = parseInt(edgePoint.getAttribute('data-edge'), 10);
      var epiIndex = parseInt(edgePoint.getAttribute('data-edge-point'), 10);
      var epEdge = state.spec.edges && state.spec.edges[epi];
      if (!epEdge || !epEdge.points) return;
      pushHistory();
      editor.drag = {
        type: 'edge-point', edge: epi, index: epiIndex,
        px: p.x, py: p.y, points: epEdge.points.map(function (pt) { return pt.slice(); })
      };
      ev.preventDefault();
      return;
    }

    var handle = closestHandle(ev.target);
    if (handle) {
      var hid = handle.getAttribute('data-node-id');
      var hn = state.spec.nodes[hid];
      if (!hn) return;
      pushHistory();
      editor.drag = {
        type: 'resize', id: hid, handle: handle.getAttribute('data-handle'),
        x0: hn.x || 0, y0: hn.y || 0, w0: hn.w || 160, h0: hn.h || 60,
        px: p.x, py: p.y
      };
      ev.preventDefault();
      return;
    }

    var moduleDelete = closestModuleDelete(ev.target);
    if (moduleDelete) {
      var delId = moduleDelete.getAttribute('data-module-delete');
      if (state.spec.nodes && state.spec.nodes[delId]) {
        pushHistory();
        delete state.spec.nodes[delId];
        state.spec.selected = null;
        state.spec.selectedEdge = null;
        state.spec.selectedEdges = [];
        state.spec.selectedDrawing = null;
        touchSpec();
        syncControls();
        render();
        ev.preventDefault();
        return;
      }
    }

    var nodeEl = closestNode(ev.target);
    var nid = nodeEl ? nodeEl.getAttribute('data-node-id') : null;
    /* Hit test on the scene, not on the DOM target: a logo image, a chart
       embed or any other decoration inside a node must not steal the grab. */
    if (!nid) {
      var hitId = nodeAtPoint(p.x, p.y);
      if (hitId) {
        nid = hitId;
        nodeEl = stage.querySelector('[data-node-id="' + hitId + '"]');
      }
    }
    if (nid) {
      var n = state.spec.nodes[nid];
      if (!n) return;
      var additive = ev.shiftKey || ev.metaKey || ev.ctrlKey;
      var ids = selectionIds();
      var wasSelected = ids.indexOf(nid) >= 0;
      if (!wasSelected) {
        selectNode(nid, additive);
        ids = selectionIds();
      }
      pushHistory();
      var items = ids.map(function (id) {
        var node = state.spec.nodes[id];
        var el = stage.querySelector('[data-node-id="' + id + '"]');
        if (el) el.classList.add('is-dragging');
        return { id: id, x: node.x || 0, y: node.y || 0, el: el };
      });
      editor.drag = {
        type: 'move', items: items,
        startX: p.x, startY: p.y,
        moved: false, additive: additive,
        collapse: wasSelected && ids.length > 1 && !additive ? nid : null,
        toggle: additive && wasSelected ? nid : null
      };
      ev.preventDefault();
      return;
    }

    var edgeEl = closestEdge(ev.target);
    if (edgeEl) {
      var ei = parseInt(edgeEl.getAttribute('data-edge'), 10);
      if (state.spec.selectedEdge !== ei) {
        state.spec.selectedEdge = ei;
        state.spec.selectedEdges = [ei];
        state.spec.selected = null;
        state.spec.selectedDrawing = null;
        touchSpec();
        syncEditor();
        render();
      }
      var ee2 = state.spec.edges && state.spec.edges[ei];
      if (ee2) {
        pushHistory();
        editor.drag = {
          type: 'move-edge',
          edge: ei,
          px: p.x, py: p.y,
          sx: p.x, sy: p.y,
          moved: false,
          points: ee2.points && ee2.points.length >= 2
            ? ee2.points.map(function (pt) { return [pt[0], pt[1]]; })
            : null
        };
      }
      ev.preventDefault();
      return;
    }

    var drawEl = closestDrawing(ev.target);
    if (drawEl) {
      selectDrawing(drawEl.getAttribute('data-drawing'));
      ev.preventDefault();
      return;
    }

    /* Excalidraw: pressing inside the common bounding box of the selection
       drags the selection, even when the press lands on empty canvas between
       the elements. Only a press outside the box starts a marquee. */
    var selBox = selectionBBox();
    if (selBox && !ev.shiftKey) {
      var spad = 6;
      if (p.x >= selBox.x - spad && p.x <= selBox.x + selBox.w + spad &&
          p.y >= selBox.y - spad && p.y <= selBox.y + selBox.h + spad) {
        pushHistory();
        var boxItems = selectionIds().map(function (id) {
          var node = state.spec.nodes[id];
          var el = stage.querySelector('[data-node-id="' + id + '"]');
          if (el) el.classList.add('is-dragging');
          return { id: id, x: node.x || 0, y: node.y || 0, el: el };
        });
        editor.drag = {
          type: 'move', items: boxItems,
          startX: p.x, startY: p.y,
          moved: false, additive: false, collapse: null, toggle: null
        };
        ev.preventDefault();
        return;
      }
    }

    var marquee = AlurKit.rect(overlayLayer(), p.x, p.y, 0, 0, 'alur-marquee', {
      fill: 'rgba(88,166,255,0.09)', stroke: '#58a6ff', 'stroke-dasharray': '5 4'
    });
    editor.drag = {
      type: 'marquee', x0: p.x, y0: p.y, x1: p.x, y1: p.y,
      base: ev.shiftKey ? selectionIds() : [], preview: marquee
    };
    ev.preventDefault();
  });

  stage.addEventListener('dblclick', function (ev) {
    if (!isCanvas()) return;
    var nodeEl = closestNode(ev.target);
    if (nodeEl) {
      var id = nodeEl.getAttribute('data-node-id');
      if (state.spec.nodes && state.spec.nodes[id]) {
        setSelection([id]);
        if (state.spec.nodes[id].shape === 'module') toggleModuleBlock(id);
        else startTextEdit(id);
        ev.preventDefault();
      }
      return;
    }
    var edgeEl = closestEdge(ev.target);
    if (!edgeEl) return;
    var ei = parseInt(edgeEl.getAttribute('data-edge'), 10);
    var e = state.spec.edges && state.spec.edges[ei];
    if (!e || !e.points || e.points.length < 2) return;
    var svg = stage.querySelector('svg');
    var p = svgPoint(svg, ev);
    var best = null;
    for (var i = 0; i < e.points.length - 1; i++) {
      var a = e.points[i];
      var b = e.points[i + 1];
      var vx = b[0] - a[0];
      var vy = b[1] - a[1];
      var len2 = vx * vx + vy * vy || 1;
      var t = Math.max(0, Math.min(1, ((p.x - a[0]) * vx + (p.y - a[1]) * vy) / len2));
      var qx = a[0] + vx * t;
      var qy = a[1] + vy * t;
      var dist = Math.abs(p.x - qx) + Math.abs(p.y - qy);
      if (!best || dist < best.dist) best = { dist: dist, at: i, point: [qx, qy] };
    }
    if (best) {
      pushHistory();
      e.points.splice(best.at + 1, 0, best.point);
      state.spec.selectedEdge = ei;
      touchSpec();
      syncControls();
      syncEditor();
      render();
      ev.preventDefault();
    }
  });

  function clearGuides() {
    var svg = stage.querySelector('svg');
    if (!svg) return;
    Array.prototype.forEach.call(svg.querySelectorAll('.alur-guide'), function (el) {
      if (el.parentNode) el.parentNode.removeChild(el);
    });
  }

  function updateNodeVisual(n, el) {
    if (!n || !el) return;
    var w = n.w || 160;
    var h = n.h || 60;
    var shape = n.shape || 'box';
    el.setAttribute('transform', 'translate(' + (n.x || 0) + ' ' + (n.y || 0) + ')');
    var inner = el.querySelector('.alur-node-inner');
    if (!inner) return;

    if (shape === 'circle') {
      var circles = inner.querySelectorAll('circle');
      if (circles[0]) {
        circles[0].setAttribute('cx', w / 2);
        circles[0].setAttribute('cy', h / 2);
        circles[0].setAttribute('r', Math.max(18, Math.min(w, h) / 2 - 2));
      }
      if (circles[1]) {
        circles[1].setAttribute('cx', w / 2);
        circles[1].setAttribute('cy', h / 2);
        circles[1].setAttribute('r', Math.max(18, Math.min(w, h) / 2 - 2));
      }
      var label = inner.querySelector('.alur-node-label');
      var sub = inner.querySelector('.alur-node-sub');
      if (label) label.setAttribute('y', h - 12);
      if (sub) sub.setAttribute('y', h + 4);
    } else if (shape === 'diamond') {
      var d = 'M ' + (w / 2) + ' 0 L ' + w + ' ' + (h / 2) +
        ' L ' + (w / 2) + ' ' + h + ' L 0 ' + (h / 2) + ' Z';
      var paths = inner.querySelectorAll('path');
      Array.prototype.forEach.call(paths, function (p) { p.setAttribute('d', d); });
    } else if (shape === 'chart') {
      var foChart = inner.querySelector('.alur-chart-fo');
      if (foChart) {
        foChart.setAttribute('width', Math.max(12, w));
        foChart.setAttribute('height', Math.max(12, h));
        foChart.setAttribute('y', 0);
      }
      var chartRects = inner.querySelectorAll('rect');
      if (chartRects[0]) {
        chartRects[0].setAttribute('width', w);
        chartRects[0].setAttribute('height', h);
      }
    } else if (shape === 'table') {
      /* The table lives in a foreignObject: the box alone is not enough, the
         embedded table has to follow the node when it is resized. */
      var foTable = inner.querySelector('.alur-table-fo');
      if (foTable) {
        foTable.setAttribute('width', Math.max(20, w));
        foTable.setAttribute('height', Math.max(20, h));
      }
      var tableRects = inner.querySelectorAll('rect');
      if (tableRects[0]) {
        tableRects[0].setAttribute('width', w);
        tableRects[0].setAttribute('height', h);
      }
    } else if (shape !== 'plain' && shape !== 'none') {
      var rects = inner.querySelectorAll('rect');
      if (rects[0]) {
        rects[0].setAttribute('width', w);
        rects[0].setAttribute('height', h);
        rects[0].setAttribute('rx', shape === 'pill' ? h / 2 : 12);
      }
      if (rects[1]) {
        rects[1].setAttribute('height', h);
        rects[1].setAttribute('rx', shape === 'pill' ? h / 2 : 2);
      }
    }

    var handles = stage.querySelectorAll('.alur-handle');
    Array.prototype.forEach.call(handles, function (r) {
      if (r.getAttribute('data-node-id') !== n.id) return;
      var spec = {
        nw: [0, 0], n: [w / 2, 0], ne: [w, 0], e: [w, h / 2],
        se: [w, h], s: [w / 2, h], sw: [0, h], w: [0, h / 2]
      }[r.getAttribute('data-handle')];
      if (!spec) return;
      r.setAttribute('x', (n.x || 0) + spec[0] - 4);
      r.setAttribute('y', (n.y || 0) + spec[1] - 4);
    });
  }

  function nodeBoundaryPoint(n, towardX, towardY) {
    var b = nodeVisualBounds(n);
    var w = b.w;
    var h = b.h;
    var cx = b.x + w / 2;
    var cy = b.y + h / 2;
    var dx = towardX - cx;
    var dy = towardY - cy;
    if (!dx && !dy) return [cx, cy];
    var pad = 1;
    var hw = Math.max(1, w / 2 - pad);
    var hh = Math.max(1, h / 2 - pad);
    var shape = n.shape || 'box';
    var t;
    if (shape === 'circle') {
      var rx = Math.max(1, hw);
      var ry = Math.max(1, hh);
      t = 1 / Math.sqrt((dx * dx) / (rx * rx) + (dy * dy) / (ry * ry));
    } else if (shape === 'diamond') {
      t = 1 / (Math.abs(dx) / hw + Math.abs(dy) / hh);
    } else {
      var radius = shape === 'pill' ? Math.min(hw, hh) :
        (n.edge === 'round' ? Math.min(14, hh) : 0);
      t = Math.min(hw / Math.max(0.001, Math.abs(dx)),
                   hh / Math.max(0.001, Math.abs(dy)));
      if (radius > 0) {
        var px = dx * t;
        var py = dy * t;
        if (Math.abs(px) > hw - radius && Math.abs(py) > hh - radius) {
          var ccx = (px < 0 ? -1 : 1) * (hw - radius);
          var ccy = (py < 0 ? -1 : 1) * (hh - radius);
          var len = Math.sqrt(dx * dx + dy * dy);
          var ux = dx / len;
          var uy = dy / len;
          var bq = ux * ccx + uy * ccy;
          var cq = ccx * ccx + ccy * ccy - radius * radius;
          var disc = bq * bq - cq;
          if (disc >= 0) {
            var tc = bq + Math.sqrt(disc);
            if (tc > 0) t = tc / len;
          }
        }
      }
    }
    return [cx + dx * t, cy + dy * t];
  }

  function edgePointsForNodes(a, b) {
    var ab = nodeVisualBounds(a);
    var bb = nodeVisualBounds(b);
    var ac = [ab.x + ab.w / 2, ab.y + ab.h / 2];
    var bc = [bb.x + bb.w / 2, bb.y + bb.h / 2];
    return [nodeBoundaryPoint(a, bc[0], bc[1]), nodeBoundaryPoint(b, ac[0], ac[1])];
  }

  function updateEdgesForNode(nodeId) {
    var s = state.spec;
    var nodes = s.nodes || {};
    (s.edges || []).forEach(function (e, i) {
      if (e.points) return;
      if (e.from !== nodeId && e.to !== nodeId) return;
      var a = nodes[e.from];
      var b = nodes[e.to];
      if (!a || !b) return;
      /* Attach to the shape border, not the centre. The centre-to-centre
         path is hidden under the node, which made the arrow look like it
         stopped before the box/circle. */
      var ends = edgePointsForNodes(a, b);
      var d = AlurKit.curve(ends[0][0], ends[0][1], ends[1][0], ends[1][1]);
      var main = stage.querySelector('.alur-canvas-edge[data-edge="' + i + '"]');
      if (!main) return;
      var group = main.parentNode;
      if (group && group.querySelectorAll) {
        Array.prototype.forEach.call(group.querySelectorAll('path'), function (p) {
          if (p !== main) p.setAttribute('d', d);
        });
      }
      main.setAttribute('d', d);
      /* Panah ikut pindah, tidak disembunyikan. Sebelumnya head di-opacity:0
         selama drag dan hanya digambar ulang saat pointerup, sehingga panah
         "hilang" beberapa saat. Sekarang geometrinya dihitung ulang dari titik
         sambung yang baru, jadi panah menempel di border walau node bergerak.
         Heads now follow the edge: the old code hid them during a drag and only
         redrew on pointerup, which is why arrows kept vanishing. */
      var heads = stage.querySelectorAll('.alur-edge-head[data-edge="' + i + '"]');
      if (heads.length) {
        var color = AlurKit.color(e.color || state.spec.color || 'blue');
        var type = e.arrowType || 'arrow';
        var width = e.width || 2.4;
        var startHead = !!e.arrowStart;
        var endHead = e.arrowEnd !== undefined ? e.arrowEnd : true;
        Array.prototype.forEach.call(heads, function (h, hi) {
          var isStart = startHead && heads.length > 1 ? hi === 0 : false;
          var tip = isStart ? ends[0] : ends[1];
          var from = isStart ? ends[1] : ends[0];
          h.style.opacity = '';
          if (!AlurKit.arrowInto(h, tip, from, type, color, { width: width })) {
            /* bentuk tidak bisa diperbarui (mis. circle -> arrow): buang, biar
               render berikutnya menggambar yang benar. */
            if (h.parentNode) h.parentNode.removeChild(h);
          }
        });
      }
    });
  }

  function drawGuides(primaryId) {
    clearGuides();
    var svg = stage.querySelector('svg');
    if (!svg) return;
    var overlay = overlayLayer();
    if (!overlay) return;
    var s = state.spec;
    var n = s.nodes[primaryId];
    if (!n) return;
    var nw = n.w || 160;
    var nh = n.h || 60;
    var px = [n.x || 0, (n.x || 0) + nw / 2, (n.x || 0) + nw];
    var py = [n.y || 0, (n.y || 0) + nh / 2, (n.y || 0) + nh];
    /* Kanvas tanpa halaman: patokan snap hanya objek lain, bukan tepi/center
       halaman. Garis panduan membentang sepanjang viewport saat ini.
       No page edges: guides snap to other objects only, across the view. */
    var xs = [];
    var ys = [];
    var vb = svg.viewBox && svg.viewBox.baseVal;
    var gx0 = vb ? vb.x : -2000, gy0 = vb ? vb.y : -2000;
    var gx1 = vb ? vb.x + vb.width : 4000, gy1 = vb ? vb.y + vb.height : 4000;
    Object.keys(s.nodes || {}).forEach(function (id) {
      if (id === primaryId) return;
      var o = s.nodes[id];
      if (!o) return;
      var ow = o.w || 160;
      var oh = o.h || 60;
      xs.push(o.x || 0, (o.x || 0) + ow / 2, (o.x || 0) + ow);
      ys.push(o.y || 0, (o.y || 0) + oh / 2, (o.y || 0) + oh);
    });
    var near = 6;
    var seenX = {};
    var seenY = {};
    function line(d) { AlurKit.path(overlay, d, 'alur-guide', { fill: 'none' }); }
    px.forEach(function (mx) {
      xs.forEach(function (tx) {
        if (Math.abs(tx - mx) > near) return;
        var key = Math.round(tx);
        if (seenX[key]) return;
        seenX[key] = true;
        line('M ' + tx + ' ' + gy0 + ' L ' + tx + ' ' + gy1);
      });
    });
    py.forEach(function (my) {
      ys.forEach(function (ty) {
        if (Math.abs(ty - my) > near) return;
        var key = Math.round(ty);
        if (seenY[key]) return;
        seenY[key] = true;
        line('M ' + gx0 + ' ' + ty + ' L ' + gx1 + ' ' + ty);
      });
    });
  }

  /* Table edits are made inside the canvas module (so the reading page gets
     them for free); the editor only mirrors the result into state.spec. */
  stage.addEventListener('pointerdown', function (ev) {
    if (ev.target.closest && ev.target.closest('[data-table-action]')) pushHistory();
  });

  stage.addEventListener('alur:table', function (ev) {
    var d = ev.detail || {};
    var n = state.spec.nodes && state.spec.nodes[d.id];
    if (!n || !d.columns || !d.rows) return;
    n.columns = d.columns;
    n.rows = d.rows;
    touchSpec();
    syncControls();
    render();
  });

  stage.addEventListener('input', function (ev) {
    var cell = ev.target.closest && ev.target.closest('td[data-table-node], th[data-table-node]');
    if (!cell) return;
    var host = cell.closest('[data-table-node]');
    var id = host && host.getAttribute('data-table-node');
    var n = state.spec.nodes && state.spec.nodes[id];
    if (!n) return;
    ensureTableData(n);
    var r = parseInt(cell.getAttribute('data-r'), 10);
    var c = parseInt(cell.getAttribute('data-c'), 10);
    if (cell.getAttribute('data-r') === '-1') {
      if (n.columns[c] != null) n.columns[c] = cell.textContent;
    } else if (n.rows[r] && n.rows[r][c] != null) {
      n.rows[r][c] = cell.textContent;
    }
    touchSpec();
    syncChartDataPanel();
  });

  function dragMove(ev) {
    if (!editor.drag) return;
    var svg = stage.querySelector('svg');
    if (!svg) return;
    var p = svgPoint(svg, ev);

    if (editor.drag.type === 'pan') {
      var svg = stage.querySelector('svg');
      var rect = svg ? svg.getBoundingClientRect() : { width: 1, height: 1 };
      var vb = svg && svg.viewBox ? svg.viewBox.baseVal : null;
      var sx = vb && rect.width ? vb.width / rect.width : 1;
      var sy = vb && rect.height ? vb.height / rect.height : 1;
      state.spec.panX = editor.drag.panX - (ev.clientX - editor.drag.clientX) * sx;
      state.spec.panY = editor.drag.panY - (ev.clientY - editor.drag.clientY) * sy;
      applyView(true);
      touchSpec();
      return;
    }

    if (editor.drag.type === 'erase') {
      eraseAt(ev.clientX, ev.clientY);
      return;
    }

    if (editor.drag.type === 'laser') {
      var lp = editor.drag.points;
      var lastL = lp[lp.length - 1];
      if (Math.abs(p.x - lastL[0]) + Math.abs(p.y - lastL[1]) > 2) {
        lp.push([p.x, p.y]);
        if (editor.drag.preview) editor.drag.preview.setAttribute('d', pointsToPath(lp));
      }
      return;
    }

    if (editor.drag.type === 'arrow-link') {
      editor.drag.x1 = p.x;
      editor.drag.y1 = p.y;
      editor.drag.moved = true;
      if (editor.drag.preview) {
        editor.drag.preview.setAttribute('d',
          'M ' + editor.drag.x0.toFixed(1) + ' ' + editor.drag.y0.toFixed(1) +
          ' L ' + p.x.toFixed(1) + ' ' + p.y.toFixed(1));
      }
      return;
    }

    if (editor.drag.type === 'arrow') {
      if (!editor.drag.moved) {
        var adx = p.x - editor.drag.x0;
        var ady = p.y - editor.drag.y0;
        if (Math.abs(adx) + Math.abs(ady) <= 4) {
          editor.drag.x1 = editor.drag.x0;
          editor.drag.y1 = editor.drag.y0;
          return;
        }
        editor.drag.moved = true;
        if (editor.drag.armedFrom) {
          clearConnectArm();
          editor.drag.armedFrom = null;
        }
      }
      editor.drag.x1 = p.x;
      editor.drag.y1 = p.y;
      editor.drag.points = [[editor.drag.x0, editor.drag.y0], [p.x, p.y]];
      if (editor.drag.preview) {
        editor.drag.preview.setAttribute('d',
          'M ' + editor.drag.x0.toFixed(1) + ' ' + editor.drag.y0.toFixed(1) +
          ' L ' + p.x.toFixed(1) + ' ' + p.y.toFixed(1));
      }
      return;
    }

    if (editor.drag.type === 'move-edge') {
      var me = state.spec.edges && state.spec.edges[editor.drag.edge];
      if (!me) return;
      if (!me.points || me.points.length < 2) {
        var mna = state.spec.nodes && state.spec.nodes[me.from];
        var mnb = state.spec.nodes && state.spec.nodes[me.to];
        if (!mna || !mnb) return;
        var mca = [mna.x + (mna.w || 160) / 2, mna.y + (mna.h || 60) / 2];
        var mcb = [mnb.x + (mnb.w || 160) / 2, mnb.y + (mnb.h || 60) / 2];
        me.points = [nodeBoundaryPoint(mna, mcb[0], mcb[1]), nodeBoundaryPoint(mnb, mca[0], mca[1])];
        me.curved = true;
        delete me.from;
        delete me.to;
        editor.drag.px = editor.drag.sx;
        editor.drag.py = editor.drag.sy;
        editor.drag.points = me.points.map(function (pt) { return [pt[0], pt[1]]; });
        render();
      }
      if (!me.points) return;
      if (!editor.drag.points) {
        editor.drag.points = me.points.map(function (pt) { return [pt[0], pt[1]]; });
      }
      editor.drag.moved = true;
      var mdx = p.x - editor.drag.px;
      var mdy = p.y - editor.drag.py;
      var msnap = ev.altKey ? 1 : GRID;
      var mox = editor.drag.points[0][0];
      var moy = editor.drag.points[0][1];
      var dxr = mox + mdx;
      var dyr = moy + mdy;
      if (msnap > 1) {
        dxr = Math.round(dxr / msnap) * msnap;
        dyr = Math.round(dyr / msnap) * msnap;
      }
      var sdx = dxr - mox;
      var sdy = dyr - moy;
      me.points = editor.drag.points.map(function (pt) { return [pt[0] + sdx, pt[1] + sdy]; });
      updateEdgePath(editor.drag.edge);
      touchSpec();
      return;
    }

    if (editor.drag.type === 'edge-point') {
      var ee = state.spec.edges && state.spec.edges[editor.drag.edge];
      if (!ee || !ee.points) return;
      var snap = ev.altKey ? 1 : GRID;
      var ex = snap > 1 ? Math.round(p.x / snap) * snap : Math.round(p.x);
      var ey = snap > 1 ? Math.round(p.y / snap) * snap : Math.round(p.y);
      ee.points[editor.drag.index] = [ex, ey];
      updateEdgePath(editor.drag.edge);
      touchSpec();
      return;
    }

    if (editor.drag.type === 'draw') {
      var pts = editor.drag.points;
      var last = pts[pts.length - 1];
      if (Math.abs(p.x - last[0]) + Math.abs(p.y - last[1]) > 2) {
        pts.push([p.x, p.y]);
        if (editor.drag.preview) editor.drag.preview.setAttribute('d', pointsToPath(pts));
      }
      return;
    }

    if (editor.drag.type === 'line') {
      editor.drag.x1 = p.x;
      editor.drag.y1 = p.y;
      if (Math.abs(p.x - editor.drag.x0) + Math.abs(p.y - editor.drag.y0) > 3) {
        editor.drag.moved = true;
      }
      var lp = editor.drag.chain || [[editor.drag.x0, editor.drag.y0]];
      if (editor.drag.preview) {
        var ld = 'M ' + lp[0][0].toFixed(1) + ' ' + lp[0][1].toFixed(1);
        for (var li = 1; li < lp.length; li++) {
          ld += ' L ' + lp[li][0].toFixed(1) + ' ' + lp[li][1].toFixed(1);
        }
        ld += ' L ' + p.x.toFixed(1) + ' ' + p.y.toFixed(1);
        editor.drag.preview.setAttribute('d', ld);
      }
      return;
    }

    if (editor.drag.type === 'create') {
      editor.drag.x1 = p.x;
      editor.drag.y1 = p.y;
      editor.drag.moved = true;
      var x = Math.min(editor.drag.x0, p.x);
      var y = Math.min(editor.drag.y0, p.y);
      var w = Math.abs(p.x - editor.drag.x0);
      var h = Math.abs(p.y - editor.drag.y0);
      if (editor.drag.preview) setCreatePreview(editor.drag.preview, editor.drag.shape, x, y, w, h);
      return;
    }

    if (editor.drag.type === 'marquee') {
      editor.drag.x1 = p.x;
      editor.drag.y1 = p.y;
      if (editor.drag.preview) {
        var mx = Math.min(editor.drag.x0, p.x);
        var my = Math.min(editor.drag.y0, p.y);
        editor.drag.preview.setAttribute('x', mx);
        editor.drag.preview.setAttribute('y', my);
        editor.drag.preview.setAttribute('width', Math.abs(p.x - editor.drag.x0));
        editor.drag.preview.setAttribute('height', Math.abs(p.y - editor.drag.y0));
      }
      return;
    }

    if (editor.drag.type === 'move') {
      var drag = editor.drag;
      var dx = p.x - drag.startX;
      var dy = p.y - drag.startY;
      /* A click is not a drag: nothing moves until the pointer really travels
         (Excalidraw's dragging threshold). */
      if (!drag.moved) {
        if (Math.abs(dx) + Math.abs(dy) < DRAG_THRESHOLD / (state.spec.zoom || 1)) return;
        drag.moved = true;
      }
      var snap = (ev.altKey || editor.snap === false) ? 1 : GRID;
      var lead = drag.items[0];
      var leadX = lead.x + dx;
      var leadY = lead.y + dy;
      if (snap > 1) {
        leadX = Math.round(leadX / snap) * snap;
        leadY = Math.round(leadY / snap) * snap;
      }
      var ddx = leadX - lead.x;
      var ddy = leadY - lead.y;
      drag.items.forEach(function (item) {
        var node = state.spec.nodes[item.id];
        if (!node) return;
        node.x = Math.round(item.x + ddx);
        node.y = Math.round(item.y + ddy);
        if (item.el) {
          item.el.setAttribute('transform', 'translate(' + node.x + ' ' + node.y + ')');
        }
        updateEdgesForNode(item.id);
      });
      drawSelectionHandles();
      drawGuides(lead.id);
      touchSpec();
      return;
    }

    if (editor.drag.type === 'resize') {
      var rn = state.spec.nodes[editor.drag.id];
      if (!rn) return;
      var dx = p.x - editor.drag.px;
      var dy = p.y - editor.drag.py;
      var x2 = editor.drag.x0, y2 = editor.drag.y0;
      var w2 = editor.drag.w0, h2 = editor.drag.h0;
      if (editor.drag.handle.indexOf('e') >= 0) w2 = editor.drag.w0 + dx;
      if (editor.drag.handle.indexOf('s') >= 0) h2 = editor.drag.h0 + dy;
      if (editor.drag.handle.indexOf('w') >= 0) { x2 = editor.drag.x0 + dx; w2 = editor.drag.w0 - dx; }
      if (editor.drag.handle.indexOf('n') >= 0) { y2 = editor.drag.y0 + dy; h2 = editor.drag.h0 - dy; }
      var snap = (ev.altKey || editor.snap === false) ? 1 : GRID;
      if (snap > 1) {
        x2 = Math.round(x2 / snap) * snap;
        y2 = Math.round(y2 / snap) * snap;
        w2 = Math.max(40, Math.round(w2 / snap) * snap);
        h2 = Math.max(30, Math.round(h2 / snap) * snap);
      }
      rn.x = Math.round(x2);
      rn.y = Math.round(y2);
      rn.w = Math.max(40, Math.round(w2));
      rn.h = Math.max(30, Math.round(h2));
      var nodeEl = stage.querySelector('.alur-canvas-node[data-node-id="' + rn.id + '"]');
      updateNodeVisual(rn, nodeEl);
      updateEdgesForNode(rn.id);
      touchSpec();
    }
  }

  /* ---- auto-pan -------------------------------------------------------
     Menyeret dekat tepi menggeser kanvas, jadi garis bisa ditarik terus ke
     luar layar tanpa "macet" di pinggir. Drag near the edge keeps going. */
  var AUTOPAN_EDGE = 60;
  var AUTOPAN_MAX = 18;
  var autoPanRaf = null;

  function updateAutoPan() {
    if (!editor.drag || editor.drag.type === 'pan' || !editor.lastClient) {
      editor.autoPan = null;
      return;
    }
    var r = stage.getBoundingClientRect();
    var c = editor.lastClient;
    var vx = 0, vy = 0;
    var dl = c.x - r.left, dr = r.right - c.x;
    var dt = c.y - r.top, db = r.bottom - c.y;
    if (dl < AUTOPAN_EDGE) vx = -1 + Math.max(0, dl) / AUTOPAN_EDGE;
    else if (dr < AUTOPAN_EDGE) vx = 1 - Math.max(0, dr) / AUTOPAN_EDGE;
    if (dt < AUTOPAN_EDGE) vy = -1 + Math.max(0, dt) / AUTOPAN_EDGE;
    else if (db < AUTOPAN_EDGE) vy = 1 - Math.max(0, db) / AUTOPAN_EDGE;
    editor.autoPan = (vx || vy) ? { x: vx, y: vy } : null;
    if (editor.autoPan) startAutoPan();
  }

  function startAutoPan() {
    if (autoPanRaf) return;
    var step = function () {
      autoPanRaf = null;
      if (!editor.drag || !editor.autoPan) return;
      var z = clampZoom(state.spec.zoom) || 1;
      /* panX/panY belum tentu ada di scene lama: jangan pakai += langsung,
         undefined + n = NaN dan kanvas berhenti bergeser selamanya. */
      state.spec.panX = (state.spec.panX || 0) + editor.autoPan.x * AUTOPAN_MAX / z;
      state.spec.panY = (state.spec.panY || 0) + editor.autoPan.y * AUTOPAN_MAX / z;
      applyView(true);
      var c = editor.lastClient;
      if (c) dragMove({ clientX: c.x, clientY: c.y, altKey: c.alt });
      autoPanRaf = requestAnimationFrame(step);
    };
    autoPanRaf = requestAnimationFrame(step);
  }

  window.addEventListener('pointermove', function (ev) {
    if (!editor.drag) return;
    editor.lastClient = { x: ev.clientX, y: ev.clientY, alt: !!ev.altKey };
    updateAutoPan();
    dragMove(ev);
  });

  function clearConnectArm() {
    if (editor.from) {
      var el = stage.querySelector('.alur-canvas-node[data-node-id="' + editor.from + '"]');
      if (el) el.classList.remove('is-connect-from');
      editor.from = null;
    }
    Array.prototype.forEach.call(document.querySelectorAll('.alur-canvas-node.is-connect-from'), function (node) {
      node.classList.remove('is-connect-from');
    });
  }

  function startConnect(id) {
    var node = state.spec.nodes && state.spec.nodes[id];
    if (!node) return;
    setTool('arrow');
    editor.from = id;
    var el = stage.querySelector('.alur-canvas-node[data-node-id="' + id + '"]');
    if (el) el.classList.add('is-connect-from');
    syncControls();
    syncEditor();
    syncShapePanel();
    var st = document.getElementById('statusTool');
    if (st) st.textContent = 'connect: tap a target node';
  }

  function connectNodes(from, to) {
    if (!from || !to || from === to) return false;
    var edges = state.spec.edges || (state.spec.edges = []);
    for (var i = 0; i < edges.length; i++) {
      var e = edges[i];
      if ((e.from === from && e.to === to) || (e.from === to && e.to === from)) {
        state.spec.selected = null;
        state.spec.selectedEdge = i;
        state.spec.selectedEdges = [i];
        state.spec.selectedDrawing = null;
        touchSpec();
        syncControls();
        syncEditor();
        render();
        /* Say it out loud: an existing cable is selected, not a dead tool. */
        var dup = document.getElementById('statusTool');
        if (dup) {
          dup.textContent = 'already connected — cable selected';
          setTimeout(function () { if (dup) dup.textContent = 'tool: ' + editor.tool; }, 1400);
        }
        return true;
      }
    }
    var es = edgeStyle();
    edges.push({
      from: from,
      to: to,
      cable: state.spec.cable || 'solid',
      motion: state.spec.motion || 'flow',
      arrowStart: false,
      arrowEnd: true,
      arrowType: es.arrowType || 'arrow',
      strokeStyle: es.strokeStyle || state.spec.cable || 'solid',
      width: es.width || 2
    });
    if (es.color) edges[edges.length - 1].color = es.color;
    state.spec.selected = null;
    state.spec.selectedEdge = edges.length - 1;
    state.spec.selectedEdges = [edges.length - 1];
    state.spec.selectedDrawing = null;
    touchSpec();
    syncControls();
    syncEditor();
    render();
    return true;
  }

  function endDrag() {
    if (!editor.drag) return;
    var drag = editor.drag;
    editor.drag = null;
    editor.lastClient = null;
    editor.autoPan = null;
    if (autoPanRaf) { cancelAnimationFrame(autoPanRaf); autoPanRaf = null; }

    if (drag.type === 'pan') {
      applyView();
      syncControls();
      syncEditor();
      return;
    }

    if (drag.type === 'erase') {
      syncControls();
      syncEditor();
      render();
      return;
    }

    if (drag.type === 'laser') {
      if (drag.preview && drag.preview.parentNode) {
        var lp = drag.preview;
        setTimeout(function () { if (lp.parentNode) lp.parentNode.removeChild(lp); }, 280);
      }
      return;
    }

    if (drag.type === 'arrow-link') {
      if (drag.preview && drag.preview.parentNode) drag.preview.parentNode.removeChild(drag.preview);
      var endNode = (drag.moved && !drag.preventBind) ? nodeAtPoint(drag.x1, drag.y1) : null;
      if (endNode && endNode !== drag.from) {
        var fromEl = stage.querySelector('.alur-canvas-node[data-node-id="' + drag.from + '"]');
        if (fromEl) fromEl.classList.remove('is-connect-from');
        editor.from = null;
        connectNodes(drag.from, endNode);
        if (!editor.keepTool) setTool('select');
        return;
      }
      if (drag.moved) {
        var ld = Math.sqrt(Math.pow(drag.x1 - drag.x0, 2) + Math.pow(drag.y1 - drag.y0, 2));
        if (ld >= 6) {
          state.spec.edges = state.spec.edges || [];
          state.spec.edges.push({
            points: [[drag.x0, drag.y0], [drag.x1, drag.y1]],
            cable: state.spec.cable || 'solid',
            motion: 'none',
            arrowStart: true,
            arrowEnd: true,
            arrowType: 'arrow',
            curved: true,
            color: '#e6edf3',
            width: 2
          });
          state.spec.selected = null;
          state.spec.selectedEdge = state.spec.edges.length - 1;
          state.spec.selectedDrawing = null;
          var fromEl2 = stage.querySelector('.alur-canvas-node[data-node-id="' + drag.from + '"]');
          if (fromEl2) fromEl2.classList.remove('is-connect-from');
          editor.from = null;
          touchSpec();
          syncControls();
          syncEditor();
          render();
          if (!editor.keepTool) setTool('select');
        }
      }
      return;
    }

    if (drag.type === 'arrow') {
      if (drag.preview && drag.preview.parentNode) drag.preview.parentNode.removeChild(drag.preview);
      var downNode = drag.downNode || null;
      var aNode = downNode || nodeAtPoint(drag.x0, drag.y0);
      var bNode = nodeAtPoint(drag.x1, drag.y1);
      var adx = drag.x1 - drag.x0;
      var ady = drag.y1 - drag.y0;
      var adist = Math.sqrt(adx * adx + ady * ady);

      /* A source was already armed (tap-armed or Connect button). A tap on a
         target completes it; a drag starts a new arrow from the pressed node. */
      if (drag.armedFrom) {
        if (!drag.moved) {
          clearConnectArm();
          if (downNode && downNode !== drag.armedFrom && state.spec.nodes[downNode]) {
            pushHistory();
            connectNodes(drag.armedFrom, downNode);
            if (!editor.keepTool) setTool('select');
          } else {
            syncControls();
            syncEditor();
          }
          return;
        }
        clearConnectArm();
      }

      /* A tap without a source arms the node for a second tap. */
      if (!drag.moved) {
        if (downNode && state.spec.nodes[downNode]) {
          editor.from = downNode;
          var armEl = stage.querySelector('.alur-canvas-node[data-node-id="' + downNode + '"]');
          if (armEl) armEl.classList.add('is-connect-from');
          var st = document.getElementById('statusTool');
          if (st) st.textContent = 'connect: tap a target node';
        }
        syncControls();
        syncEditor();
        return;
      }

      if (connectNodes(aNode, bNode)) {
        if (!editor.keepTool) setTool('select');
        return;
      }
      var aNodes = state.spec.nodes || {};
      var p0 = [drag.x0, drag.y0];
      var p1 = [drag.x1, drag.y1];
      if (aNode && !bNode && aNodes[aNode]) {
        p0 = nodeBoundaryPoint(aNodes[aNode], p1[0], p1[1]);
      } else if (!aNode && bNode && aNodes[bNode]) {
        p1 = nodeBoundaryPoint(aNodes[bNode], p0[0], p0[1]);
      }
      var fdx = p1[0] - p0[0];
      var fdy = p1[1] - p0[1];
      if (adist >= 6 && Math.sqrt(fdx * fdx + fdy * fdy) >= 6) {
        pushHistory();
        state.spec.edges = state.spec.edges || [];
        state.spec.edges.push({
          points: [p0, p1],
          cable: state.spec.cable || 'solid',
          motion: 'none',
          arrowStart: true,
          arrowEnd: true,
          arrowType: 'arrow',
          curved: true,
          color: '#e6edf3',
          width: 2
        });
        state.spec.selected = null;
        state.spec.selectedEdge = state.spec.edges.length - 1;
        state.spec.selectedDrawing = null;
        touchSpec();
        syncControls();
        syncEditor();
        render();
        if (!editor.keepTool) setTool('select');
        return;
      }
      syncControls();
      syncEditor();
      return;
    }

    if (drag.type === 'edge-point' || drag.type === 'move-edge') {
      if (drag.type === 'move-edge') {
        var mv = state.spec.edges && state.spec.edges[drag.edge];
        if (mv) mv.curved = true;
      }
      touchSpec();
      syncControls();
      syncEditor();
      render();
      return;
    }

    if (drag.type === 'move' && !drag.moved) {
      /* Excalidraw: a plain click on one member of a multi-selection narrows
         the selection to that element. */
      if (drag.collapse) {
        setSelection([drag.collapse]);
        syncControls();
        syncEditor();
        render();
        return;
      }
      syncControls();
      syncEditor();
      updateSelectionVisual();
      return;
    }

    if (drag.type === 'line') {
      if (!drag.moved) {
        if (!editor.lineChain) {
          editor.lineChain = [[drag.x0, drag.y0]];
        } else {
          editor.lineChain.push([drag.x1, drag.y1]);
          var lcFirst = editor.lineChain[0];
          var lcLast = editor.lineChain[editor.lineChain.length - 1];
          var lcClose = Math.sqrt(
            Math.pow(lcLast[0] - lcFirst[0], 2) + Math.pow(lcLast[1] - lcFirst[1], 2)) < 8;
          if (editor.lineChain.length >= 3 && lcClose) { finishLineChain(); return; }
        }
        editor.drag = null;
        syncControls();
        syncEditor();
        return;
      }
      if (drag.preview && drag.preview.parentNode) drag.preview.parentNode.removeChild(drag.preview);
      editor.lineChain = null;
      var lNodeA = nodeAtPoint(drag.x0, drag.y0);
      var lNodeB = nodeAtPoint(drag.x1, drag.y1);
      if (connectNodes(lNodeA, lNodeB)) {
        if (!editor.keepTool) setTool('select');
        return;
      }
      var lNodes = state.spec.nodes || {};
      var lp0 = [drag.x0, drag.y0];
      var lp1 = [drag.x1, drag.y1];
      if (lNodeA && !lNodeB && lNodes[lNodeA]) {
        lp0 = nodeBoundaryPoint(lNodes[lNodeA], lp1[0], lp1[1]);
      } else if (!lNodeA && lNodeB && lNodes[lNodeB]) {
        lp1 = nodeBoundaryPoint(lNodes[lNodeB], lp0[0], lp0[1]);
      }
      var ldx = lp1[0] - lp0[0];
      var ldy = lp1[1] - lp0[1];
      if (Math.sqrt(ldx * ldx + ldy * ldy) >= 6) {
        state.spec.edges = state.spec.edges || [];
        var les = edgeStyle();
        state.spec.edges.push({
          points: [lp0, lp1],
          cable: state.spec.cable || 'solid',
          motion: 'none',
          arrowStart: false,
          arrowEnd: false,
          arrowType: les.arrowType || 'arrow',
          strokeStyle: les.strokeStyle || state.spec.cable || 'solid',
          curved: false,
          color: les.color || '#e6edf3',
          width: les.width || 2
        });
        state.spec.selected = null;
        state.spec.selectedEdge = state.spec.edges.length - 1;
        state.spec.selectedDrawing = null;
        touchSpec();
        syncControls();
        syncEditor();
        render();
        if (!editor.keepTool) setTool('select');
      }
      return;
    }

    if (drag.type === 'draw') {
      if (drag.preview && drag.preview.parentNode) drag.preview.parentNode.removeChild(drag.preview);
      if (drag.points.length > 1) {
        state.spec.drawings = state.spec.drawings || [];
        var drawingId = 'd' + (++drawSeq);
        state.spec.drawings.push({
          id: drawingId,
          d: pointsToPath(drag.points),
          color: editor.penStyle.color,
          width: editor.penStyle.width,
          strokeStyle: editor.penStyle.strokeStyle,
          opacity: editor.penStyle.opacity
        });
        state.spec.selectedDrawing = drawingId;
        state.spec.selected = null;
        state.spec.selectedEdge = null;
        state.spec.selectedEdges = [];
        touchSpec();
        syncControls();
        syncEditor();
        render();
      }
      return;
    }

    if (drag.type === 'create') {
      if (drag.preview && drag.preview.parentNode) drag.preview.parentNode.removeChild(drag.preview);
      var x = Math.min(drag.x0, drag.x1);
      var y = Math.min(drag.y0, drag.y1);
      var w = Math.abs(drag.x1 - drag.x0);
      var h = Math.abs(drag.y1 - drag.y0);
      if (drag.shape === 'text' && (!drag.moved || w < 24 || h < 18)) {
        var textId = addNode('text', drag.x0 - 90, drag.y0 - 20, 180, 40);
        if (textId) setTimeout(function () { startTextEdit(textId); }, 0);
        if (!editor.keepTool) setTool('select');
        return;
      }
      if (!drag.moved || w < 24 || h < 18) {
        /* Klik tanpa menyeret = bentuk ukuran default, ditengahkan di kursor
           (cara Excalidraw). Tidak ada lagi pesan "drag to size" yang
           membuat tool terasa kaku. */
        var def = { box: [180, 100], diamond: [160, 100], circle: [130, 130], text: [180, 40] };
        var d = def[drag.shape] || [160, 100];
        var dx0 = drag.x0 - d[0] / 2;
        var dy0 = drag.y0 - d[1] / 2;
        var nid0 = addNode(drag.shape, snapGrid(dx0), snapGrid(dy0), d[0], d[1]);
        if (drag.shape === 'text' && nid0) {
          setTimeout(function () { startTextEdit(nid0); }, 0);
        }
        if (!editor.keepTool) setTool('select');
        return;
      }
      var newId = addNode(drag.shape, x, y, w, h);
      if (drag.shape === 'text' && newId) {
        setTimeout(function () { startTextEdit(newId); }, 0);
      }
      if (!editor.keepTool) setTool('select');
      return;
    }

    if (drag.type === 'marquee') {
      if (drag.preview && drag.preview.parentNode) drag.preview.parentNode.removeChild(drag.preview);
      var rx = Math.min(drag.x0, drag.x1);
      var ry = Math.min(drag.y0, drag.y1);
      var rw = Math.abs(drag.x1 - drag.x0);
      var rh = Math.abs(drag.y1 - drag.y0);
      if (rw < 3 && rh < 3) {
        if (!drag.base.length) setSelection([]);
        return;
      }
      var hits = drag.base.slice();
      Object.keys(state.spec.nodes || {}).forEach(function (id) {
        var n = state.spec.nodes[id];
        if (!n) return;
        var nw = n.w || 160;
        var nh = n.h || 60;
        if ((n.x || 0) < rx + rw && (n.x || 0) + nw > rx &&
            (n.y || 0) < ry + rh && (n.y || 0) + nh > ry) {
          if (hits.indexOf(id) < 0) hits.push(id);
        }
      });
      setSelection(hits);
      return;
    }

    if (drag.type === 'move') {
      drag.items.forEach(function (item) {
        if (item.el) item.el.classList.remove('is-dragging');
      });
      clearGuides();
      if (drag.toggle && !drag.moved) {
        var ids = selectionIds().filter(function (id) { return id !== drag.toggle; });
        setSelection(ids);
        return;
      }
    }

    syncControls();
    syncEditor();
    render();
  }

  window.addEventListener('pointerup', endDrag);
  window.addEventListener('pointercancel', endDrag);

  /* Touch browsers may still claim the gesture for scrolling even with
     touch-action:none. While a canvas drag is active, keep the gesture. */
  stage.addEventListener('touchmove', function (ev) {
    if (editor.drag) ev.preventDefault();
  }, { passive: false });

  stage.addEventListener('wheel', function (ev) {
    if (!isCanvas()) return;
    ev.preventDefault();
    var svg = stage.querySelector('svg');
    if (!svg) return;
    var m = viewMetrics();
    if (!m.w || !m.h) return;
    /* Cara Excalidraw: roda = geser kanvas (shift = geser mendatar), ctrl/⌘
       + roda (termasuk cubit trackpad) = zoom, dan zoom dikunci 10%–100%.
       Roda biasa TIDAK PERNAH memperbesar. */
    var unit = ev.deltaMode === 1 ? 16 : (ev.deltaMode === 2 ? m.h : 1);
    var dx = (ev.deltaX || 0) * unit;
    var dy = (ev.deltaY || 0) * unit;
    if (!ev.ctrlKey && !ev.metaKey) {
      if (ev.shiftKey && !dx) { dx = dy; dy = 0; }
      state.spec.panX = (state.spec.panX || 0) + dx / m.z;
      state.spec.panY = (state.spec.panY || 0) + dy / m.z;
      applyView();
      touchSpec();
      return;
    }
    var fx = (ev.clientX - m.left) / m.w;
    var fy = (ev.clientY - m.top) / m.h;
    var sceneX = (state.spec.panX || 0) + fx * m.vw;
    var sceneY = (state.spec.panY || 0) + fy * m.vh;
    /* Trackpad mengirim deltaY kecil; pakai langkah halus, mouse pakai 1.1. */
    var step = Math.abs(dy) < 20 ? (1 - dy / 400) : (dy < 0 ? 1.1 : 0.9);
    var z = clampZoom(m.z * step);
    if (z === m.z) return;
    state.spec.zoom = z;
    state.spec.panX = sceneX - fx * (m.w / z);
    state.spec.panY = sceneY - fy * (m.h / z);
    applyView();
    touchSpec();
  }, { passive: false });

  Array.prototype.forEach.call(document.querySelectorAll('[data-tool]'), function (b) {
    b.addEventListener('click', function () { setTool(b.getAttribute('data-tool')); });
  });

  function addAtCenter(shape, w, h) {
    var c = viewportSceneCenter();
    pushHistory();
    addNode(shape, c.x - w / 2, c.y - h / 2, w, h);
  }

  document.getElementById('addBox').addEventListener('click', function () { addAtCenter('box', 160, 60); });
  document.getElementById('addPlain').addEventListener('click', function () { addAtCenter('plain', 160, 40); });
  document.getElementById('addPill').addEventListener('click', function () { addAtCenter('pill', 160, 56); });
  document.getElementById('addCircle').addEventListener('click', function () { addAtCenter('circle', 110, 110); });
  document.getElementById('deleteBtn').addEventListener('click', deleteSelected);
  document.getElementById('connectBtn').addEventListener('click', function () { setTool('arrow'); });

  document.getElementById('undoBtn').addEventListener('click', undo);
  document.getElementById('redoBtn').addEventListener('click', redo);
  document.getElementById('dupBtn').addEventListener('click', duplicateSelection);
  document.getElementById('copyBtn').addEventListener('click', copySelection);
  document.getElementById('pasteBtn').addEventListener('click', pasteClipboard);
  document.getElementById('helpBtn').addEventListener('click', toggleShortcuts);
  var themeBtn = document.getElementById('themeToggle');
  if (themeBtn) themeBtn.addEventListener('click', toggleTheme);
  applyTheme((function () {
    try { return localStorage.getItem(THEME_KEY) === 'light' ? 'light' : 'dark'; } catch (e) { return 'dark'; }
  })(), false);
  document.getElementById('zoomIn').addEventListener('click', function () { setZoom((state.spec.zoom || 1) * 1.15); });
  document.getElementById('zoomOut').addEventListener('click', function () { setZoom((state.spec.zoom || 1) / 1.15); });
  document.getElementById('zoomFit').addEventListener('click', function () {
    zoomFit();
  });
  /* Klik angka persen = kembali 100%, sama seperti Excalidraw. */
  document.getElementById('zoomVal').addEventListener('click', function () { setZoom(1); });

  var inspectorBtn = document.getElementById('inspectorToggle');
  if (inspectorBtn) {
    inspectorBtn.addEventListener('click', function () { setInspector(!inspectorOpen); });
  }

  var gridToggleBtn = document.getElementById('gridToggle');
  if (gridToggleBtn) {
    syncGridButton();
    gridToggleBtn.addEventListener('click', function () { toggleGridView(); });
  }

  function download(name, text, type) {
    var blob = new Blob([text], { type: type || 'application/octet-stream' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 2000);
  }

  document.getElementById('exportJson').addEventListener('click', function () {
    download('alur-scene.json', JSON.stringify(state.spec, null, 2), 'application/json');
  });

  document.getElementById('exportSvg').addEventListener('click', function () {
    var svg = stage.querySelector('svg');
    if (!svg) return;
    var clone = svg.cloneNode(true);
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    download('alur-scene.svg', new XMLSerializer().serializeToString(clone), 'image/svg+xml');
  });

  function drawBody() {
    return JSON.stringify(state.spec, null, 2);
  }

  /* The code box holds the fenced block, exactly what read.html eats: what you
     see is what you paste into a .md file. */
  function drawCode() {
    return '```draw\n' + drawBody() + '\n```';
  }

  function drawMarkdown() {
    return drawCode() + '\n';
  }

  /* ------------------------------------------------------- draw code box */

  var codeBox = document.getElementById('drawCode');
  var codeStatusEl = document.getElementById('codeStatus');

  function codeStatus(kind, text) {
    if (!codeStatusEl) return;
    codeStatusEl.className = 'code-status' + (kind ? ' is-' + kind : '');
    codeStatusEl.textContent = text;
  }

  /* Kanvas yang mengubah kode, bukan sebaliknya: isi box hanya disegarkan
     kalau box tidak sedang dipegang pengguna. The box mirrors the canvas
     unless the user is typing in it. */
  function syncDrawCode() {
    if (!codeBox || document.activeElement === codeBox) return;
    var text = drawCode();
    if (codeBox.value === text) return;
    var top = codeBox.scrollTop;
    codeBox.value = text;
    codeBox.scrollTop = top;
    codeBox.classList.remove('is-bad');
  }

  function sceneStats(spec) {
    var s = spec || {};
    var nodes = Array.isArray(s.nodes) ? s.nodes.length : Object.keys(s.nodes || {}).length;
    var edges = Array.isArray(s.edges) ? s.edges.length : Object.keys(s.edges || {}).length;
    return nodes + ' node' + (nodes === 1 ? '' : 's') + ' · ' +
           edges + ' edge' + (edges === 1 ? '' : 's');
  }

  function readCodeBox() {
    var raw = (codeBox.value || '').trim();
    if (!raw) throw new Error('empty');
    /* Terima blok pagar (```draw ... ``` atau ```json ... ```) maupun JSON
       telanjang. Accept a fenced block as well as bare JSON. */
    var fence = /^```[a-zA-Z]*\s*\n([\s\S]*?)\n?```$/.exec(raw);
    if (fence) raw = fence[1].trim();
    var spec;
    try {
      spec = JSON.parse(raw);
    } catch (err) {
      throw new Error('JSON: ' + err.message);
    }
    if (!spec || typeof spec !== 'object' || Array.isArray(spec)) {
      throw new Error('expected a JSON object');
    }

    /* Kanvas menyimpan node sebagai peta {id: node} dan edge sebagai array.
       Keduanya tetap diterima supaya blok dari sumber lain tidak ditolak.
       Nodes are a map, edges an array; both shapes are accepted. */
    if (Array.isArray(spec.nodes)) {
      var map = {};
      spec.nodes.forEach(function (nd, i) {
        if (!nd || typeof nd !== 'object') return;
        var id = nd.id || ('n' + (i + 1));
        nd.id = id;
        map[id] = nd;
      });
      spec.nodes = map;
    }
    if (Array.isArray(spec.edges)) {
      /* sudah benar */
    } else if (spec.edges && typeof spec.edges === 'object') {
      spec.edges = Object.keys(spec.edges).map(function (k) {
        var e = spec.edges[k] || {};
        if (!e.from) e.from = k;
        return e;
      });
    }
    if (!spec.nodes || typeof spec.nodes !== 'object' || Array.isArray(spec.nodes)) {
      throw new Error('nodes must be an object or an array');
    }
    if (!Array.isArray(spec.edges)) throw new Error('edges must be an array');
    return spec;
  }

  function applyCode() {
    if (!codeBox) return false;
    var spec;
    try {
      spec = readCodeBox();
    } catch (err) {
      codeBox.classList.add('is-bad');
      codeStatus('bad', 'Not applied — ' + err.message);
      return false;
    }
    state.spec = spec;
    codeBox.classList.remove('is-bad');
    syncScene();
    syncControls();
    render();
    codeStatus('ok', 'Applied · ' + sceneStats(state.spec));
    return true;
  }

  function revertCode() {
    if (!codeBox) return;
    codeBox.value = drawCode();
    codeBox.classList.remove('is-bad');
    codeStatus('', 'Reverted to the canvas · ' + sceneStats(state.spec));
  }

  /* Copy, never download. The Clipboard API needs a secure context and the
     right permission; when it is missing (or refused) fall back to a hidden
     textarea + execCommand, and only then admit failure. */
  function copyText(text, done) {
    function legacy() {
      try {
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.setAttribute('readonly', '');
        ta.style.cssText = 'position:fixed;top:-1000px;left:-1000px;opacity:0';
        document.body.appendChild(ta);
        ta.select();
        ta.setSelectionRange(0, ta.value.length);
        var ok = document.execCommand('copy');
        document.body.removeChild(ta);
        return !!ok;
      } catch (err) {
        return false;
      }
    }
    function ok() { if (done) done(true); }
    function fail() { if (done) done(false); }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(ok, function () {
        if (legacy()) ok(); else fail();
      });
      return;
    }
    if (legacy()) ok(); else fail();
  }

  function flashLabel(btn, text, restore) {
    if (!btn) return;
    var prev = btn.getAttribute('data-label') || btn.textContent;
    btn.setAttribute('data-label', prev);
    btn.textContent = text;
    setTimeout(function () { btn.textContent = restore || prev; }, 900);
  }

  (function wireCodeBox() {
    if (!codeBox) return;
    var applyBtn = document.getElementById('applyCode');
    var revertBtn = document.getElementById('revertCode');
    var copyBtn = document.getElementById('copyCode');

    if (applyBtn) applyBtn.addEventListener('click', applyCode);
    if (revertBtn) revertBtn.addEventListener('click', revertCode);

    if (copyBtn) copyBtn.addEventListener('click', function () {
      copyText(drawMarkdown(), function (okCopy) {
        flashLabel(copyBtn, okCopy ? 'Copied' : 'Copy failed', 'Copy');
      });
    });

    /* Ctrl+Enter apply, Tab sisip dua spasi (bukan pindah fokus). */
    codeBox.addEventListener('keydown', function (ev) {
      if (ev.key === 'Enter' && (ev.ctrlKey || ev.metaKey)) {
        ev.preventDefault();
        applyCode();
        return;
      }
      if (ev.key === 'Tab') {
        ev.preventDefault();
        var s = codeBox.selectionStart, e = codeBox.selectionEnd;
        codeBox.value = codeBox.value.slice(0, s) + '  ' + codeBox.value.slice(e);
        codeBox.selectionStart = codeBox.selectionEnd = s + 2;
      }
    });

    /* Status jujur: apa yang diketik belum tentu tervalidasi. */
    codeBox.addEventListener('input', function () {
      try {
        var spec = readCodeBox();
        codeBox.classList.remove('is-bad');
        codeStatus('', 'Ready · ' + sceneStats(spec) + ' — press Apply');
      } catch (err) {
        codeBox.classList.add('is-bad');
        codeStatus('bad', err.message);
      }
    });

    codeBox.addEventListener('blur', function () {
      if (codeBox.value.trim() === drawCode().trim()) syncDrawCode();
    });
  })();

  document.getElementById('exportDraw').addEventListener('click', function () {
    download('alur-scene.md', drawMarkdown(), 'text/markdown');
  });

  document.getElementById('copyDraw').addEventListener('click', function () {
    var b = document.getElementById('copyDraw');
    copyText(drawMarkdown(), function (okCopy) {
      flashLabel(b, okCopy ? 'Copied' : 'Copy failed', 'Copy draw');
    });
  });

  function toggleShortcuts() {
    var card = document.getElementById('shortcutCard');
    if (card) card.hidden = !card.hidden;
  }

  document.addEventListener('keydown', function (ev) {
    if (!editor.textEdit || ev.target.id !== 'inlineText') return;
    if (ev.key === 'Enter' && !ev.shiftKey) {
      ev.preventDefault();
      commitTextEdit();
      return;
    }
    if (ev.key === 'Escape') {
      ev.preventDefault();
      cancelTextEdit();
      return;
    }
    if (ev.key === 'Tab') {
      ev.preventDefault();
      var area = ev.target;
      var s = area.selectionStart;
      area.value = area.value.slice(0, s) + '\t' + area.value.slice(area.selectionEnd);
      area.selectionStart = area.selectionEnd = s + 1;
    }
  });

  document.addEventListener('focusout', function (ev) {
    if (ev.target && ev.target.id === 'inlineText') commitTextEdit();
  });

  function adjustFontSize(delta) {
    var ids = selectionIds();
    if (!ids.length) return;
    pushHistory();
    ids.forEach(function (id) {
      var n = state.spec.nodes[id];
      if (!n) return;
      n.fontSize = Math.max(8, Math.min(48, (n.fontSize || 13) + delta));
    });
    touchSpec();
    syncControls();
    render();
  }

  function addLink() {
    var ids = selectionIds();
    if (!ids.length) return;
    var n = state.spec.nodes[ids[0]];
    if (!n) return;
    var url = window.prompt('Link URL', n.link || 'https://');
    if (url === null) return;
    pushHistory();
    n.link = url;
    touchSpec();
    syncControls();
    render();
  }

  function selectionBBox() {
    var ids = selectionIds();
    if (!ids.length) return null;
    var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    ids.forEach(function (id) {
      var n = state.spec.nodes[id];
      if (!n) return;
      var x = n.x || 0, y = n.y || 0;
      var w = n.w || 160, h = n.h || 60;
      minX = Math.min(minX, x);
      minY = Math.min(minY, y);
      maxX = Math.max(maxX, x + w);
      maxY = Math.max(maxY, y + h);
    });
    if (maxX < minX) return null;
    return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
  }

  function zoomToSelection() {
    var bb = selectionBBox();
    if (!bb) { zoomFit(); return; }
    fitBox(bb, 1);
    applyView();
    touchSpec();
    syncControls();
  }

  function zoomFit() {
    var z = fitBox(sceneBounds(state.spec));
    if (z == null) {
      state.spec.zoom = 1;
      state.spec.panX = 0;
      state.spec.panY = 0;
    }
    applyView();
    touchSpec();
    syncControls();
  }

  /* Keyboard pan: a step is in screen pixels, so it feels the same at any zoom. */
  function panPage(dx, dy) {
    var m = viewMetrics();
    state.spec.panX = (state.spec.panX || 0) + (dx * 60) / m.z;
    state.spec.panY = (state.spec.panY || 0) + (dy * 60) / m.z;
    applyView();
    touchSpec();
  }

  function syncGridButton() {
    var btn = document.getElementById('gridToggle');
    if (!btn) return;
    var on = state.spec.grid !== false;
    btn.classList.toggle('is-on', on);
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    btn.title = (on ? 'Hide' : 'Show') + ' grid (Ctrl+\')';
  }

  function toggleGridView() {
    state.spec.grid = state.spec.grid === false;
    syncGridButton();
    syncControls();
    render();
  }

  function toggleViewMode() {
    document.body.classList.toggle('view-mode');
    if (document.body.classList.contains('view-mode')) closePanels();
    syncShapePanel();
  }

  var THEME_KEY = 'ruang.theme.v1';

  function currentTheme() {
    var b = document.body;
    return (b.classList.contains('theme--light') || b.classList.contains('light-theme')) ? 'light' : 'dark';
  }

  function applyTheme(theme, persist) {
    var light = theme === 'light';
    var b = document.body;
    b.classList.toggle('theme--light', light);
    b.classList.toggle('theme--dark', !light);
    b.classList.toggle('light-theme', light);
    b.setAttribute('data-theme', light ? 'light' : 'dark');
    var btn = document.getElementById('themeToggle');
    if (btn) {
      btn.setAttribute('aria-pressed', light ? 'true' : 'false');
      btn.title = light ? 'Switch to dark theme (Alt+Shift+D)' : 'Switch to light theme (Alt+Shift+D)';
      var ico = btn.querySelector('.theme-ico');
      if (ico) ico.textContent = light ? '\u2600' : '\u263e';
    }
    if (persist !== false) {
      try { localStorage.setItem(THEME_KEY, light ? 'light' : 'dark'); } catch (e) {}
    }
  }

  function toggleTheme() {
    applyTheme(currentTheme() === 'light' ? 'dark' : 'light');
  }

  function focusShapeControl(kind) {
    if (!isCanvas()) return;
    var panel = document.getElementById('shapePanel');
    if (panel && panel.hidden) syncShapePanel();
    var target = null;
    if (kind === 'background') {
      var labels = document.querySelectorAll('#shapePanelBody .shape-label');
      for (var i = 0; i < labels.length; i++) {
        if (labels[i].textContent === 'Fill') {
          target = labels[i].parentNode.querySelector('.swatch');
          break;
        }
      }
    } else if (kind === 'font') {
      target = document.querySelector('#shapePanelBody select');
    } else {
      target = document.querySelector('#shapePanelBody .swatch');
    }
    if (target) target.focus();
  }

  function cycleShapeType() {
    var ids = selectionIds();
    if (ids.length !== 1) return;
    var n = state.spec.nodes[ids[0]];
    if (!n) return;
    var order = ['box', 'diamond', 'circle', 'plain'];
    var at = order.indexOf(n.shape || 'box');
    pushHistory();
    n.shape = order[(at + 1) % order.length];
    touchSpec();
    syncControls();
    render();
  }

  function copyStyles() {
    var ids = selectionIds();
    if (!ids.length) return;
    var n = state.spec.nodes[ids[0]];
    editor.clipStyles = {
      color: n.color, fill: n.fill, strokeWidth: n.strokeWidth,
      strokeStyle: n.strokeStyle, fillStyle: n.fillStyle, sloppiness: n.sloppiness,
      edge: n.edge, opacity: n.opacity
    };
  }

  function pasteStyles() {
    if (!editor.clipStyles) return;
    var ids = selectionIds();
    if (!ids.length) return;
    pushHistory();
    ids.forEach(function (id) {
      var n = state.spec.nodes[id];
      if (!n) return;
      Object.keys(editor.clipStyles).forEach(function (k) {
        if (editor.clipStyles[k] !== undefined) n[k] = editor.clipStyles[k];
      });
    });
    touchSpec();
    syncControls();
    render();
  }

  function alignSelection(dir) {
    var ids = selectionIds();
    var bb = selectionBBox();
    if (ids.length < 2 || !bb) return;
    pushHistory();
    ids.forEach(function (id) {
      var n = state.spec.nodes[id];
      if (!n) return;
      if (dir === 'top') n.y = bb.y;
      if (dir === 'bottom') n.y = bb.y + bb.h - (n.h || 60);
      if (dir === 'left') n.x = bb.x;
      if (dir === 'right') n.x = bb.x + bb.w - (n.w || 160);
    });
    touchSpec();
    syncControls();
    render();
  }

  function layerSelection(dir) {
    var ids = selectionIds();
    if (!ids.length) return;
    pushHistory();
    var nodes = state.spec.nodes;
    var copy = {};
    var rest = Object.keys(nodes).filter(function (k) { return ids.indexOf(k) < 0; });
    if (dir === 'front') rest = rest.concat(ids);
    else rest = ids.concat(rest);
    rest.forEach(function (k) { copy[k] = nodes[k]; });
    state.spec.nodes = copy;
    touchSpec();
    syncControls();
    render();
  }

  function resetCanvas() {
    pushHistory();
    state.spec.nodes = {};
    state.spec.edges = [];
    state.spec.drawings = [];
    state.spec.selected = null;
    state.spec.selectedEdge = null;
    state.spec.selectedEdges = [];
    state.spec.selectedDrawing = null;
    touchSpec();
    syncControls();
    syncEditor();
    render();
  }

  function stickyNote() {
    if (!isCanvas()) return;
    var c = viewportSceneCenter();
    var id = addNode('plain', c.x - 80, c.y - 30, 160, 60);
    if (id) setTimeout(function () { startTextEdit(id); }, 0);
  }

  function bucketFill() {
    var ids = selectionIds();
    if (!ids.length) return;
    var fill = (editor.clipStyles && editor.clipStyles.fill) || 'blue';
    pushHistory();
    ids.forEach(function (id) { if (state.spec.nodes[id]) state.spec.nodes[id].fill = fill; });
    touchSpec();
    syncControls();
    render();
  }

  window.addEventListener('keydown', function (ev) {
    var tag = (ev.target.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea' || tag === 'select' || ev.target.isContentEditable) return;
    var k = ev.key.toLowerCase();
    if (ev.key === 'Escape') {
      if (editor.lineChain) { finishLineChain(); return; }
      if (document.body.classList.contains('focus-mode')) { toggleFocus(false); return; }
      var card = document.getElementById('shortcutCard');
      if (card && !card.hidden) { card.hidden = true; return; }
      var openDock = document.querySelector('.dock.is-open');
      if (openDock) { setPanel(openDock.id.replace('panel', '').toLowerCase(), false); return; }
      var shapePanel = document.getElementById('shapePanel');
      if (shapePanel && !shapePanel.hidden) { shapePanel.hidden = true; return; }
      if (selectionIds().length || (state.spec.selectedEdges && state.spec.selectedEdges.length) || state.spec.selectedEdge != null || state.spec.selectedDrawing) {
        setSelection([]);
      }
      return;
    }
    if (!isCanvas()) return;
    if (ev.key === '?') { ev.preventDefault(); toggleShortcuts(); return; }
    if ((ev.ctrlKey || ev.metaKey) && k === 'a') { ev.preventDefault(); selectAllNodes(); return; }
    if (ev.key === 'Delete' || ev.key === 'Backspace') { ev.preventDefault(); deleteSelected(); return; }
    if (ev.key === 'Enter' && !ev.ctrlKey && !ev.metaKey && !ev.shiftKey) {
      var one = selectionIds();
      if (one.length === 1) { ev.preventDefault(); startTextEdit(one[0]); return; }
    }
    if (ev.key === 'Enter' && (ev.ctrlKey || ev.metaKey)) {
      if (state.spec.selectedEdge != null) {
        ev.preventDefault();
        var ce = state.spec.edges && state.spec.edges[state.spec.selectedEdge];
        if (ce && ce.points) {
          state.spec.pointEdit = true;
          render();
        }
      }
      return;
    }
    if ((ev.ctrlKey || ev.metaKey) && ev.altKey && k === 'c') {
      ev.preventDefault(); copyStyles(); return;
    }
    if ((ev.ctrlKey || ev.metaKey) && ev.altKey && k === 'v') {
      ev.preventDefault(); pasteStyles(); return;
    }
    if ((ev.ctrlKey || ev.metaKey) && ev.shiftKey && k === 'v') {
      ev.preventDefault(); pasteClipboard(); return;
    }
    if ((ev.ctrlKey || ev.metaKey) && k === 'z') {
      ev.preventDefault();
      if (ev.shiftKey) redo(); else undo();
      return;
    }
    if ((ev.ctrlKey || ev.metaKey) && k === 'y') { ev.preventDefault(); redo(); return; }
    if ((ev.ctrlKey || ev.metaKey) && k === 'c') { ev.preventDefault(); copySelection(); return; }
    if ((ev.ctrlKey || ev.metaKey) && k === 'v') {
      if (editor.clipboard && editor.clipboard.nodes && editor.clipboard.nodes.length) {
        ev.preventDefault();
        pasteClipboard();
      }
      return;
    }
    if ((ev.ctrlKey || ev.metaKey) && k === 'd') { ev.preventDefault(); duplicateSelection(); return; }
    if ((ev.ctrlKey || ev.metaKey) && ev.shiftKey && k === 'z') { ev.preventDefault(); redo(); return; }
    if ((ev.ctrlKey || ev.metaKey) && k === 'x') {
      ev.preventDefault(); copySelection(); deleteSelected(); return;
    }
    if ((ev.ctrlKey || ev.metaKey) && ev.shiftKey && k === 'v') {
      ev.preventDefault(); pasteClipboard(); return;
    }
    if ((ev.ctrlKey || ev.metaKey) && ev.altKey && k === 'c') {
      ev.preventDefault(); copyStyles(); return;
    }
    if ((ev.ctrlKey || ev.metaKey) && ev.altKey && k === 'v') {
      ev.preventDefault(); pasteStyles(); return;
    }
    if ((ev.ctrlKey || ev.metaKey) && (ev.key === '+' || ev.key === '=' || ev.code === 'NumpadAdd')) {
      ev.preventDefault(); setZoom((state.spec.zoom || 1) * 1.15); return;
    }
    if ((ev.ctrlKey || ev.metaKey) && (ev.key === '-' || ev.code === 'NumpadSubtract')) {
      ev.preventDefault(); setZoom((state.spec.zoom || 1) / 1.15); return;
    }
    if ((ev.ctrlKey || ev.metaKey) && ev.key === '0') { ev.preventDefault(); setZoom(1); return; }
    if (ev.shiftKey && ev.key === '1') { ev.preventDefault(); zoomFit(); return; }
    if ((ev.ctrlKey || ev.metaKey) && ev.key === "'") { ev.preventDefault(); toggleGridView(); return; }
    if ((ev.ctrlKey || ev.metaKey) && k === 'f') {
      ev.preventDefault();
      setPanel('assets', true);
      setTimeout(function () { var s = document.getElementById('logoSearch'); if (s) s.focus(); }, 60);
      return;
    }
    if ((ev.ctrlKey || ev.metaKey) && ev.key === 'Delete') { ev.preventDefault(); resetCanvas(); return; }
    if ((ev.ctrlKey || ev.metaKey) && ev.shiftKey && ev.key === '[') {
      ev.preventDefault(); layerSelection('back'); return;
    }
    if ((ev.ctrlKey || ev.metaKey) && ev.shiftKey && ev.key === ']') {
      ev.preventDefault(); layerSelection('front'); return;
    }
    if ((ev.ctrlKey || ev.metaKey) && ev.key === '[') {
      ev.preventDefault();
      var idsB = selectionIds();
      if (idsB.length === 1) moveNodeLayer(idsB[0], 'back');
      return;
    }
    if ((ev.ctrlKey || ev.metaKey) && ev.key === ']') {
      ev.preventDefault();
      var idsF = selectionIds();
      if (idsF.length === 1) moveNodeLayer(idsF[0], 'front');
      return;
    }
    if ((ev.ctrlKey || ev.metaKey) && ev.shiftKey && ev.key === 'ArrowUp') { ev.preventDefault(); alignSelection('top'); return; }
    if ((ev.ctrlKey || ev.metaKey) && ev.shiftKey && ev.key === 'ArrowDown') { ev.preventDefault(); alignSelection('bottom'); return; }
    if ((ev.ctrlKey || ev.metaKey) && ev.shiftKey && ev.key === 'ArrowLeft') { ev.preventDefault(); alignSelection('left'); return; }
    if ((ev.ctrlKey || ev.metaKey) && ev.shiftKey && ev.key === 'ArrowRight') { ev.preventDefault(); alignSelection('right'); return; }
    if ((ev.ctrlKey || ev.metaKey) && ev.shiftKey && ev.key === '<') { ev.preventDefault(); adjustFontSize(-1); return; }
    if ((ev.ctrlKey || ev.metaKey) && ev.shiftKey && ev.key === '>') { ev.preventDefault(); adjustFontSize(1); return; }
    if (ev.shiftKey && ev.key === '!') { ev.preventDefault(); zoomFit(); return; }
    if (ev.shiftKey && ev.key === '@') { ev.preventDefault(); zoomToSelection(); return; }
    if (ev.key === 'PageUp') {
      ev.preventDefault();
      if (ev.shiftKey) panPage(-4, 0); else panPage(0, -4);
      return;
    }
    if (ev.key === 'PageDown') {
      ev.preventDefault();
      if (ev.shiftKey) panPage(4, 0); else panPage(0, 4);
      return;
    }
    if (ev.altKey && ev.shiftKey && k === 'd') { ev.preventDefault(); toggleTheme(); return; }
    if (ev.altKey && k === 'z') { ev.preventDefault(); toggleViewMode(); return; }
    if (ev.altKey && k === 'r') { ev.preventDefault(); toggleViewMode(); return; }
    if (ev.altKey && k === '/') { ev.preventDefault(); setInspector(true); return; }
    if (ev.altKey && k === 's') {
      ev.preventDefault();
      editor.snap = !editor.snap;
      var snapStatus = document.getElementById('statusTool');
      if (snapStatus) snapStatus.textContent = editor.snap ? 'snap on' : 'snap off';
      setTimeout(function () { if (snapStatus) snapStatus.textContent = 'tool: ' + editor.tool; }, 1200);
      return;
    }
    if (k === 'n') { ev.preventDefault(); stickyNote(); return; }
    if (ev.shiftKey && k === 'f') { ev.preventDefault(); focusShapeControl('font'); return; }
    if (k === 'f') { ev.preventDefault(); addNode('box', viewportSceneCenter().x - 90, viewportSceneCenter().y - 50, 180, 100); return; }
    if (k === 'b') { ev.preventDefault(); bucketFill(); return; }
    if (k === 'i' || k === 's' || k === 'g') {
      ev.preventDefault();
      focusShapeControl(k === 'i' ? 'stroke' : (k === 's' ? 'stroke' : 'background'));
      return;
    }
    /* Tab is left alone so keyboard focus can move through controls. */
    if (ev.key === 'ArrowLeft') {
      ev.preventDefault();
      if (selectionIds().length) nudgeSelection(ev.shiftKey ? -10 : -1, 0);
      else panPage(ev.shiftKey ? -4 : -1, 0);
      return;
    }
    if (ev.key === 'ArrowRight') {
      ev.preventDefault();
      if (selectionIds().length) nudgeSelection(ev.shiftKey ? 10 : 1, 0);
      else panPage(ev.shiftKey ? 4 : 1, 0);
      return;
    }
    if (ev.key === 'ArrowUp') {
      ev.preventDefault();
      if (selectionIds().length) nudgeSelection(0, ev.shiftKey ? -10 : -1);
      else panPage(0, ev.shiftKey ? -4 : -1);
      return;
    }
    if (ev.key === 'ArrowDown') {
      ev.preventDefault();
      if (selectionIds().length) nudgeSelection(0, ev.shiftKey ? 10 : 1);
      else panPage(0, ev.shiftKey ? 4 : 1);
      return;
    }
    var map = {
      v: 'select', '1': 'select',
      h: 'pan',
      r: 'box', '2': 'box',
      d: 'diamond', '3': 'diamond',
      o: 'circle', '4': 'circle',
      a: 'arrow', '5': 'arrow',
      l: 'line', '6': 'line',
      p: 'draw', '7': 'draw',
      t: 'text', '8': 'text',
      '9': 'table',
      e: 'eraser', '0': 'eraser',
      k: 'laser'
    };
    if ((ev.ctrlKey || ev.metaKey) && k === 'k') { ev.preventDefault(); addLink(); return; }
    if (map[k]) { setTool(map[k]); return; }
    if (k === 'q') {
      editor.keepTool = !editor.keepTool;
      var st = document.getElementById('statusTool');
      if (st) st.textContent = editor.keepTool ? 'tool stays active' : 'tool resets after draw';
      setTimeout(function () { if (st) st.textContent = 'tool: ' + editor.tool; }, 1200);
      return;
    }
    if (k === 'y') { togglePanel('layers'); return; }
  });

  window.addEventListener('keydown', function (ev) {
    var typing = isTypingTarget(ev.target);
    if (ev.code === 'Space' && !typing) {
      if (!spaceDown) {
        spaceDown = true;
        stage.style.cursor = 'grab';
      }
      if (ev.target === document.body) ev.preventDefault();
    }
    if (ev.key === 'Escape') {
      if (paletteState.open) { ev.preventDefault(); ev.stopPropagation(); closePalette(); return; }
      if (ctxState.open) { ev.preventDefault(); ev.stopPropagation(); closeCtx(); return; }
    }
    if ((ev.ctrlKey || ev.metaKey) &&
        (ev.key === '/' || (ev.shiftKey && ev.key.toLowerCase() === 'p'))) {
      ev.preventDefault();
      ev.stopPropagation();
      togglePalette();
      return;
    }
    if (ev.key === '/' && !typing) {
      ev.preventDefault();
      ev.stopPropagation();
      openPalette('');
      return;
    }
    if ((ev.ctrlKey || ev.metaKey) && ev.key === '.') {
      ev.preventDefault();
      toggleFocus();
      return;
    }
    if (!typing && !paletteState.open && !isCanvas()) {
      var pk = ev.key.toLowerCase();
      if (pk === 'y') { ev.preventDefault(); togglePanel('layers'); }
      else if (pk === 'l') { ev.preventDefault(); togglePanel('assets'); }
    }
  }, true);

  Array.prototype.forEach.call(document.querySelectorAll('[data-panel]'), function (b) {
    b.addEventListener('click', function () { togglePanel(b.getAttribute('data-panel')); });
  });

  function mobilePanel(name) {
    if (name === 'properties') {
      inspectorOpen = true;
      var current = document.getElementById('shapePanel');
      var wasOpen = !!(current && !current.hidden);
      closePanels();
      if (wasOpen) return;
      syncShapePanel();
      var sp = document.getElementById('shapePanel');
      if (sp && sp.hidden) {
        /* Nothing is selected (or the line/arrow tool intentionally hides the
           inspector): still open a useful sheet instead of a blank panel. */
        sp.hidden = false;
        var sb = document.getElementById('shapePanelBody');
        var st = document.getElementById('shapePanelTitle');
        if (sb && !sb.textContent.trim()) {
          if (st) st.textContent = 'Properties';
          sb.innerHTML = '<p class="hint">Select a node, text, arrow, or drawing on the canvas to edit it.</p>';
        }
      }
      return;
    }
    if (name === 'shortcuts') {
      toggleShortcuts();
      return;
    }
    if (name === 'tools') {
      var toolsEl = document.getElementById('panelTools');
      var toolsOpen = !!(toolsEl && toolsEl.classList.contains('is-open'));
      closePanels();
      if (!toolsOpen) setPanel('tools', true);
      return;
    }
    if (name === 'assets' || name === 'layers') {
      var el = panelEl(name);
      var wasOpen = !!(el && el.classList.contains('is-open'));
      closePanels();
      if (!wasOpen) setPanel(name, true);
      return;
    }
    if (name === 'scene') {
      var sceneEl = document.getElementById('panelScene');
      var sceneOpen = !!(sceneEl && sceneEl.classList.contains('is-open'));
      closePanels();
      if (!sceneOpen) setPanel('scene', true);
      return;
    }
    if (name === 'template') {
      var tplEl = document.getElementById('panelScene');
      var tplOpen = !!(tplEl && tplEl.classList.contains('is-open'));
      closePanels();
      if (!tplOpen) setPanel('scene', true);
      window.setTimeout(function () {
        var t = document.getElementById('preset');
        if (t && t.focus) t.focus();
      }, 80);
      return;
    }
    if (name === 'logos') {
      var lgEl = document.getElementById('panelAssets');
      var lgOpen = !!(lgEl && lgEl.classList.contains('is-open'));
      closePanels();
      if (!lgOpen) setPanel('assets', true);
      return;
    }
    togglePanel(name);
  }  function mobilePanel(name) {
    if (name === 'properties') {
      inspectorOpen = true;
      var current = document.getElementById('shapePanel');
      var wasOpen = !!(current && !current.hidden);
      closePanels();
      if (wasOpen) return;
      syncShapePanel();
      var sp = document.getElementById('shapePanel');
      if (sp && sp.hidden) {
        /* Nothing is selected (or the line/arrow tool intentionally hides the
           inspector): still open a useful sheet instead of a blank panel. */
        sp.hidden = false;
        var sb = document.getElementById('shapePanelBody');
        var st = document.getElementById('shapePanelTitle');
        if (sb && !sb.textContent.trim()) {
          if (st) st.textContent = 'Properties';
          sb.innerHTML = '<p class="hint">Select a node, text, arrow, or drawing on the canvas to edit it.</p>';
        }
      }
      return;
    }
    if (name === 'shortcuts') {
      toggleShortcuts();
      return;
    }
    if (name === 'tools') {
      var toolsEl = document.getElementById('panelTools');
      var toolsOpen = !!(toolsEl && toolsEl.classList.contains('is-open'));
      closePanels();
      if (!toolsOpen) setPanel('tools', true);
      return;
    }
    if (name === 'assets' || name === 'layers') {
      var el = panelEl(name);
      var wasOpen = !!(el && el.classList.contains('is-open'));
      closePanels();
      if (!wasOpen) setPanel(name, true);
      return;
    }
    if (name === 'scene') {
      var sceneEl = document.getElementById('panelScene');
      var sceneOpen = !!(sceneEl && sceneEl.classList.contains('is-open'));
      closePanels();
      if (!sceneOpen) setPanel('scene', true);
      return;
    }
    if (name === 'template') {
      var tplEl = document.getElementById('panelScene');
      var tplOpen = !!(tplEl && tplEl.classList.contains('is-open'));
      closePanels();
      if (!tplOpen) setPanel('scene', true);
      window.setTimeout(function () {
        var t = document.getElementById('preset');
        if (t && t.focus) t.focus();
      }, 80);
      return;
    }
    if (name === 'logos') {
      var lgEl = document.getElementById('panelAssets');
      var lgOpen = !!(lgEl && lgEl.classList.contains('is-open'));
      closePanels();
      if (!lgOpen) setPanel('assets', true);
      return;
    }
    togglePanel(name);
  }

  /* ------------------------------------------------------------------
     Mobile panel system: one dock at a time, opened from the top bar or
     the tab strip. The tool buttons move into the dock on phones so the
     canvas keeps the whole screen. */

  var mobileMq = window.matchMedia('(max-width: 760px)');
  var panelToggleBtn = document.getElementById('panelToggle');
  var mobileTabsBar = document.getElementById('mobileTabs');
  var activePanel = 'tools';

  function toolGridHost() {
    return mobileMq.matches ? document.getElementById('toolGrid') : document.getElementById('editorBar');
  }

  function placeToolButtons() {
    var rail = document.getElementById('editorBar');
    var grid = document.getElementById('toolGrid');
    if (!rail || !grid) return;
    var host = toolGridHost();
    if (!host) return;
    if (host === rail) {
      Array.prototype.slice.call(grid.children).forEach(function (n) { rail.appendChild(n); });
    } else {
      Array.prototype.slice.call(rail.children).forEach(function (n) { grid.appendChild(n); });
    }
    syncStageInsets();
  }

  function highlightTabs(name) {
    if (!mobileTabsBar) return;
    Array.prototype.forEach.call(mobileTabsBar.querySelectorAll('.mtab'), function (b) {
      b.classList.toggle('is-on', b.getAttribute('data-open-panel') === name);
    });
    if (panelToggleBtn) {
      var open = !!document.querySelector('.dock.is-open');
      panelToggleBtn.classList.toggle('is-on', open);
      panelToggleBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
  }

  function openMobilePanel(name) {
    activePanel = name;
    var el = name === 'properties' ? document.getElementById('shapePanel') : panelEl(name);
    var isOpen = !!el && (el.classList.contains('is-open') ||
      (el.id === 'shapePanel' && el.hidden === false));
    if (isOpen) {
      closePanels();
      if (el && el.id === 'shapePanel') el.hidden = true;
      highlightTabs(name);
      return;
    }
    mobilePanel(name);
    window.setTimeout(function () { highlightTabs(name); }, 0);
  }

  if (panelToggleBtn) {
    panelToggleBtn.addEventListener('click', function () {
      if (document.querySelector('.dock.is-open') || (document.getElementById('shapePanel') && !document.getElementById('shapePanel').hidden)) {
        closePanels();
        var sp = document.getElementById('shapePanel');
        if (sp) sp.hidden = true;
        highlightTabs(activePanel);
        return;
      }
      openMobilePanel(activePanel);
    });
  }

  if (mobileTabsBar) {
    mobileTabsBar.addEventListener('click', function (ev) {
      var b = ev.target.closest('[data-open-panel]');
      if (!b) return;
      ev.preventDefault();
      openMobilePanel(b.getAttribute('data-open-panel'));
    });
  }

  if (mobileMq.addEventListener) mobileMq.addEventListener('change', placeToolButtons);
  else if (mobileMq.addListener) mobileMq.addListener(placeToolButtons);
  placeToolButtons();

  function mobileAction(action) {
    switch (action) {
      case 'undo': undo(); break;
      case 'redo': redo(); break;
      case 'duplicate': duplicateSelection(); break;
      case 'copy': copySelection(); break;
      case 'paste': pasteClipboard(); break;
      case 'delete': deleteSelected(); break;
      case 'clear':
        if (window.confirm('Clear all nodes, edges, and drawings?')) resetCanvas();
        break;
      case 'zoom-out': setZoom((state.spec.zoom || 1) / 1.15); break;
      case 'zoom-in': setZoom((state.spec.zoom || 1) * 1.15); break;
      case 'zoom-fit':
        zoomFit();
        break;
      case 'grid': toggleGridView(); break;
      case 'focus': toggleFocus(true); break;
    }
  }

  window.addEventListener('resize', function () {
    syncStageInsets();
  });

  Array.prototype.forEach.call(document.querySelectorAll('[data-close]'), function (b) {
    b.addEventListener('click', function () { setPanel(b.getAttribute('data-close'), false); });
  });

  document.getElementById('shapePanelClose').addEventListener('click', function () {
    setInspector(false);
  });


  Object.keys(PANELS).forEach(initDockDrag);
  Object.keys(PANELS).forEach(initDockResize);

  var docTitle = document.getElementById('docTitle');
  if (docTitle) {
    docTitle.addEventListener('input', function () {
      state.spec.title = docTitle.value.trim() || 'Untitled diagram';
      stage.setAttribute('data-title', state.spec.title);
      touchSpec();
    });
  }

  var paletteInput = document.getElementById('paletteInput');
  if (paletteInput) {
    paletteInput.addEventListener('input', renderPalette);
    paletteInput.addEventListener('keydown', function (ev) {
      ev.stopPropagation();
      if (ev.key === 'ArrowDown') {
        ev.preventDefault();
        paletteState.index = Math.min(paletteState.items.length - 1, paletteState.index + 1);
        highlightPalette();
      } else if (ev.key === 'ArrowUp') {
        ev.preventDefault();
        paletteState.index = Math.max(0, paletteState.index - 1);
        highlightPalette();
      } else if (ev.key === 'Enter') {
        ev.preventDefault();
        runPalette(paletteState.index);
      } else if (ev.key === 'Escape') {
        ev.preventDefault();
        closePalette();
      }
    });
  }

  var paletteBox = document.getElementById('palette');
  if (paletteBox) {
    paletteBox.addEventListener('click', function (ev) {
      if (ev.target === paletteBox) closePalette();
    });
  }

  var ctxMenu = document.getElementById('ctxMenu');
  if (ctxMenu) {
    ctxMenu.addEventListener('click', function (ev) {
      var btn = ev.target.closest ? ev.target.closest('[data-cmd]') : null;
      if (btn) ctxCommand(btn.getAttribute('data-cmd'));
    });
  }

  document.addEventListener('pointerdown', function (ev) {
    if (!ctxState.open) return;
    if (ctxMenu && !ctxMenu.contains(ev.target)) closeCtx();
  }, true);

  stage.addEventListener('contextmenu', function (ev) {
    if (!isCanvas()) return;
    var svg = stage.querySelector('svg');
    if (!svg) return;
    ev.preventDefault();
    ctxState.point = svgPoint(svg, ev);
    openCtx(ev);
  });

  var minimapCollapsed = (function () {
    try { return localStorage.getItem('ruang.minimap.v1') !== 'open'; } catch (err) { return true; }
  })();

  var minimap = document.getElementById('minimapSvg');
  if (minimap) {
    minimap.addEventListener('click', function (ev) {
      if (!isCanvas()) return;
      if (minimapCollapsed) {
        minimapCollapsed = false;
        try { localStorage.setItem('ruang.minimap.v1', 'open'); } catch (err) {}
        minimap.classList.remove('is-collapsed');
        return;
      }
      var rect = minimap.getBoundingClientRect();
      var vb = minimap.viewBox && minimap.viewBox.baseVal;
      if (!rect.width || !rect.height || !vb || !vb.width) return;
      var sx = vb.x + (ev.clientX - rect.left) / rect.width * vb.width;
      var sy = vb.y + (ev.clientY - rect.top) / rect.height * vb.height;
      var m = viewMetrics();
      state.spec.panX = sx - m.vw / 2;
      state.spec.panY = sy - m.vh / 2;
      applyView();
      touchSpec();
    });
  }

  Array.prototype.forEach.call(document.querySelectorAll('#focusMode, #focusModeBottom'), function (btn) {
    btn.addEventListener('click', function () { toggleFocus(true); });
  });
  var focusExit = document.getElementById('focusExit');
  if (focusExit) focusExit.addEventListener('click', function () { toggleFocus(false); });

  window.addEventListener('keyup', function (ev) {
    if (ev.code === 'Space') {
      spaceDown = false;
      stage.style.cursor = '';
    }
  });

  window.addEventListener('pagehide', saveScene);
  window.addEventListener('beforeunload', saveScene);
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden') saveScene();
  });

  window.addEventListener('resize', function () {
    if (window.innerWidth <= 760) {
      Object.keys(PANELS).forEach(function (n) {
        var el = panelEl(n);
        if (el) { el.style.left = ''; el.style.top = ''; el.style.right = ''; }
      });
    }
    Object.keys(PANEL_RESIZABLE).forEach(applyPanelSize);
    if (isCanvas()) applyView();
    else renderMinimap();
  });

  updateHistoryButtons();

  /* Blok yang sedang "dalam konteks": kalau tepat satu blok modul terpilih,
     itulah target panel 4. Kalau tidak, targetnya scene. */
  function focusedBlock() {
    var ids = selectionIds();
    if (ids.length === 1) {
      var n = state.spec.nodes && state.spec.nodes[ids[0]];
      if (n && n.shape === 'module' && n.module) return { module: n.module, node: n, id: ids[0] };
      if (n && n.shape === 'chart') return { module: 'chart', node: n, id: ids[0] };
    }
    return { module: state.spec.module || 'flow', node: null, id: null };
  }

  function syncControls() {
    var s = state.spec;
    var m = s.module || 'flow';
    document.getElementById('module').value = m;
    var fm = focusedBlock();
    var linkSec = document.getElementById('linkSection');
    if (linkSec) linkSec.hidden = !(state.spec.edges || []).length;
    var playSec = document.getElementById('playbackSection');
    if (playSec) {
      var moving = state.spec.motion && state.spec.motion !== 'none';
      playSec.hidden = !moving;
    }

    if (fm.module === 'chart') {
      var ct = document.getElementById('chartType');
      if (ct) {
        var cur = fm.node ? (fm.node.chartType || 'bar') : (s.type || 'bar');
        ct.value = cur;
      }
    }
    var lc = document.getElementById('linkControls');
    if (lc) lc.style.display = (m === 'flow' || m === 'pipeline' || m === 'canvas' || m === 'reverse-proxy' || m === 'graph') ? '' : 'none';
    var cb = document.getElementById('cable');
    if (cb) cb.value = s.cable || 'solid';
    var mo = document.getElementById('motion');
    if (mo) mo.value = s.motion || 'flow';
    var sp = document.getElementById('speed');
    if (sp) sp.value = s.speed || 1;
    var spv = document.getElementById('speedVal');
    if (spv) spv.textContent = (s.speed || 1).toFixed(2).replace(/0$/, '') + '×';
    /* Panel 4 (Chart) ikut berubah setiap kali status diperbarui, termasuk
       setelah render() — supaya daftar "tambah chart" tidak nyangkut. */
    syncChartDataPanel();
    syncLogoPanel();
    syncEditor();
    specBox.value = JSON.stringify(s, null, 2);
  }

  function render() {
    refreshCanvasChartSpecs();
    if (stage.__alur) {
      Alur.destroy(stage.__alur);
      stage.__alur = null;
    }
    stage.innerHTML = '';
    stage.setAttribute('data-module', state.spec.module || 'flow');
    stage.setAttribute('data-spec', JSON.stringify(state.spec));
    stage.removeAttribute('data-ready');
    Alur.mount(stage);
    applyViewNow();
    updateStatus();
    renderLayers();
    syncTitle();
    if (stage.querySelector('svg')) updateSelectionVisual();
    queueSave();
    /* Setiap benda yang masuk/keluar kanvas langsung kelihatan kodenya.
       Every canvas change shows up in the draw block. */
    syncDrawCode();
  }

  function setAllEdges(patch) {
    (state.spec.edges || []).forEach(function (e) {
      Object.keys(patch).forEach(function (k) { e[k] = patch[k]; });
    });
  }

  document.getElementById('module').addEventListener('change', function (ev) {
    /* Hidden legacy switch: it adds the module to the canvas, never swaps it. */
    insertModule(ev.target.value);
    ev.target.value = state.spec.module || 'canvas';
  });

  document.getElementById('chartType').addEventListener('change', function (ev) {
    var val = ev.target.value;
    var fm = focusedBlock();
    /* Ada blok Chart terpilih: ubah blok itu, JANGAN ganti seluruh scene.
       Dulu handler ini menimpa state.spec, jadi canvas terasa "pindah halaman"
       padahal belum ada data yang diisi. */
    if (fm.node) {
      pushHistory();
      fm.node.chartType = val;
      if (fm.node.dataSource !== 'table') {
        var preset = chartPreset(val, fm.node._series || 2, fm.node._points || 7);
        preset._preset = 'custom';
        preset.grid = true;
        fm.node.moduleSpec = preset;
      }
      touchSpec();
      syncControls();
      render();
      return;
    }
    var s = state.spec;
    var spec = chartPreset(val, s._series || 2, s._points || 7);
    spec._preset = 'custom';
    spec.grid = true;
    state.spec = spec;
    syncScene();
    syncControls();
    render();
  });

  document.getElementById('cable').addEventListener('change', function (ev) {
    state.spec.cable = ev.target.value;
    setAllEdges({ cable: ev.target.value });
    syncControls();
    render();
  });

  document.getElementById('motion').addEventListener('change', function (ev) {
    state.spec.motion = ev.target.value;
    setAllEdges({ motion: ev.target.value });
    syncControls();
    render();
  });

  var speedTimer = null;
  document.getElementById('speed').addEventListener('input', function (ev) {
    state.spec.speed = parseFloat(ev.target.value);
    document.getElementById('speedVal').textContent = state.spec.speed.toFixed(2).replace(/0$/, '') + '×';
    specBox.value = JSON.stringify(state.spec, null, 2);
    clearTimeout(speedTimer);
    speedTimer = setTimeout(render, 140);
  });

  document.getElementById('reset').addEventListener('click', function () {
    try { localStorage.removeItem(SAVE_KEY); } catch (err) {}
    state.spec = presetFor(document.getElementById('module').value || 'canvas');
    logoState.target = null;
    logoState.q = '';
    logoState.cat = 'all';
    logoState.limit = 96;
    document.getElementById('logoSearch').value = '';
    syncLogoCats();
    syncControls();
    render();
  });

  /* Import photo / drop / paste ----------------------------------------- */

  document.getElementById('importPhoto').addEventListener('click', function () {
    document.getElementById('photoInput').click();
  });

  document.getElementById('photoInput').addEventListener('change', function (ev) {
    var file = ev.target.files && ev.target.files[0];
    if (file) addImageFile(file);
    ev.target.value = '';
  });

  stage.addEventListener('dragover', function (ev) {
    if (!ev.dataTransfer || Array.prototype.indexOf.call(ev.dataTransfer.types || [], 'Files') < 0) return;
    ev.preventDefault();
    ev.dataTransfer.dropEffect = 'copy';
  });

  stage.addEventListener('drop', function (ev) {
    if (!ev.dataTransfer || !ev.dataTransfer.files || !ev.dataTransfer.files.length) return;
    var file = ev.dataTransfer.files[0];
    if (!/^image\//.test(file.type || '')) return;
    ev.preventDefault();
    addImageFile(file, ev.clientX, ev.clientY);
  });

  document.addEventListener('paste', function (ev) {
    if (isTypingTarget(ev.target)) return;
    if (!ev.clipboardData || !ev.clipboardData.items) return;
    for (var i = 0; i < ev.clipboardData.items.length; i++) {
      var item = ev.clipboardData.items[i];
      if (item.kind === 'file' && /^image\//.test(item.type || '')) {
        ev.preventDefault();
        addImageFile(item.getAsFile());
        return;
      }
    }
  });

  /* Chart data panel ----------------------------------------------------- */

  function applyChartTarget() {
    var fm = focusedBlock();
    var n = fm.node;
    if (!n) return null;
    return n;
  }

  function onChartControlChange() {
    var n = applyChartTarget();
    if (!n) return;
    pushHistory();
    n.dataSource = document.getElementById('chartSource').value;
    if (n.dataSource === 'manual') {
      var db = document.getElementById('chartData');
      n.chartData = db ? db.value : (n.chartData || '');
    }
    n.sourceTable = document.getElementById('chartTable').value || null;
    n.groupBy = document.getElementById('chartGroupBy').value;
    n.agg = document.getElementById('chartAgg').value;
    refreshCanvasChartSpecs();
    touchSpec();
    syncControls();
    render();
  }

  ['chartSource', 'chartTable', 'chartGroupBy', 'chartAgg'].forEach(function (id) {
    var el = document.getElementById(id);
    if (el) el.addEventListener('change', onChartControlChange);
  });
  (function () {
    var db = document.getElementById('chartData');
    if (!db) return;
    db.addEventListener('input', function () {
      var n = applyChartTarget();
      if (!n) return;
      n.chartData = db.value;
      refreshCanvasChartSpecs();
      touchSpec();
      render();
    });
  })();

  /* Logo panel events ---------------------------------------------------- */

  document.getElementById('logoSearch').addEventListener('input', function (ev) {
    logoState.q = ev.target.value;
    logoState.limit = 96;
    renderLogoGrid(true);
  });

  document.getElementById('logoNode').addEventListener('change', function (ev) {
    logoState.target = ev.target.value;
    syncLogoPanel();
  });

  (function syncLogoCount() {
    var count = document.getElementById('logoCount');
    var inline = document.getElementById('logoCountInline');
    var search = document.getElementById('logoSearch');
    if (count) count.textContent = LOGOS.total;
    if (inline) inline.textContent = LOGOS.total;
    if (search) search.placeholder = 'Search ' + LOGOS.total + ' logos — docker, nginx, burp…';
  })();

  syncLogoCats();

  /* Logo grid grows as you scroll; no More button. */
  document.getElementById('logoGrid').addEventListener('scroll', function () {
    var grid = this;
    if (grid.scrollTop + grid.clientHeight < grid.scrollHeight - 48) return;
    var total = LOGOS.search(logoState.q, logoState.cat).length;
    if (logoState.limit >= total) return;
    logoState.limit += 96;
    renderLogoGrid();
  }, { passive: true });

  /* One canvas only. A saved module scene (flow, chart, proxy, pipeline, graph)
     is flattened into plain nodes and edges on load, so the arrow tool and every
     other tool work on every scene, whatever was saved before. */
  (function normalizeScene() {
    var s = state.spec;
    if (!s || s.module === 'canvas') return;
    var flat = materializeScene(s);
    var base = presetFor('canvas');
    base.grid = true;
    base.nodes = flat.nodes;
    base.edges = flat.edges;
    base.drawings = (s.drawings || []).slice();
    if (s.title) base.title = s.title;
    base.zoom = 1;
    base.panX = 0;
    base.panY = 0;
    state.spec = base;
  })();

  Alur.init(document);
  renderBlockList();
  syncScene();
  syncControls();
  syncStageInsets();

  render();
})();
