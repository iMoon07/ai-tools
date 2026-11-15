p = '/home/moon/Projects/imoon07.github.io/draw.html'
s = open(p, encoding='utf-8').read()

old = """    var styleRow = document.createElement('div');
    styleRow.className = 'shape-row';
    [['B', bold, 'bold'], ['I', italic, 'italic']].forEach(function (it) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'ghost' + (it[1] ? ' is-on' : '');
      b.textContent = it[0];
      b.title = it[2];
      b.addEventListener('click', function () {
        updateTextStyle((function () { var p = {}; p[it[2]] = !it[1]; return p; })(), n, isDefault);
      });
      styleRow.appendChild(b);
    });"""

new = """    var styleRow = document.createElement('div');
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
    }));"""

assert s.count(old) == 1, 'style row'
s = s.replace(old, new, 1)

old2 = """    if (value !== before) {
      pushHistory();
      n.label = value;
      touchSpec();
      syncControls();
      syncEditor();
      render();
    }
  }"""
new2 = """    /* Excalidraw: empty text is no text. */
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
        var lines = value.split('\\n').length;
        n.h = Math.max(24, Math.round(lines * fs * lh + 8));
      }
      touchSpec();
      syncControls();
      syncEditor();
      render();
    }
  }"""
assert s.count(old2) == 1, 'commit'
s = s.replace(old2, new2, 1)

open(p, 'w', encoding='utf-8').write(s)
print('draw.html ok')