import pathlib
p = pathlib.Path('draw.html')
s = p.read_text(encoding='utf-8')
old = '  render();\n})();\n'
if old not in s:
    print('NOT FOUND'); exit(1)
new = '  window._state = state; window._editor = editor; window._syncShapePanel = syncShapePanel;\n  render();\n})();\n'
s = s.replace(old, new)
p.write_text(s, encoding='utf-8')
print('exposed')
