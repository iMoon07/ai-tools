import pathlib
p = pathlib.Path('draw.html')
s = p.read_text(encoding='utf-8')

old_toggle = """  function toggleTheme() {
    document.body.classList.toggle('light-theme');
  }"""
new_toggle = """  var THEME_KEY = 'ruang.theme.v1';

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
      if (ico) ico.textContent = light ? '\\u2600' : '\\u263e';
    }
    if (persist !== false) {
      try { localStorage.setItem(THEME_KEY, light ? 'light' : 'dark'); } catch (e) {}
    }
  }

  function toggleTheme() {
    applyTheme(currentTheme() === 'light' ? 'dark' : 'light');
  }"""
assert old_toggle in s
s = s.replace(old_toggle, new_toggle, 1)

old_bind = "  document.getElementById('helpBtn').addEventListener('click', toggleShortcuts);"
new_bind = old_bind + """
  var themeBtn = document.getElementById('themeToggle');
  if (themeBtn) themeBtn.addEventListener('click', toggleTheme);
  applyTheme((function () {
    try { return localStorage.getItem(THEME_KEY) === 'light' ? 'light' : 'dark'; } catch (e) { return 'dark'; }
  })(), false);"""
assert old_bind in s
s = s.replace(old_bind, new_bind, 1)

# no-flash: apply the stored theme as soon as <body> exists
old_body = "<body>\n<div id=\"stage\" class=\"alur\" data-module=\"canvas\" data-editor=\"1\"></div>"
new_body = """<body>
<script>
(function () {
  try {
    if (localStorage.getItem('ruang.theme.v1') === 'light') {
      document.body.classList.add('theme--light', 'light-theme');
      document.body.setAttribute('data-theme', 'light');
    }
  } catch (e) {}
})();
</script>
<div id="stage" class="alur" data-module="canvas" data-editor="1"></div>"""
assert old_body in s
s = s.replace(old_body, new_body, 1)

p.write_text(s, encoding='utf-8')
print('js patched')
