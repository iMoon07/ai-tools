p = '/home/moon/Projects/imoon07.github.io/draw.html'
s = open(p, encoding='utf-8').read()

helper = """  /* Copy, never download. The Clipboard API needs a secure context and the
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

"""

anchor = "  (function wireCodeBox() {"
assert s.count(anchor) == 1
s = s.replace(anchor, helper + anchor, 1)

old_copy = """    if (copyBtn) copyBtn.addEventListener('click', function () {
      var text = drawMarkdown();
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () {
          copyBtn.textContent = 'Copied';
          setTimeout(function () { copyBtn.textContent = 'Copy'; }, 900);
        }, function () { download('alur-scene.md', text, 'text/markdown'); });
      } else {
        download('alur-scene.md', text, 'text/markdown');
      }
    });"""
new_copy = """    if (copyBtn) copyBtn.addEventListener('click', function () {
      copyText(drawMarkdown(), function (okCopy) {
        flashLabel(copyBtn, okCopy ? 'Copied' : 'Copy failed', 'Copy');
      });
    });"""
assert s.count(old_copy) == 1
s = s.replace(old_copy, new_copy, 1)

old_copy2 = """  document.getElementById('copyDraw').addEventListener('click', function () {
    var text = drawMarkdown();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        var b = document.getElementById('copyDraw');
        if (b) { b.textContent = 'Copied'; setTimeout(function () { b.textContent = 'Copy draw'; }, 900); }
      }, function () { download('alur-scene.md', text, 'text/markdown'); });
    } else {
      download('alur-scene.md', text, 'text/markdown');
    }
  });"""
new_copy2 = """  document.getElementById('copyDraw').addEventListener('click', function () {
    var b = document.getElementById('copyDraw');
    copyText(drawMarkdown(), function (okCopy) {
      flashLabel(b, okCopy ? 'Copied' : 'Copy failed', 'Copy draw');
    });
  });"""
assert s.count(old_copy2) == 1
s = s.replace(old_copy2, new_copy2, 1)

open(p, 'w', encoding='utf-8').write(s)
print('ok')