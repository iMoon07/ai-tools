import io, re, pathlib
p = pathlib.Path('draw.html')
s = p.read_text(encoding='utf-8')

old_start = "  body.light-theme { background: #f6f8fa; color: #111; }"
old_end = "  body.light-theme .alur-grid-major { stroke: #b8c2cf; }"
i = s.index(old_start)
j = s.index(old_end) + len(old_end)
old = s[i:j]

new = """  /* Theme. Excalidraw keeps the light palette as the CSS-variable defaults and
     flips a single class for dark; here the dark palette is the default (the
     editor was built dark first) and `theme--light` swaps the variables. The
     legacy `light-theme` class is still honoured so nothing silently regresses. */
  body.theme--light,
  body.light-theme {
    --bg: #ffffff;
    --surface: rgba(255, 255, 255, 0.94);
    --surface-solid: #ffffff;
    --surface-2: #eef1f5;
    --line: #d0d7de;
    --line-soft: #e4e8ee;
    --text: #1f2328;
    --muted: #57606a;
    --accent: #0969da;
    --accent-soft: rgba(9, 105, 218, 0.12);
    --danger: #cf222e;
    background: var(--bg);
    color: var(--text);
  }
  html:has(body.theme--light),
  html:has(body.light-theme) { background: #f6f8fa; }

  body.theme--light .topbar,
  body.light-theme .topbar,
  body.theme--light .tool-rail,
  body.light-theme .tool-rail,
  body.theme--light .zoom-bar,
  body.light-theme .zoom-bar,
  body.theme--light .dock,
  body.light-theme .dock,
  body.theme--light .shape-panel,
  body.light-theme .shape-panel,
  body.theme--light .shortcut-card,
  body.light-theme .shortcut-card,
  body.theme--light .minimap,
  body.light-theme .minimap {
    background: var(--surface);
    border-color: var(--line);
    color: var(--text);
    box-shadow: 0 18px 44px -34px rgba(15, 23, 42, 0.35);
  }

  body.theme--light #stage,
  body.light-theme #stage { background: #ffffff; }

  body.theme--light input,
  body.light-theme input,
  body.theme--light textarea,
  body.light-theme textarea,
  body.theme--light select,
  body.light-theme select {
    background: #ffffff;
    color: var(--text);
    border-color: var(--line);
  }

  body.theme--light .alur-canvas-node .alur-node-label,
  body.light-theme .alur-canvas-node .alur-node-label,
  body.theme--light .alur-canvas-node .alur-node-sub,
  body.light-theme .alur-canvas-node .alur-node-sub { fill: #111; }
  body.theme--light .alur-canvas-grid circle,
  body.light-theme .alur-canvas-grid circle { fill: #c9d1d9; }
  body.theme--light .alur-grid-minor,
  body.light-theme .alur-grid-minor { stroke: #d0d7de; }
  body.theme--light .alur-grid-major,
  body.light-theme .alur-grid-major { stroke: #b8c2cf; }"""

s = s[:i] + new + s[j:]

# theme toggle button in the topbar, next to the help button
old_help = '  <button id="helpBtn" class="tool" title="Keyboard shortcuts (?)" data-name="Shortcuts (?)" aria-label="Shortcuts">?</button>'
new_help = old_help + '\n  <button id="themeToggle" class="tool" type="button" title="Toggle theme (Alt+Shift+D)" data-name="Toggle theme" aria-label="Toggle theme" aria-pressed="false"><span class="theme-ico" aria-hidden="true">☾</span></button>'
assert old_help in s
s = s.replace(old_help, new_help, 1)

p.write_text(s, encoding='utf-8')
print('css + markup patched')
