  /* Canvas editor ------------------------------------------------------- */

  var editor = {
    tool: 'select',
    from: null,
    drag: null,
    history: [],
    future: []
  };
  var nodeSeq = 0;
  var drawSeq = 0;

  function isCanvas() { return (state.spec.module || 'flow') === 'canvas'; }

  function closestNode(el) {
    while (el && el !== stage) {
      if (el.classList && el.classList.contains('alur-canvas-node')) return el;
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

  function touchSpec() {
    specBox.value = JSON.stringify(state.spec, null, 2);
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

  function applyView() {
    var svg = stage.querySelector('svg');
    if (!svg) return;
    var W = state.spec.width || 900;
    var H = state.spec.height || 520;
    var z = state.spec.zoom || 1;
    svg.setAttribute('viewBox',
      (state.spec.panX || 0) + ' ' + (state.spec.panY || 0) + ' ' + (W / z) + ' ' + (H / z));
    var zv = document.getElementById('zoomVal');
    if (zv) zv.textContent = Math.round(z * 100) + '%';
  }

  function setZoom(z) {
    state.spec.zoom = Math.max(0.35, Math.min(3, z));
    applyView();
    touchSpec();
  }

  function updateStatus() {
    var counts = document.getElementById('statusCounts');
    var tool = document.getElementById('statusTool');
    var zv = document.getElementById('zoomVal');
    if (counts) {
      var n = Object.keys(state.spec.nodes || {}).length;
      var e = (state.spec.edges || []).length;
      var d = (state.spec.drawings || []).length;
      counts.textContent = n + ' nodes · ' + e + ' edges' + (d ? ' · ' + d + ' drawings' : '');
    }
    if (tool) tool.textContent = 'tool: ' + editor.tool;
    if (zv) zv.textContent = Math.round((state.spec.zoom || 1) * 100) + '%';
  }

  function updateHistoryButtons() {
    var u = document.getElementById('undoBtn');
    var r = document.getElementById('redoBtn');
    if (u) u.disabled = !editor.history.length;
    if (r) r.disabled = !editor.future.length;
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

  function setTool(tool) {
    editor.tool = tool;
    editor.from = null;
    Array.prototype.forEach.call(document.querySelectorAll('[data-tool]'), function (b) {
      b.classList.toggle('is-on', b.getAttribute('data-tool') === tool);
    });
    syncEditor();
  }

  function selectNode(id) {
    state.spec.selected = id || null;
    state.spec.selectedEdge = null;
    state.spec.selectedDrawing = null;
    touchSpec();
    syncEditor();
    render();
  }

  function selectEdge(i) {
    state.spec.selectedEdge = (state.spec.selectedEdge === i) ? null : i;
    state.spec.selected = null;
    state.spec.selectedDrawing = null;
    touchSpec();
    syncEditor();
    render();
  }

  function selectDrawing(id) {
    state.spec.selectedDrawing = (state.spec.selectedDrawing === id) ? null : id;
    state.spec.selected = null;
    state.spec.selectedEdge = null;
    touchSpec();
    syncEditor();
    render();
  }

  function addNode(shape, x, y, w, h) {
    var s = state.spec;
    s.nodes = s.nodes || {};
    var id, n = 1;
    do { id = 'n' + (++nodeSeq); } while (s.nodes[id]);
    s.nodes[id] = {
      id: id,
      x: Math.round(x),
      y: Math.round(y),
      w: Math.round(w),
      h: Math.round(h),
      shape: shape,
      label: shape === 'plain' ? 'Text' : (shape === 'pill' ? 'Box' : shape.charAt(0).toUpperCase() + shape.slice(1)),
      sub: '',
      color: COLOR_KEYS[Object.keys(s.nodes).length % COLOR_KEYS.length]
    };
    s.selected = id;
    s.selectedEdge = null;
    s.selectedDrawing = null;
    touchSpec();
    syncControls();
    syncEditor();
    render();
    if (shape === 'plain') {
      setTimeout(function () {
        var input = document.querySelector('#nodeInspector input');
        if (input) { input.focus(); input.select(); }
      }, 0);
    }
  }

  function deleteSelected() {
    var s = state.spec;
    pushHistory();
    if (s.selectedDrawing) {
      s.drawings = (s.drawings || []).filter(function (d) { return d.id !== s.selectedDrawing; });
      s.selectedDrawing = null;
    } else if (s.selectedEdge != null && s.edges[s.selectedEdge]) {
      s.edges.splice(s.selectedEdge, 1);
      s.selectedEdge = null;
    } else if (s.selected && s.nodes[s.selected]) {
      delete s.nodes[s.selected];
      s.edges = (s.edges || []).filter(function (e) {
        return e.from !== s.selected && e.to !== s.selected;
      });
      s.selected = null;
    }
    touchSpec();
    syncControls();
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

  function renderNodeInspector() {
    var host = document.getElementById('nodeInspector');
    host.innerHTML = '';
    var id = state.spec.selected;
    var n = id && state.spec.nodes[id];
    if (!n) { host.innerHTML = '<p class="hint">No node selected.</p>'; return; }

    host.appendChild(textField('Label', n.label, function (v) { n.label = v; }));
    host.appendChild(textField('Sub', n.sub, function (v) { n.sub = v; }));
    host.appendChild(selectField('Shape', [
      ['box', 'Box'], ['pill', 'Pill'], ['circle', 'Circle'], ['plain', 'Plain (no box)']
    ], n.shape || 'box', function (v) { n.shape = v; }));
    host.appendChild(selectField('Color', COLOR_KEYS.map(function (k) { return [k, k]; }),
      n.color || 'blue', function (v) { n.color = v; }));

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
    host.appendChild(selectField('Color',
      COLOR_KEYS.map(function (k) { return [k, k]; }),
      e.color || 'blue',
      function (v) { e.color = v; }));
    host.appendChild(textField('Label', e.label, function (v) { e.label = v; }));
  }

  function syncEditor() {
    var bar = document.getElementById('editorBar');
    var status = document.getElementById('stageStatus');
    if (bar) bar.style.display = isCanvas() ? '' : 'none';
    if (status) status.style.display = isCanvas() ? '' : 'none';
    var panel = document.getElementById('editorPanel');
    if (panel) panel.style.display = isCanvas() ? '' : 'none';
    updateStatus();
    if (!isCanvas()) return;

    document.getElementById('gridToggle').checked = state.spec.grid !== false;
    document.getElementById('editorMode').textContent = editor.tool;

    var hints = {
      select: 'Drag a node to move it. Use the handles to resize. Click an edge or drawing to select.',
      box: 'Drag on the canvas to draw a box. Click for a default box.',
      round: 'Drag on the canvas to draw a rounded box.',
      circle: 'Drag on the canvas to draw a circle.',
      text: 'Drag or click to place text. Edit the label in the inspector.',
      arrow: 'Drag from one node to another to connect them.',
      draw: 'Drag to sketch a freehand stroke.',
      pan: 'Drag to pan. Use the wheel or +/- to zoom.'
    };
    document.getElementById('editorHint').textContent = hints[editor.tool] || hints.select;

    renderNodeInspector();
    renderEdgeInspector();
  }

  stage.addEventListener('pointerdown', function (ev) {
    if (!isCanvas()) return;
    var svg = stage.querySelector('svg');
    if (!svg) return;
    var p = svgPoint(svg, ev);

    if (editor.tool === 'pan') {
      pushHistory();
      editor.drag = {
        type: 'pan', px: p.x, py: p.y,
        panX: state.spec.panX || 0, panY: state.spec.panY || 0
      };
      ev.preventDefault();
      return;
    }

    if (editor.tool === 'draw') {
      pushHistory();
      var preview = AlurKit.path(overlayLayer(), '', 'alur-preview-path', {
        fill: 'none', stroke: '#e6edf3', 'stroke-width': 2,
        'stroke-linecap': 'round', 'stroke-linejoin': 'round'
      });
      editor.drag = { type: 'draw', points: [[p.x, p.y]], preview: preview };
      ev.preventDefault();
      return;
    }

    if (editor.tool === 'arrow') {
      var arrowNode = closestNode(ev.target);
      if (arrowNode) {
        if (!editor.from) {
          pushHistory();
          editor.from = arrowNode.getAttribute('data-node-id');
          arrowNode.classList.add('is-connect-from');
        } else if (editor.from !== arrowNode.getAttribute('data-node-id')) {
          state.spec.edges = state.spec.edges || [];
          state.spec.edges.push({
            from: editor.from,
            to: arrowNode.getAttribute('data-node-id'),
            cable: state.spec.cable || 'solid',
            motion: state.spec.motion || 'flow'
          });
          editor.from = null;
          touchSpec();
          syncControls();
          syncEditor();
          render();
        }
      }
      ev.preventDefault();
      return;
    }

    if (editor.tool === 'box' || editor.tool === 'round' || editor.tool === 'circle' || editor.tool === 'text') {
      pushHistory();
      var shape = editor.tool === 'round' ? 'pill' : editor.tool;
      var previewRect = AlurKit.rect(overlayLayer(), p.x, p.y, 0, 0, 'alur-preview', {
        fill: 'rgba(88,166,255,0.12)', stroke: '#58a6ff', 'stroke-dasharray': '4 3'
      });
      editor.drag = {
        type: 'create', shape: shape,
        x0: p.x, y0: p.y, x1: p.x, y1: p.y,
        moved: false, preview: previewRect
      };
      ev.preventDefault();
      return;
    }

    /* select tool */
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

    var nodeEl = closestNode(ev.target);
    if (nodeEl) {
      var nid = nodeEl.getAttribute('data-node-id');
      var n = state.spec.nodes[nid];
      if (!n) return;
      pushHistory();
      selectNode(nid);
      var fresh = stage.querySelector('[data-node-id="' + nid + '"]');
      editor.drag = {
        type: 'move', id: nid, el: fresh,
        dx: (n.x || 0) - p.x, dy: (n.y || 0) - p.y
      };
      if (fresh) fresh.classList.add('is-dragging');
      ev.preventDefault();
      return;
    }

    var edgeEl = closestEdge(ev.target);
    if (edgeEl) {
      selectEdge(parseInt(edgeEl.getAttribute('data-edge'), 10));
      ev.preventDefault();
      return;
    }

    var drawEl = closestDrawing(ev.target);
    if (drawEl) {
      selectDrawing(drawEl.getAttribute('data-drawing'));
      ev.preventDefault();
      return;
    }

    selectNode(null);
  });

  window.addEventListener('pointermove', function (ev) {
    if (!editor.drag) return;
    var svg = stage.querySelector('svg');
    if (!svg) return;
    var p = svgPoint(svg, ev);

    if (editor.drag.type === 'pan') {
      state.spec.panX = editor.drag.panX - (p.x - editor.drag.px);
      state.spec.panY = editor.drag.panY - (p.y - editor.drag.py);
      applyView();
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

    if (editor.drag.type === 'create') {
      editor.drag.x1 = p.x;
      editor.drag.y1 = p.y;
      editor.drag.moved = true;
      var x = Math.min(editor.drag.x0, p.x);
      var y = Math.min(editor.drag.y0, p.y);
      var w = Math.abs(p.x - editor.drag.x0);
      var h = Math.abs(p.y - editor.drag.y0);
      if (editor.drag.preview) {
        editor.drag.preview.setAttribute('x', x);
        editor.drag.preview.setAttribute('y', y);
        editor.drag.preview.setAttribute('width', w);
        editor.drag.preview.setAttribute('height', h);
      }
      return;
    }

    if (editor.drag.type === 'move') {
      var n = state.spec.nodes[editor.drag.id];
      if (!n) return;
      n.x = Math.round(p.x + editor.drag.dx);
      n.y = Math.round(p.y + editor.drag.dy);
      if (editor.drag.el) {
        editor.drag.el.setAttribute('transform', 'translate(' + n.x + ' ' + n.y + ')');
      }
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
      rn.x = Math.round(x2);
      rn.y = Math.round(y2);
      rn.w = Math.max(40, Math.round(w2));
      rn.h = Math.max(30, Math.round(h2));
      touchSpec();
      render();
    }
  });

  function endDrag() {
    if (!editor.drag) return;
    var drag = editor.drag;
    editor.drag = null;

    if (drag.type === 'draw') {
      if (drag.preview && drag.preview.parentNode) drag.preview.parentNode.removeChild(drag.preview);
      if (drag.points.length > 1) {
        state.spec.drawings = state.spec.drawings || [];
        state.spec.drawings.push({
          id: 'd' + (++drawSeq),
          d: pointsToPath(drag.points),
          color: '#e6edf3',
          width: 2
        });
      }
    }

    if (drag.type === 'create') {
      if (drag.preview && drag.preview.parentNode) drag.preview.parentNode.removeChild(drag.preview);
      var x = Math.min(drag.x0, drag.x1);
      var y = Math.min(drag.y0, drag.y1);
      var w = Math.abs(drag.x1 - drag.x0);
      var h = Math.abs(drag.y1 - drag.y0);
      if (!drag.moved || w < 16 || h < 12) {
        x = drag.x0;
        y = drag.y0;
        w = 160;
        h = drag.shape === 'plain' ? 40 : 60;
      }
      addNode(drag.shape, x, y, w, h);
      return;
    }

    if (drag.type === 'move' && drag.el) {
      drag.el.classList.remove('is-dragging');
    }

    syncControls();
    syncEditor();
    render();
  }

  window.addEventListener('pointerup', endDrag);
  window.addEventListener('pointercancel', endDrag);

  stage.addEventListener('wheel', function (ev) {
    if (!isCanvas()) return;
    ev.preventDefault();
    var z = (state.spec.zoom || 1) * (ev.deltaY < 0 ? 1.1 : 0.9);
    setZoom(z);
  }, { passive: false });

  Array.prototype.forEach.call(document.querySelectorAll('[data-tool]'), function (b) {
    b.addEventListener('click', function () { setTool(b.getAttribute('data-tool')); });
  });

  document.getElementById('addBox').addEventListener('click', function () {
    pushHistory();
    addNode('box', 90 + Math.random() * 60, 90 + Math.random() * 60, 160, 60);
  });
  document.getElementById('addPlain').addEventListener('click', function () {
    pushHistory();
    addNode('plain', 90 + Math.random() * 60, 90 + Math.random() * 60, 160, 40);
  });
  document.getElementById('addPill').addEventListener('click', function () {
    pushHistory();
    addNode('pill', 90 + Math.random() * 60, 90 + Math.random() * 60, 160, 56);
  });
  document.getElementById('addCircle').addEventListener('click', function () {
    pushHistory();
    addNode('circle', 90 + Math.random() * 60, 90 + Math.random() * 60, 110, 110);
  });
  document.getElementById('deleteBtn').addEventListener('click', deleteSelected);
  document.getElementById('connectBtn').addEventListener('click', function () { setTool('arrow'); });

  document.getElementById('undoBtn').addEventListener('click', undo);
  document.getElementById('redoBtn').addEventListener('click', redo);
  document.getElementById('zoomIn').addEventListener('click', function () { setZoom((state.spec.zoom || 1) * 1.15); });
  document.getElementById('zoomOut').addEventListener('click', function () { setZoom((state.spec.zoom || 1) / 1.15); });
  document.getElementById('zoomFit').addEventListener('click', function () {
    state.spec.zoom = 1;
    state.spec.panX = 0;
    state.spec.panY = 0;
    applyView();
    touchSpec();
  });

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

  document.getElementById('gridToggle').addEventListener('change', function (ev) {
    pushHistory();
    state.spec.grid = ev.target.checked;
    touchSpec();
    render();
  });

  window.addEventListener('keydown', function (ev) {
    if (!isCanvas()) return;
    var tag = (ev.target.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea' || tag === 'select') return;
    var k = ev.key.toLowerCase();
    if (ev.key === 'Escape') { setTool('select'); return; }
    if (ev.key === 'Delete' || ev.key === 'Backspace') { ev.preventDefault(); deleteSelected(); return; }
    if ((ev.ctrlKey || ev.metaKey) && k === 'z') {
      ev.preventDefault();
      if (ev.shiftKey) redo(); else undo();
      return;
    }
    if ((ev.ctrlKey || ev.metaKey) && k === 'y') { ev.preventDefault(); redo(); return; }
    var map = { v: 'select', b: 'box', r: 'round', o: 'circle', t: 'text', a: 'arrow', d: 'draw', h: 'pan' };
    if (map[k]) setTool(map[k]);
  });

  updateHistoryButtons();
