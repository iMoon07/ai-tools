import pathlib
p = pathlib.Path('draw.html')
s = p.read_text(encoding='utf-8')
old = '  window._state = state; window._editor = editor; window._syncShapePanel = syncShapePanel;\n  render();\n})();\n'
new = '  render();\n})();\n'
if old in s:
    s = s.replace(old, new)
    p.write_text(s, encoding='utf-8')
    print('reverted')
else:
    print('not found')
