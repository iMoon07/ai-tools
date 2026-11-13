import base64, io, re
from pathlib import Path
from PIL import Image

SRC = Path("/home/moon/Projects/ai-tools/assets/logos")
DST = Path("/home/moon/Projects/logo")

def read(name):
    return (SRC / name).read_text(encoding="utf-8")

def write(rel, text):
    p = DST / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    print("wrote", rel, len(text), "bytes")

# 1) Simple Icons files: copy verbatim (builder strips <title>)
for name in ["actix", "rocket", "gin", "blazor", "trpc"]:
    s = read(name + ".svg")
    write(f"programming/{name}.svg", s)

# 2) echo: crop the three-polygon sound mark out of the wordmark
s = read("echo.svg")
m = re.search(r'<g transform="translate\(-16,-15\.7\)">.*?</g>', s, re.S)
assert m, "echo mark not found"
write("programming/echo.svg",
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 37">\n'
      + m.group(0).replace("<g ", "<g fill-rule=\"evenodd\" ", 1)
      + "\n</svg>\n")

# 3) fiber: keep the three speed-line paths (the F mark), drop the wordmark
s = read("fiber.svg")
paths = re.findall(r'<path[^>]*fill="#00acd7"[^>]*/>', s)
assert len(paths) == 3, len(paths)
write("programming/fiber.svg",
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="20 60 200 140">\n'
      + "\n".join(paths) + "\n</svg>\n")

# 4) jakartaee: keep the horse (3 warm fills + the dark blue base), drop the text
s = read("jakartaee.svg")
keep = []
for m in re.finditer(r'<path[^>]*fill="(#[0-9A-Fa-f]{6})"[^>]*/>', s):
    tag, fill = m.group(0), m.group(1).upper()
    if fill in ("#FDB940", "#FEB322", "#F98200") or (fill == "#1B208B" and 'd="M112.931' in tag):
        keep.append(tag)
assert len(keep) == 4, len(keep)
write("programming/jakartaee.svg",
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 175">\n'
      + "\n".join(keep) + "\n</svg>\n")

# 5) chronograf: official gradient clock
write("stack/chronograf.svg", read("chronograf-logo.svg"))

# 6) custom marks (no official SVG exists)
write("programming/axum.svg", '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <path fill="#2E6BE6" d="M12 1.8 22.2 22h-4.9l-1.8-3.6H8.5L6.7 22H1.8L12 1.8Zm0 6.9-2.4 4.9h4.8L12 8.7Z"/>
</svg>
''')
write("stack/telegraf.svg", '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <path fill="#22ADF6" d="M8 1.5h2.2v5H8zM13.8 1.5H16v5h-2.2zM5.5 7.5h13a2 2 0 0 1 2 2v2.2a8.5 8.5 0 0 1-17 0V9.5a2 2 0 0 1 2-2Zm5.4 12.3h2.2V23h-2.2z"/>
</svg>
''')
write("stack/kapacitor.svg", '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <path fill="#00A2E8" d="M1 10h4l2-6 4 16 3-10 2 4h7v2h-8l-1-2-3 10L6.9 8 6 12H1z"/>
</svg>
''')
write("stack/iis.svg", '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <path fill="#3C8DBC" d="M2.5 3.5h8.2v8.2H2.5zM13.3 3.5h8.2v8.2h-8.2zM2.5 13.3h8.2v7.2H2.5zM13.3 13.3h8.2v7.2h-8.2z"/>
</svg>
''')

# 7) raster fallbacks: sinatra fedora + pyramid (lightened for the dark nodes)
def png_data_uri(path, lighten=False, min_luma=0.30):
    im = Image.open(path).convert("RGBA")
    px = im.load()
    w, h = im.size
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    def luma(rgb):
        r, g, b = (lin(c) for c in rgb)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    if lighten:
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if a == 0:
                    continue
                for _ in range(24):
                    if luma((r, g, b)) >= min_luma:
                        break
                    r = round(r + (255 - r) * 0.12)
                    g = round(g + (255 - g) * 0.12)
                    b = round(b + (255 - b) * 0.12)
                px[x, y] = (r, g, b, a)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def raster_svg(path, lighten=False):
    im = Image.open(path)
    w, h = im.size
    uri = png_data_uri(path, lighten=lighten)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">\n'
            f'  <image href="{uri}" width="{w}" height="{h}"/>\n</svg>\n')

write("programming/sinatra.svg", raster_svg(SRC / "sinatra.png"))
write("programming/pyramid.svg", raster_svg(SRC / "pyramid.png", lighten=True))
