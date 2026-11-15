
(function () {
  'use strict';

  var SAVE_KEY = 'topology.lab.v2';
  var TONES = [
    ['blue', '#58a6ff'], ['green', '#3fb950'], ['amber', '#d29922'],
    ['red', '#f85149'], ['purple', '#bc8cff'], ['cyan', '#39d0d8'],
    ['pink', '#f778ba'], ['slate', '#8b949e']
  ];
  var KINDS = ['process', 'actor', 'store', 'choice', 'out', 'tech', 'host',
    'client', 'server', 'database', 'cloud', 'security', 'network'];

  var PRESETS = [
    {
      id: 'request-response',
      label: 'Request / Response',
      spec: {
        title: 'Request / Response',
        vertical: true,
        columns: [['C'], ['P'], ['K']],
        nodes: {
          C: ['Customer', 'browser', 'customer', 'client', 'https://en.wikipedia.org/wiki/Web_browser'],
          P: ['API', 'node', 'waiter', 'process', 'https://en.wikipedia.org/wiki/Web_server'],
          K: ['Database', 'postgres', 'warehouse', 'database', 'https://en.wikipedia.org/wiki/Database']
        },
        edges: [
          { from: 'C', to: 'P', badge: 'Request', color: 'blue' },
          { from: 'P', to: 'K', badge: 'Query', color: 'cyan' },
          { from: 'K', to: 'P', badge: 'Rows', back: true },
          { from: 'P', to: 'C', badge: 'Response', back: true }
        ],
        legend: { flow: 'Request', back: 'Response' },
        facilitiesLabel: 'On one machine',
        facilities: [['server', 'Core'], ['lock', 'Transport'], ['package', 'Optional']]
      }
    },
    {
      id: 'chain',
      label: 'Linear chain',
      spec: {
        title: 'Linear chain',
        vertical: true,
        columns: [['C'], ['P'], ['K'], ['G']],
        nodes: {
          C: ['Customer', 'Places an order', 'customer', 'actor'],
          P: ['Waiter', 'Takes the order', 'waiter', 'process'],
          K: ['Chef', 'Prepares the order', 'cook', 'process'],
          G: ['Pantry', 'Stores ingredients', 'warehouse', 'store']
        },
        edges: [
          { from: 'C', to: 'P', badge: 'Order' },
          { from: 'P', to: 'K', badge: 'Ticket' },
          { from: 'K', to: 'G', badge: 'Fetch' },
          { from: 'G', to: 'K', badge: 'Items', back: true },
          { from: 'K', to: 'P', badge: 'Dish', back: true },
          { from: 'P', to: 'C', badge: 'Serve', back: true }
        ],
        legend: { flow: 'Request', back: 'Response' }
      }
    },
    {
      id: 'fan',
      label: 'Fan-out grid',
      spec: {
        title: 'Choose a platform',
        vertical: true,
        columns: [['B'], { nodes: ['C', 'D', 'E', 'F'], grid: 2 }, ['I']],
        nodes: {
          B: ['Where to run it?', '', 'git-branch', 'choice'],
          C: ['Bare Metal', 'Own hardware', 'hard-drive', 'host'],
          D: ['Virtual Machine', 'Private room', 'monitor', 'host'],
          E: ['Container', 'Shared kernel', 'si-docker', 'host'],
          F: ['Serverless', 'Per request', 'zap', 'host'],
          I: ['All components', 'Run in one place', 'layers', 'out']
        },
        edges: [
          { from: 'B', to: 'C' }, { from: 'B', to: 'D' },
          { from: 'B', to: 'E' }, { from: 'B', to: 'F' },
          { from: 'C', to: 'I', back: true }, { from: 'D', to: 'I', back: true },
          { from: 'E', to: 'I', back: true }, { from: 'F', to: 'I', back: true }
        ]
      }
    },
    {
      id: 'stack',
      label: 'Stack with logos',
      spec: {
        title: 'Request path',
        vertical: false,
        columns: [['client'], ['edge'], ['app'], ['db']],
        nodes: {
          client: ['Client', 'browser', 'customer', 'client'],
          edge: ['Edge', 'nginx', 'stack:nginx', 'server'],
          app: ['App', 'node', 'programming:nodejs', 'process'],
          db: ['Database', 'postgres', 'stack:postgresql', 'database']
        },
        edges: [
          { from: 'client', to: 'edge', badge: 'TLS', color: 'green', width: 2.5 },
          { from: 'edge', to: 'app', badge: 'proxy_pass' },
          { from: 'app', to: 'db', badge: 'SQL', color: 'amber', dash: 'dashed' }
        ]
      }
    }
  ];

  var state = {
    spec: null,
    sel: null,
    guides: false,
    def: { color: 'blue', width: 2, dash: 'solid', motion: 'flow' }
  };

  var $ = function (id) { return document.getElementById(id); };
  var el = {
    board: $('board'), preview: $('preview'), docTitle: $('docTitle'),
    topStatus: $('topStatus'),
    nodeList: $('nodeList'), edgeList: $('edgeList'), facList: $('facList'),
    specBox: $('specBox'), codeStatus: $('codeStatus'), toast: $('toast'), logoGrid: $('logoGrid'),
    logoSearch: $('logoSearch'), logoCat: $('logoCat'), presetSel: $('presetSel'),
    legendFlow: $('lgFlow'), legendBack: $('lgBack'), defSwatches: $('defSwatches')
  };

  /* ------------------------------------------------------------ helpers */

  function clone(o) { return JSON.parse(JSON.stringify(o)); }

  function uid(prefix) {
    var ids = Object.keys(state.spec.nodes || {});
    var n = 1;
    while (ids.indexOf(prefix + n) >= 0) n++;
    return prefix + n;
  }

  function toneColor(name) {
    for (var i = 0; i < TONES.length; i++) if (TONES[i][0] === name) return TONES[i][1];
    return null;
  }

  function toast(msg) {
    el.toast.textContent = msg;
    el.toast.classList.add('is-on');
    clearTimeout(toast._t);
    toast._t = setTimeout(function () { el.toast.classList.remove('is-on'); }, 1500);
  }

  /* Edge bisa array lama ["A","B","label",true] atau objek baru. Semua kode
     panel memakai objek; normalisasi terjadi sekali saat load/apply.
     Edges may be legacy arrays or objects; the panel only works with objects. */
  function normalizeEdges() {
    var spec = state.spec;
    if (!Array.isArray(spec.edges)) { spec.edges = []; return; }
    spec.edges = spec.edges.map(function (e) {
      if (e && !Array.isArray(e)) {
        if (!e.color) e.color = e.back ? 'green' : 'blue';
        if (e.motion === undefined) e.motion = 'flow';
        return e;
      }
      var back = !!e[3];
      return {
        from: e[0], to: e[1],
        badge: e[2] || '',
        back: back,
        color: back ? 'green' : 'blue',
        width: 2,
        dash: 'solid',
        motion: 'flow'
      };
    });
  }

  function nodeArr(id) {
    var n = state.spec.nodes[id];
    if (!Array.isArray(n)) state.spec.nodes[id] = n = [id, '', 'circle-dot', 'process'];
    return n;
  }

  function rebuildColumns() {
    var spec = state.spec;
    var ids = Object.keys(spec.nodes);
    var groups = [];
    ids.forEach(function (id) {
      var col = Math.max(1, parseInt(spec.nodes[id]._col || 1, 10) || 1);
      while (groups.length < col) groups.push([]);
      groups[col - 1].push(id);
    });
    if (!groups.length) return [['A']];
    spec.columns = groups.map(function (list) {
      if (list.length > 1) {
        var want = parseInt(spec.nodes[list[0]]._grid, 10) || list.length;
        var g = Math.max(2, Math.min(4, list.length, want));
        return { nodes: list, grid: g };
      }
      return [list[0]];
    });
    return spec.columns;
  }

  /* Susun "columns" dari spec yang ditempel. Tanpa ini "columns" (dan "grid")
     dari JSON hilang dan tiap node dapat kolom sendiri. Keep a pasted spec's
     own "columns" and "grid": otherwise every node lands in its own column. */
  function assignColumns(spec) {
    var ids = Object.keys(spec.nodes || {}), seen = {};
    var cols = Array.isArray(spec.columns) ? spec.columns : [];
    if (!cols.length) {
      ids.forEach(function (id, i) { spec.nodes[id]._col = i + 1; delete spec.nodes[id]._grid; });
      return;
    }
    cols.forEach(function (c, i) {
      var list = Array.isArray(c) ? c : (c && Array.isArray(c.nodes) ? c.nodes : null);
      if (!list) return;
      var grid = (!Array.isArray(c) && c && c.grid) ? parseInt(c.grid, 10) || 0 : 0;
      list.forEach(function (id) {
        if (!Object.prototype.hasOwnProperty.call(spec.nodes, id) || seen[id]) return;
        seen[id] = 1;
        spec.nodes[id]._col = i + 1;
        if (grid > 1) spec.nodes[id]._grid = grid;
        else delete spec.nodes[id]._grid;
      });
    });
    var base = cols.length;
    ids.filter(function (id) { return !seen[id]; }).forEach(function (id, i) {
      spec.nodes[id]._col = base + 1 + Math.floor(i / 4);
      delete spec.nodes[id]._grid;
    });
  }

  /* _col hanya untuk editor; columns yang dipublikasikan tetap dari rebuild.
     _col is editor-only; the published columns come from rebuildColumns(). */
  function cleanSpec() {
    var spec = clone(state.spec);
    Object.keys(spec.nodes || {}).forEach(function (id) {
      var n = spec.nodes[id];
      if (n && typeof n === 'object') { delete n._col; delete n._grid; }
    });
    delete spec._col;
    return spec;
  }

  function fence() {
    return '```topology\n' + JSON.stringify(cleanSpec(), null, 2) + '\n```';
  }

  function edgeColor(e) {
    return toneColor(e.color) || (typeof e.color === 'string' && e.color.charAt(0) === '#' ? e.color : '#8b949e');
  }

  /* ------------------------------------------------------------- render */

  function render() {
    var spec = cleanSpec();
    el.preview.innerHTML = '';
    el.preview.className = 'topology';
    delete el.preview.dataset.rendered;
    if (document.activeElement !== el.docTitle) el.docTitle.value = state.spec.title || '';

    var count = Object.keys(state.spec.nodes || {}).length;
    var edgeCount = (state.spec.edges || []).length;
    if (el.topStatus) el.topStatus.textContent = count + ' node · ' + edgeCount + ' edge';
    el.board.classList.toggle('is-empty', count === 0);

    if (count) {
      try { window.Topology.render(el.preview, spec); }
      catch (err) { el.preview.textContent = 'Render error: ' + err.message; }
    }

    var flow = (state.spec.legend && state.spec.legend.flow) || 'Request';
    var back = (state.spec.legend && state.spec.legend.back) || 'Response';
    el.legendFlow.textContent = flow;
    el.legendBack.textContent = back;

    syncPanels();
    queueSave();
  }

  function syncPanels() {
    if (document.activeElement !== el.specBox) el.specBox.value = fence();
    renderNodes();
    renderEdges();
    renderLook();
    highlight();
  }

  /* Sintaks ditulis langsung; kanvas mengikuti selama JSON-nya sah.
     The fence is edited in place — the canvas follows while the JSON parses. */
  function codeStatus(kind, msg) {
    el.codeStatus.className = 'code-status' + (kind ? ' is-' + kind : '');
    el.codeStatus.textContent = msg || '';
  }

  function statusLine() {
    var n = Object.keys(state.spec.nodes || {}).length;
    var e = (state.spec.edges || []).length;
    return 'valid · ' + n + ' node · ' + e + ' edge';
  }

  function stripFence(raw) {
    return String(raw)
      .replace(/^\s*```(?:topology|json)?[ \t]*\r?\n/, '')
      .replace(/\r?\n?```\s*$/, '');
  }

  function liveParse() {
    var next;
    try {
      next = JSON.parse(stripFence(el.specBox.value));
    } catch (err) {
      codeStatus('bad', 'sintaks salah — ' + err.message);
      return false;
    }
    if (!next || typeof next !== 'object' || Array.isArray(next) ||
        !next.nodes || typeof next.nodes !== 'object' || Array.isArray(next.nodes)) {
      codeStatus('bad', 'butuh objek dengan "nodes"');
      return false;
    }

    state.spec = next;
    assignColumns(state.spec);
    normalizeEdges();
    rebuildColumns();
    state.sel = null;

    render();
    codeStatus('ok', statusLine());
    return true;
  }

  function highlight() {
    Array.prototype.forEach.call(el.preview.querySelectorAll('.topo-node'), function (n) {
      n.classList.toggle('is-selected', !!state.sel && n.dataset.node === state.sel);
    });
  }

  /* -------------------------------------------------------------- nodes */

  function renderNodes() {
    var spec = state.spec;
    var ids = Object.keys(spec.nodes);
    el.nodeList.innerHTML = '';

    if (!ids.length) {
      el.nodeList.innerHTML = '<div class="empty">Belum ada node.</div>';
      return;
    }

    ids.forEach(function (id) {
      var n = nodeArr(id);
      var card = document.createElement('div');
      card.className = 'card' + (state.sel === id ? ' is-on' : '');
      card.dataset.node = id;

      var head = document.createElement('div');
      head.className = 'card-head';

      var dot = document.createElement('span');
      dot.className = 'dot';
      dot.style.background = toneColor(n[3]) || '#58a6ff';

      var b = document.createElement('b');
      b.textContent = n[0] || id;

      var idTag = document.createElement('span');
      idTag.className = 'id mono';
      idTag.textContent = id;

      var del = document.createElement('button');
      del.type = 'button';
      del.className = 'btn btn--sm btn--danger btn--icon';
      del.style.marginLeft = 'auto';
      del.textContent = '×';
      del.title = 'Delete node';
      del.addEventListener('click', function () {
        delete state.spec.nodes[id];
        state.spec.edges = state.spec.edges.filter(function (e) {
          return e.from !== id && e.to !== id;
        });
        if (state.sel === id) state.sel = null;
        render();
      });

      head.appendChild(dot);
      head.appendChild(b);
      head.appendChild(idTag);
      head.appendChild(del);
      card.appendChild(head);

      card.addEventListener('click', function (ev) {
        if (ev.target.closest('button')) return;
        state.sel = id;
        render();
      });

      /* Drop logo langsung ke kartu node. */
      card.addEventListener('dragover', function (ev) {
        if (!ev.dataTransfer) return;
        ev.preventDefault();
        card.classList.add('is-drop');
      });
      card.addEventListener('dragleave', function () { card.classList.remove('is-drop'); });
      card.addEventListener('drop', function (ev) {
        ev.preventDefault();
        card.classList.remove('is-drop');
        var logo = ev.dataTransfer.getData('text/x-logo');
        if (!logo) return;
        nodeArr(id)[2] = logo;
        state.sel = id;
        render();
        toast('Logo → ' + id);
      });

      var g2 = document.createElement('div');
      g2.className = 'grid2';

      var lab = document.createElement('label');
      lab.className = 'field';
      lab.innerHTML = '<span>Label</span>';
      var labInp = document.createElement('input');
      labInp.className = 'inp';
      labInp.type = 'text';
      labInp.value = n[0] || '';
      labInp.addEventListener('input', function () { n[0] = labInp.value; render(); });
      lab.appendChild(labInp);
      g2.appendChild(lab);

      var sub = document.createElement('label');
      sub.className = 'field';
      sub.innerHTML = '<span>Sub label</span>';
      var subInp = document.createElement('input');
      subInp.className = 'inp';
      subInp.type = 'text';
      subInp.value = n[1] || '';
      subInp.addEventListener('input', function () { n[1] = subInp.value; render(); });
      sub.appendChild(subInp);
      g2.appendChild(sub);
      card.appendChild(g2);

      var g3 = document.createElement('div');
      g3.className = 'grid3';

      var icon = document.createElement('label');
      icon.className = 'field';
      icon.innerHTML = '<span>Icon</span>';
      var iconInp = document.createElement('input');
      iconInp.className = 'inp mono';
      iconInp.type = 'text';
      iconInp.value = n[2] || '';
      iconInp.placeholder = 'customer / stack:docker';
      iconInp.addEventListener('input', function () { n[2] = iconInp.value; render(); });
      icon.appendChild(iconInp);
      g3.appendChild(icon);

      var kind = document.createElement('label');
      kind.className = 'field';
      kind.innerHTML = '<span>Kind</span>';
      var kindSel = document.createElement('select');
      kindSel.className = 'inp';
      KINDS.forEach(function (k) {
        var o = document.createElement('option');
        o.value = k; o.textContent = k;
        if ((n[3] || 'process') === k) o.selected = true;
        kindSel.appendChild(o);
      });
      kindSel.addEventListener('change', function () { n[3] = kindSel.value; render(); });
      kind.appendChild(kindSel);
      g3.appendChild(kind);

      var col = document.createElement('label');
      col.className = 'field';
      col.innerHTML = '<span>Col</span>';
      var colInp = document.createElement('input');
      colInp.className = 'inp';
      colInp.type = 'number';
      colInp.min = '1';
      colInp.max = '9';
      colInp.value = String(parseInt(n._col || 1, 10));
      colInp.addEventListener('input', function () {
        var col = Math.max(1, parseInt(colInp.value, 10) || 1);
        if (col !== n._col) { delete n._grid; n._col = col; }
        rebuildColumns();
        render();
      });
      col.appendChild(colInp);
      g3.appendChild(col);
      card.appendChild(g3);

      var href = document.createElement('label');
      href.className = 'field';
      href.style.marginBottom = '0';
      href.innerHTML = '<span>Link (opsional)</span>';
      var hrefInp = document.createElement('input');
      hrefInp.className = 'inp';
      hrefInp.type = 'url';
      hrefInp.placeholder = 'https://…';
      hrefInp.value = n[4] || '';
      hrefInp.addEventListener('input', function () {
        if (hrefInp.value) n[4] = hrefInp.value;
        else if (n.length > 4) n.length = 4;
        render();
      });
      href.appendChild(hrefInp);
      card.appendChild(href);

      el.nodeList.appendChild(card);
    });
  }

  /* -------------------------------------------------------------- edges */

  function renderEdges() {
    var spec = state.spec;
    var ids = Object.keys(spec.nodes);
    el.edgeList.innerHTML = '';

    if (!ids.length) {
      el.edgeList.innerHTML = '<div class="empty">Tambah node dulu.</div>';
      return;
    }
    if (!spec.edges.length) {
      el.edgeList.innerHTML = '<div class="empty">Belum ada kabel.</div>';
    }

    spec.edges.forEach(function (e, i) {
      var card = document.createElement('div');
      card.className = 'card';

      var head = document.createElement('div');
      head.className = 'card-head';

      var dot = document.createElement('span');
      dot.className = 'dot';
      dot.style.background = e.back ? '#3fb950' : edgeColor(e);

      var b = document.createElement('b');
      b.textContent = e.back ? 'Back' : 'Flow';

      var del = document.createElement('button');
      del.type = 'button';
      del.className = 'btn btn--sm btn--danger btn--icon';
      del.style.marginLeft = 'auto';
      del.textContent = '×';
      del.addEventListener('click', function () {
        spec.edges.splice(i, 1);
        render();
      });

      head.appendChild(dot);
      head.appendChild(b);
      head.appendChild(del);
      card.appendChild(head);

      /* from -> to */
      var line = document.createElement('div');
      line.className = 'edge-line';

      [['From', 'from'], ['To', 'to']].forEach(function (pair) {
        var lab = document.createElement('label');
        lab.className = 'field';
        lab.style.margin = '0';
        lab.innerHTML = '<span>' + pair[0] + '</span>';
        var sel = document.createElement('select');
        sel.className = 'inp';
        ids.forEach(function (id) {
          var o = document.createElement('option');
          o.value = id; o.textContent = id;
          if (e[pair[1]] === id) o.selected = true;
          sel.appendChild(o);
        });
        sel.addEventListener('change', function () { e[pair[1]] = sel.value; render(); });
        lab.appendChild(sel);
        line.appendChild(lab);
        if (pair[1] === 'from') {
          var arw = document.createElement('div');
          arw.className = 'arw';
          arw.textContent = e.back ? '←' : '→';
          line.appendChild(arw);
        }
      });
      card.appendChild(line);

      var badge = document.createElement('label');
      badge.className = 'field';
      badge.style.marginTop = '8px';
      badge.innerHTML = '<span>Label / konteks</span>';
      var badgeInp = document.createElement('input');
      badgeInp.className = 'inp';
      badgeInp.type = 'text';
      badgeInp.placeholder = e.back ? 'Response' : 'Request';
      badgeInp.value = e.badge || '';
      badgeInp.addEventListener('input', function () {
        if (badgeInp.value) e.badge = badgeInp.value;
        else delete e.badge;
        render();
      });
      badge.appendChild(badgeInp);
      card.appendChild(badge);

      /* color + width */
      var sw = document.createElement('div');
      sw.className = 'field';
      var swHead = document.createElement('span');
      swHead.textContent = 'Warna kabel';
      sw.appendChild(swHead);
      var swWrap = document.createElement('div');
      swWrap.className = 'swatches';

      TONES.forEach(function (t) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'sw' + ((e.color || '') === t[0] ? ' is-on' : '');
        btn.style.background = t[1];
        btn.style.color = t[1];
        btn.title = t[0];
        btn.addEventListener('click', function () {
          if (e.color === t[0]) delete e.color;
          else e.color = t[0];
          render();
        });
        swWrap.appendChild(btn);
      });

      var none = document.createElement('button');
      none.type = 'button';
      none.className = 'sw sw--none' + (!e.color ? ' is-on' : '');
      none.title = 'Auto (biru/hijau)';
      none.addEventListener('click', function () { delete e.color; render(); });
      swWrap.appendChild(none);

      sw.appendChild(swWrap);
      card.appendChild(sw);

      var g3 = document.createElement('div');
      g3.className = 'grid3';

      var wLab = document.createElement('label');
      wLab.className = 'field';
      wLab.style.margin = '0';
      wLab.innerHTML = '<span>Tebal</span>';
      var wInp = document.createElement('input');
      wInp.className = 'inp';
      wInp.type = 'number';
      wInp.min = '1';
      wInp.max = '8';
      wInp.step = '0.5';
      wInp.value = String(e.width || 2);
      wInp.addEventListener('input', function () {
        var v = parseFloat(wInp.value);
        if (v > 0) e.width = v; else delete e.width;
        render();
      });
      wLab.appendChild(wInp);
      g3.appendChild(wLab);

      var dLab = document.createElement('label');
      dLab.className = 'field';
      dLab.style.margin = '0';
      dLab.innerHTML = '<span>Gaya</span>';
      var dSel = document.createElement('select');
      dSel.className = 'inp';
      ['solid', 'dashed', 'dotted', 'dash'].forEach(function (d) {
        var o = document.createElement('option');
        o.value = d; o.textContent = d;
        if ((e.dash || 'solid') === d) o.selected = true;
        dSel.appendChild(o);
      });
      dSel.addEventListener('change', function () {
        if (dSel.value === 'solid') delete e.dash;
        else e.dash = dSel.value;
        render();
      });
      dLab.appendChild(dSel);
      g3.appendChild(dLab);

      var mLab = document.createElement('label');
      mLab.className = 'field';
      mLab.style.margin = '0';
      mLab.innerHTML = '<span>Motion</span>';
      var mSel = document.createElement('select');
      mSel.className = 'inp';
      [['flow', 'flow'], ['none', 'none']].forEach(function (m) {
        var o = document.createElement('option');
        o.value = m[0]; o.textContent = m[1];
        if ((e.motion || 'flow') === m[0]) o.selected = true;
        mSel.appendChild(o);
      });
      mSel.addEventListener('change', function () {
        if (mSel.value === 'flow') delete e.motion;
        else e.motion = mSel.value;
        render();
      });
      mLab.appendChild(mSel);
      g3.appendChild(mLab);
      card.appendChild(g3);

      var backRow = document.createElement('label');
      backRow.className = 'switch';
      backRow.style.marginTop = '9px';
      var cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.checked = !!e.back;
      cb.addEventListener('change', function () {
        if (cb.checked) { e.back = true; if (!e.color || e.color === 'blue') e.color = 'green'; }
        else { delete e.back; if (e.color === 'green') delete e.color; }
        render();
      });
      backRow.appendChild(cb);
      backRow.appendChild(document.createTextNode('Jalur balik (response)'));
      card.appendChild(backRow);

      el.edgeList.appendChild(card);
    });
  }

  /* --------------------------------------------------------------- look */

  function renderLook() {
    var spec = state.spec;
    if (document.activeElement !== $('fTitle')) $('fTitle').value = spec.title || '';
    Array.prototype.forEach.call($('fVertical').children, function (b) {
      var on = spec.vertical === false ? b.dataset.v === '0' : b.dataset.v === '1';
      b.classList.toggle('is-on', on);
    });
    $('fBadges').checked = spec.badges !== false;
    if (document.activeElement !== $('fFlow')) $('fFlow').value = (spec.legend && spec.legend.flow) || '';
    if (document.activeElement !== $('fBack')) $('fBack').value = (spec.legend && spec.legend.back) || '';
    if (document.activeElement !== $('fFacLabel')) $('fFacLabel').value = spec.facilitiesLabel || '';

    var facs = Array.isArray(spec.facilities) ? spec.facilities : [];
    el.facList.innerHTML = '';
    if (!facs.length) el.facList.innerHTML = '<div class="empty">Belum ada chip.</div>';

    facs.forEach(function (f, i) {
      var icon = Array.isArray(f) ? f[0] : '';
      var label = Array.isArray(f) ? f[1] : f;
      var row = document.createElement('div');
      row.className = 'row';

      var ic = document.createElement('input');
      ic.className = 'inp mono';
      ic.style.flex = '0 0 96px';
      ic.placeholder = 'server';
      ic.value = icon;
      ic.addEventListener('input', function () {
        state.spec.facilities[i] = [ic.value, lab.value];
        render();
      });

      var lab = document.createElement('input');
      var labInp = document.createElement('input');
      labInp.className = 'inp';
      labInp.placeholder = 'Core';
      labInp.value = label;
      labInp.addEventListener('input', function () {
        state.spec.facilities[i] = [ic.value, labInp.value];
        render();
      });
      lab.appendChild(labInp);

      var del = document.createElement('button');
      del.type = 'button';
      del.className = 'btn btn--sm btn--danger btn--icon';
      del.textContent = '×';
      del.addEventListener('click', function () {
        state.spec.facilities.splice(i, 1);
        render();
      });

      row.appendChild(ic);
      row.appendChild(labInp);
      row.appendChild(del);
      el.facList.appendChild(row);
    });

    /* default cable swatches */
    if (!el.defSwatches.childElementCount) {
      TONES.forEach(function (t) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'sw';
        btn.style.background = t[1];
        btn.style.color = t[1];
        btn.title = t[0];
        btn.dataset.tone = t[0];
        btn.addEventListener('click', function () {
          state.def.color = t[0];
          paintDefaults();
        });
        el.defSwatches.appendChild(btn);
      });
    }
    paintDefaults();
  }

  function paintDefaults() {
    Array.prototype.forEach.call(el.defSwatches.children, function (b) {
      b.classList.toggle('is-on', b.dataset.tone === state.def.color);
    });
    $('defWidth').value = String(state.def.width);
    $('defDash').value = state.def.dash;
    $('defMotion').value = state.def.motion;
  }

  /* -------------------------------------------------------------- logos */

  function renderLogos() {
    if (!window.AlurLogos) return;
    var sel = el.logoCat;
    if (!sel.options.length) {
      var all = document.createElement('option');
      all.value = 'all';
      all.textContent = 'All · ' + AlurLogos.total;
      sel.appendChild(all);
      AlurLogos.categories().forEach(function (c) {
        var o = document.createElement('option');
        o.value = c.id;
        o.textContent = c.label + ' · ' + c.count;
        sel.appendChild(o);
      });
    }

    el.logoGrid.innerHTML = '';
    AlurLogos.search(el.logoSearch.value, sel.value).slice(0, 300).forEach(function (entry) {
      var tile = document.createElement('div');
      tile.className = 'tile';
      tile.draggable = true;
      tile.title = entry.id + ' — drag to a node';

      var res = AlurLogos.resolve(entry.id);
      if (res && res.kind === 'file') {
        var img = document.createElement('img');
        img.src = res.href;
        img.alt = entry.name;
        img.loading = 'lazy';
        img.draggable = false;
        tile.appendChild(img);
      } else if (res && res.kind === 'sprite') {
        tile.innerHTML = '<svg viewBox="0 0 24 24"><use href="' + res.ref + '"></use></svg>';
      }

      tile.addEventListener('dragstart', function (ev) {
        ev.dataTransfer.setData('text/x-logo', entry.id);
        ev.dataTransfer.setData('text/plain', entry.id);
        ev.dataTransfer.effectAllowed = 'copy';
      });

      tile.addEventListener('click', function () {
        if (!state.sel) { toast('Pilih node dulu'); return; }
        nodeArr(state.sel)[2] = entry.id;
        render();
        toast('Logo → ' + state.sel);
      });

      el.logoGrid.appendChild(tile);
    });
  }

  /* --------------------------------------------------------- drag target */

  function wirePreviewDrop() {
    el.preview.addEventListener('dragover', function (ev) {
      var node = ev.target.closest && ev.target.closest('.topo-node');
      if (!node) return;
      ev.preventDefault();
      if (ev.dataTransfer) ev.dataTransfer.dropEffect = 'copy';
      Array.prototype.forEach.call(el.preview.querySelectorAll('.topo-node'), function (n) {
        n.classList.toggle('is-drop', n === node);
      });
    });

    el.preview.addEventListener('dragleave', function (ev) {
      var node = ev.target.closest && ev.target.closest('.topo-node');
      if (node) node.classList.remove('is-drop');
    });

    el.preview.addEventListener('drop', function (ev) {
      var node = ev.target.closest && ev.target.closest('.topo-node');
      if (!node) return;
      ev.preventDefault();
      var logo = ev.dataTransfer.getData('text/x-logo') || ev.dataTransfer.getData('text/plain');
      node.classList.remove('is-drop');
      if (!logo) return;
      var id = node.dataset.node;
      if (!id || !state.spec.nodes[id]) return;
      nodeArr(id)[2] = logo;
      state.sel = id;
      render();
      toast('Logo → ' + id);
    });
  }

  /* --------------------------------------------------------------- save */

  function queueSave() {
    clearTimeout(queueSave._t);
    queueSave._t = setTimeout(function () {
      try { localStorage.setItem(SAVE_KEY, JSON.stringify(cleanSpec())); } catch (err) {}
    }, 300);
  }

  function loadInitial() {
    var spec = null;
    try {
      var raw = localStorage.getItem(SAVE_KEY);
      if (raw) spec = JSON.parse(raw);
    } catch (err) {}
    if (!spec || !spec.nodes) spec = clone(PRESETS[0].spec);

    state.spec = spec;
    assignColumns(spec);
    normalizeEdges();
  }

  /* ------------------------------------------------------------- events */

  var PANE_SIDE = { nodes: 'bottom', edges: 'bottom', logos: 'bottom', look: 'right', json: 'right' };
  var PANE_TITLE = { nodes: 'Nodes', edges: 'Edges', logos: 'Logos', look: 'Look', json: 'Topology' };

  function setPane(name) {
    var dock = $('dock');
    var same = dock.classList.contains('is-open') && dock.dataset.pane === name;
    var next = same ? null : name;

    Array.prototype.forEach.call(document.querySelectorAll('.dock-tab'), function (t) {
      t.classList.toggle('is-on', t.dataset.pane === next);
    });
    Array.prototype.forEach.call(document.querySelectorAll('.pane'), function (p) {
      p.classList.toggle('is-on', p.dataset.pane === next);
    });

    dock.classList.toggle('is-open', !!next);
    dock.dataset.pane = next || '';
    dock.dataset.side = next ? PANE_SIDE[next] : 'bottom';
    if (next) {
      $('dockTitle').textContent = PANE_TITLE[next] || next;
      if (next === 'logos') renderLogos();
      if (next === 'json') {
        el.specBox.value = fence();
        codeStatus('ok', statusLine());
      }
    }
    syncStageInsets();
  }

  function syncStageInsets() {
    var stage = $('stage'), dock = $('dock');
    if (!stage || !dock) return;
    if (!dock.classList.contains('is-open')) {
      stage.style.right = '';
      stage.style.bottom = '';
      return;
    }
    var r = dock.getBoundingClientRect();
    var vw = window.innerWidth, vh = window.innerHeight;
    if (!r.width || !r.height) { stage.style.right = ''; stage.style.bottom = ''; return; }
    if (dock.dataset.side === 'right') {
      stage.style.right = Math.round(Math.max(0, Math.min(vw - r.left + 10, vw * 0.45))) + 'px';
      stage.style.bottom = '';
    } else {
      stage.style.bottom = Math.round(Math.max(0, Math.min(vh - r.top + 10, vh * 0.55))) + 'px';
      stage.style.right = '';
    }
  }

  Array.prototype.forEach.call(document.querySelectorAll('.dock-tab'), function (tab) {
    tab.addEventListener('click', function () { setPane(tab.dataset.pane); });
  });

  $('dockClose').addEventListener('click', function () { setPane(null); });

  (function () {
    var head = $('dockHead'), dock = $('dock'), sx = 0, sy = 0, ox = 0, oy = 0, on = false;

    head.addEventListener('pointerdown', function (ev) {
      if (ev.target.closest('button')) return;
      var r = dock.getBoundingClientRect();
      on = true;
      sx = ev.clientX; sy = ev.clientY; ox = r.left; oy = r.top;
      dock.style.left = ox + 'px';
      dock.style.top = oy + 'px';
      dock.style.right = 'auto';
      dock.style.bottom = 'auto';
      dock.classList.add('is-dragging');
      document.body.classList.add('is-panel-dragging');
      head.setPointerCapture(ev.pointerId);
    });

    head.addEventListener('pointermove', function (ev) {
      if (!on) return;
      var w = dock.offsetWidth, h = dock.offsetHeight;
      var x = Math.max(4, Math.min(window.innerWidth - w - 4, ox + ev.clientX - sx));
      var y = Math.max(58, Math.min(window.innerHeight - h - 4, oy + ev.clientY - sy));
      dock.style.left = x + 'px';
      dock.style.top = y + 'px';
    });

    function end(ev) {
      if (!on) return;
      on = false;
      dock.classList.remove('is-dragging');
      document.body.classList.remove('is-panel-dragging');
      try { head.releasePointerCapture(ev.pointerId); } catch (e) {}
      syncStageInsets();
    }
    head.addEventListener('pointerup', end);
    head.addEventListener('pointercancel', end);
  })();

  (function () {
    var grip = $('dockResize'), dock = $('dock'), sx = 0, sy = 0, ow = 0, oh = 0, on = false;

    grip.addEventListener('pointerdown', function (ev) {
      ev.preventDefault();
      on = true;
      sx = ev.clientX; sy = ev.clientY;
      ow = dock.offsetWidth; oh = dock.offsetHeight;
      dock.style.width = ow + 'px';
      dock.style.height = oh + 'px';
      dock.style.maxHeight = 'none';
      dock.classList.add('is-dragging');
      grip.setPointerCapture(ev.pointerId);
    });

    grip.addEventListener('pointermove', function (ev) {
      if (!on) return;
      var w = Math.max(300, Math.min(window.innerWidth - 24, ow + ev.clientX - sx));
      var h = Math.max(170, Math.min(window.innerHeight - 160, oh + ev.clientY - sy));
      dock.style.width = w + 'px';
      dock.style.height = h + 'px';
    });

    function end(ev) {
      if (!on) return;
      on = false;
      dock.classList.remove('is-dragging');
      try { grip.releasePointerCapture(ev.pointerId); } catch (e) {}
      syncStageInsets();
    }
    grip.addEventListener('pointerup', end);
    grip.addEventListener('pointercancel', end);
  })();

  window.addEventListener('resize', function () { syncStageInsets(); });

  PRESETS.forEach(function (p) {
    var o = document.createElement('option');
    o.value = p.id;
    o.textContent = p.label;
    el.presetSel.appendChild(o);
  });

  el.presetSel.addEventListener('change', function () {
    var p = PRESETS.filter(function (x) { return x.id === el.presetSel.value; })[0];
    el.presetSel.value = '';
    if (!p) return;
    var n = Object.keys(state.spec.nodes || {}).length;
    if (n > 1 && !confirm('Replace the current diagram (' + n + ' nodes) with "' + p.label + '"?')) return;
    state.spec = clone(p.spec);
    state.sel = null;
    assignColumns(state.spec);
    normalizeEdges();
    render();
    toast(p.label);
  });

  $('addNode').addEventListener('click', function () {
    var id = uid('N');
    state.spec.nodes[id] = [id, 'Sub label', 'circle-dot', 'process'];
    state.spec.nodes[id]._col = 1;
    rebuildColumns();
    state.sel = id;
    render();
  });

  $('addEdge').addEventListener('click', function () {
    var ids = Object.keys(state.spec.nodes);
    if (ids.length < 2) { toast('Butuh minimal dua node'); return; }
    state.spec.edges.push({
      from: ids[0],
      to: ids[1],
      color: state.def.color,
      width: state.def.width,
      dash: state.def.dash === 'solid' ? undefined : state.def.dash,
      motion: state.def.motion === 'flow' ? undefined : state.def.motion
    });
    var e = state.spec.edges[state.spec.edges.length - 1];
    if (e.dash === undefined) delete e.dash;
    if (e.motion === undefined) delete e.motion;
    render();
  });

  $('addFac').addEventListener('click', function () {
    state.spec.facilities = state.spec.facilities || [];
    state.spec.facilities.push(['circle-dot', 'Chip']);
    render();
  });

  function setTitle(v) {
    if (v) state.spec.title = v;
    else delete state.spec.title;
    if (document.activeElement !== el.docTitle) el.docTitle.value = state.spec.title || '';
    if (document.activeElement !== $('fTitle')) $('fTitle').value = state.spec.title || '';
    queueSave();
  }

  el.docTitle.addEventListener('input', function () { setTitle(el.docTitle.value); });

  $('fTitle').addEventListener('input', function (e) {
    setTitle(e.target.value);
    render();
  });

  Array.prototype.forEach.call($('fVertical').children, function (b) {
    b.addEventListener('click', function () {
      state.spec.vertical = b.dataset.v !== '0';
      render();
    });
  });

  $('fBadges').addEventListener('change', function (e) {
    state.spec.badges = e.target.checked;
    render();
  });

  function setLegend(which, value) {
    state.spec.legend = state.spec.legend || {};
    if (value) state.spec.legend[which] = value;
    else delete state.spec.legend[which];
    render();
  }

  $('fFlow').addEventListener('input', function (e) { setLegend('flow', e.target.value); });
  $('fBack').addEventListener('input', function (e) { setLegend('back', e.target.value); });

  /* Terapkan konteks ke semua kabel: ini yang membuat "Request/Response" jadi
     label nyata di tiap kabel, bukan cuma legenda.
     Apply the context to every cable so Request/Response becomes a real label
     on each edge, not just a legend. */
  $('applyCtx').addEventListener('click', function () {
    var flow = ($('fFlow').value || '').trim();
    var back = ($('fBack').value || '').trim();
    if (!flow && !back) { toast('Isi label dulu'); return; }
    state.spec.edges.forEach(function (e) {
      var label = e.back ? back : flow;
      if (label) e.badge = label;
      else delete e.badge;
    });
    render();
    toast('Konteks diterapkan ke ' + state.spec.edges.length + ' kabel');
  });

  $('clearCtx').addEventListener('click', function () {
    state.spec.edges.forEach(function (e) { delete e.badge; });
    render();
    toast('Label kabel dikosongkan');
  });

  $('defWidth').addEventListener('input', function (e) {
    state.def.width = parseFloat(e.target.value) || 2;
  });
  $('defDash').addEventListener('change', function (e) { state.def.dash = e.target.value; });
  $('defMotion').addEventListener('change', function (e) { state.def.motion = e.target.value; });

  $('fFacLabel').addEventListener('input', function (e) {
    if (e.target.value) state.spec.facilitiesLabel = e.target.value;
    else delete state.spec.facilitiesLabel;
    render();
  });

  var codeTimer = null;

  el.specBox.addEventListener('input', function () {
    clearTimeout(codeTimer);
    codeTimer = setTimeout(liveParse, 220);
  });

  el.specBox.addEventListener('blur', function () {
    clearTimeout(codeTimer);
    if (liveParse()) el.specBox.value = fence();
  });

  el.specBox.addEventListener('keydown', function (e) {
    if (e.key === 'Tab') {
      e.preventDefault();
      var s = this.selectionStart, t = this.selectionEnd;
      this.value = this.value.slice(0, s) + '  ' + this.value.slice(t);
      this.selectionStart = this.selectionEnd = s + 2;
      clearTimeout(codeTimer);
      liveParse();
    }
  });

  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); toast('Tersalin ```topology'); }
    catch (err) { toast('Gagal menyalin — pakai Export'); }
    document.body.removeChild(ta);
  }

  function copyFence() {
    var text = fence();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(
        function () { toast('Tersalin ```topology'); },
        function () { fallbackCopy(text); });
    } else {
      fallbackCopy(text);
    }
  }

  $('copyBtn').addEventListener('click', copyFence);

  $('exportBtn').addEventListener('click', function () {
    var blob = new Blob([fence() + '\n'], { type: 'text/markdown' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'topology.md';
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
    toast('Export topology.md');
  });

  $('guidesBtn').addEventListener('click', function (e) {
    state.guides = !state.guides;
    $('stage').classList.toggle('is-guides', state.guides);
    e.currentTarget.textContent = 'Guides: ' + (state.guides ? 'on' : 'off');
    e.currentTarget.classList.toggle('is-on', state.guides);
  });

  el.logoSearch.addEventListener('input', renderLogos);
  el.logoCat.addEventListener('change', renderLogos);

  el.preview.addEventListener('click', function (e) {
    var card = e.target.closest && e.target.closest('.topo-node');
    if (!card) return;
    state.sel = card.dataset.node || null;
    render();
  });

  /* ----------------------------------------------------------- bootstrap */

  loadInitial();
  rebuildColumns();
  render();
  renderLogos();
  wirePreviewDrop();
  paintDefaults();

  var rt;
  window.addEventListener('resize', function () {
    clearTimeout(rt);
    rt = setTimeout(render, 200);
  });
})();
