#!/usr/bin/env python3
"""Author the Alur motion set: standalone animated SVGs (SMIL).

Every file is a 64x64 tile that animates on its own, so it can be dropped into
the canvas renderer unchanged (the renderer paints logos as <image>, and SMIL
keeps running inside an SVG image).
"""
from pathlib import Path

OUT = Path("/home/moon/Projects/logo/motion")

HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" '
        'height="64" fill="none">\n<title>{title}</title>\n')
FOOT = "</svg>\n"

BLUE = "#58A6FF"
TEAL = "#24A8AF"
AMBER = "#E7B549"
RED = "#DE524C"
INK = "#1C2033"


def write(name, title, body):
    text = HEAD.format(title=title) + body.lstrip("\n") + FOOT
    (OUT / name).write_text(text, encoding="utf-8")
    print("wrote", name, len(text))


def loop(dur, values, extra="", attr="opacity"):
    return ('<animate attributeName="%s" values="%s" dur="%s" repeatCount="indefinite" %s/>'
            % (attr, values, dur, extra))


def spin(dur, values, extra=""):
    return ('<animateTransform attributeName="transform" type="rotate" values="%s" '
            'dur="%s" repeatCount="indefinite" %s/>' % (values, dur, extra))


def move(dur, values, extra=""):
    return ('<animateTransform attributeName="transform" type="translate" values="%s" '
            'dur="%s" repeatCount="indefinite" %s/>' % (values, dur, extra))


# 1 ---------------------------------------------------------------- shield scan
write("shield-scan.svg", "Shield scan", """
  <defs>
    <clipPath id="sh"><path d="M32 6 52 14v16c0 14-9 23-20 28-11-5-20-14-20-28V14Z"/></clipPath>
  </defs>
  <path d="M32 6 52 14v16c0 14-9 23-20 28-11-5-20-14-20-28V14Z" stroke="%s" stroke-width="3" stroke-linejoin="round"/>
  <path d="m23 32 7 7 13-15" stroke="%s" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>
  <g clip-path="url(#sh)">
    <rect x="10" y="0" width="44" height="3" fill="%s" opacity=".55">
      %s
    </rect>
  </g>
""" % (BLUE, TEAL, BLUE, move("2.6s", "0 12; 0 46; 0 12",
                              'calcMode="spline" keyTimes="0;0.5;1" '
                              'keySplines=".4 0 .6 1;.4 0 .6 1"')))

# 2 ------------------------------------------------------------ fingerprint scan
write("fingerprint-scan.svg", "Fingerprint scan", """
  <defs>
    <clipPath id="fp"><rect x="12" y="12" width="40" height="40" rx="10"/></clipPath>
  </defs>
  <g stroke="%s" stroke-width="3" stroke-linecap="round" clip-path="url(#fp)">
    <path d="M18 46c0-16 6-27 14-27s14 11 14 27"/>
    <path d="M23 48c0-14 4-22 9-22s9 8 9 22"/>
    <path d="M27.5 50c0-12 2-18 4.5-18s4.5 6 4.5 18"/>
    <path d="M31 52v-9"/>
  </g>
  <g clip-path="url(#fp)">
    <rect x="12" y="0" width="40" height="2.6" fill="%s" opacity=".5">
      %s
    </rect>
  </g>
""" % (TEAL, TEAL, move("2.2s", "0 14; 0 50; 0 14",
                       'calcMode="spline" keyTimes="0;0.5;1" keySplines=".4 0 .6 1;.4 0 .6 1"')))

# 3 ------------------------------------------------------------------ lock pulse
write("lock-pulse.svg", "Lock pulse", """
  <g>
    %s
    <path d="M22 28v-6a10 10 0 0 1 20 0v6" stroke="%s" stroke-width="3.2" stroke-linecap="round"/>
  </g>
  <rect x="15" y="28" width="34" height="26" rx="6" stroke="%s" stroke-width="3.2"/>
  <circle cx="32" cy="39" r="3.2" fill="%s">%s</circle>
  <path d="M32 42v6" stroke="%s" stroke-width="3.2" stroke-linecap="round"/>
""" % (move("1.8s", "0 0; 0 -2.5; 0 0",
            'calcMode="spline" keyTimes="0;0.5;1" keySplines=".4 0 .6 1;.4 0 .6 1"'),
       BLUE, BLUE, AMBER, loop("1.8s", "1;0.45;1"), AMBER))

# 4 --------------------------------------------------------------- hacker typing
write("hacker-typing.svg", "Hacker typing", """
  <rect x="13" y="12" width="38" height="30" rx="4" stroke="%s" stroke-width="3"/>
  <g fill="%s">
    <rect x="19" y="20" width="0" height="3" rx="1.5">
      <animate attributeName="width" values="0;16;16" keyTimes="0;0.35;1" dur="2.4s" repeatCount="indefinite"/>
    </rect>
    <rect x="19" y="27" width="0" height="3" rx="1.5">
      <animate attributeName="width" values="0;22;22" keyTimes="0;0.4;1" dur="2.4s" begin="0.25s" repeatCount="indefinite"/>
    </rect>
    <rect x="19" y="34" width="0" height="3" rx="1.5">
      <animate attributeName="width" values="0;11;11" keyTimes="0;0.45;1" dur="2.4s" begin="0.5s" repeatCount="indefinite"/>
    </rect>
  </g>
  <rect x="43" y="33" width="2" height="8" fill="%s">%s</rect>
  <path d="M8 48h48l4 6H4Z" stroke="%s" stroke-width="3" stroke-linejoin="round"/>
""" % (BLUE, TEAL, TEAL, loop("1s", "1;1;0;0", 'calcMode="discrete"'), INK))

# 5 ------------------------------------------------------------- terminal cursor
write("terminal-cursor.svg", "Terminal cursor", """
  <rect x="7" y="11" width="50" height="42" rx="6" stroke="%s" stroke-width="3"/>
  <path d="M7 20h50" stroke="%s" stroke-width="3"/>
  <g fill="%s">
    <circle cx="14" cy="15.5" r="1.8"/><circle cx="20" cy="15.5" r="1.8"/><circle cx="26" cy="15.5" r="1.8"/>
  </g>
  <path d="m15 29 5 5-5 5" stroke="%s" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M25 39h12" stroke="%s" stroke-width="3" stroke-linecap="round"/>
  <rect x="15" y="44" width="2.4" height="6" fill="%s">%s</rect>
""" % (BLUE, BLUE, "rgba(88,166,255,.45)", TEAL, AMBER, AMBER,
       loop("1.1s", "1;1;0;0", 'calcMode="discrete"')))

# 6 ------------------------------------------------------------------ cloud sync
write("cloud-sync.svg", "Cloud sync", """
  <path d="M20 44a9 9 0 0 1 1.2-17.9A13 13 0 0 1 46.6 30 8.5 8.5 0 0 1 45 44Z"
        stroke="%s" stroke-width="3" stroke-linejoin="round"/>
  <g>%s
    <path d="M25 33a7 7 0 0 1 12-3" stroke="%s" stroke-width="3" stroke-linecap="round"/>
    <path d="m37 25 1 5-5-1" stroke="%s" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
  <g>%s
    <path d="M39 37a7 7 0 0 1-12 3" stroke="%s" stroke-width="3" stroke-linecap="round"/>
    <path d="m27 45-1-5 5 1" stroke="%s" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
""" % (BLUE, spin("3s", "0 32 35;360 32 35"), TEAL, TEAL,
       spin("3s", "360 32 35;0 32 35"), AMBER, AMBER))

# 7 ------------------------------------------------------------------ data flow
def node(x, y, colour):
    return ('<circle cx="%d" cy="%d" r="5" fill="none" stroke="%s" stroke-width="3"/>' % (x, y, colour))


write("data-flow.svg", "Data flow", """
  <g stroke="rgba(88,166,255,.45)" stroke-width="2.5">
    <path d="M14 46 32 20 50 46"/><path d="M14 46h36"/>
  </g>
  %s
  %s
  %s
  <circle r="3.4" fill="%s">
    <animateMotion dur="2.4s" repeatCount="indefinite" path="M14 46 32 20 50 46 14 46"/>
  </circle>
  <circle r="3.4" fill="%s">
    <animateMotion dur="2.4s" begin="1.2s" repeatCount="indefinite" path="M50 46 32 20 14 46 50 46"/>
  </circle>
""" % (node(14, 46, BLUE), node(32, 20, TEAL), node(50, 46, BLUE), AMBER, TEAL))

# 8 ------------------------------------------------------------------ bug crawl
write("bug-crawl.svg", "Bug crawl", """
  <circle cx="32" cy="34" r="16" stroke="%s" stroke-width="2" opacity=".5">
    <animate attributeName="r" values="14;26;14" dur="2.2s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values=".55;0;.55" dur="2.2s" repeatCount="indefinite"/>
  </circle>
  <g>
    %s
    <g stroke="%s" stroke-width="3" stroke-linecap="round">
      <ellipse cx="32" cy="38" rx="9.5" ry="12"/>
      <circle cx="32" cy="22" r="5.5"/>
      <path d="M22.5 32h-7M22.5 40l-7 4M41.5 32h7M41.5 40l7 4"/>
      <path d="m28 17-3-5M36 17l3-5"/>
    </g>
  </g>
""" % (RED, spin("1.6s", "-9 32 38;9 32 38;-9 32 38",
                 'calcMode="spline" keyTimes="0;0.5;1" keySplines=".4 0 .6 1;.4 0 .6 1"'),
       INK))

# 8b ------------------------------------------------------------- shield block
write("shield-block.svg", "Shield block", """
  <path d="M32 6 52 14v16c0 14-9 23-20 28-11-5-20-14-20-28V14Z"
        stroke="%s" stroke-width="3" stroke-linejoin="round"/>
  <g stroke="%s" stroke-width="3" stroke-linecap="round">
    <path d="M32 20v14">
      <animate attributeName="opacity" values="1;.25;1" dur="1.4s" repeatCount="indefinite"/>
    </path>
    <path d="M22 40h20">
      <animate attributeName="opacity" values=".25;1;.25" dur="1.4s" repeatCount="indefinite"/>
    </path>
  </g>
  <circle cx="32" cy="34" r="17" stroke="%s" stroke-width="2" opacity=".5">
    <animate attributeName="r" values="15;24;15" dur="2.4s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values=".5;0;.5" dur="2.4s" repeatCount="indefinite"/>
  </circle>
""" % (BLUE, AMBER, TEAL))

# 9 -------------------------------------------------------------------- eye scan
write("eye-scan.svg", "Eye scan", """
  <path d="M7 32c8-12 42-12 50 0-8 12-42 12-50 0Z" stroke="%s" stroke-width="3" stroke-linejoin="round"/>
  <g>%s<circle cx="32" cy="32" r="6.5" fill="%s"/></g>
  <rect x="9" y="0" width="2.6" height="40" fill="%s" opacity=".45" clip-path="inset(0)">
    %s
  </rect>
  <clipPath id="ec"><path d="M7 32c8-12 42-12 50 0-8 12-42 12-50 0Z"/></clipPath>
  <g clip-path="url(#ec)">
    <rect x="0" y="0" width="2.6" height="64" fill="%s" opacity=".45">
      %s
    </rect>
  </g>
""" % (BLUE, move("3.2s", "-7 0;7 0;-7 0",
                 'calcMode="spline" keyTimes="0;0.5;1" keySplines=".4 0 .6 1;.4 0 .6 1"'),
       TEAL, TEAL, move("2.4s", "0 0;0 44;0 0",
                        'calcMode="spline" keyTimes="0;0.5;1" keySplines=".4 0 .6 1;.4 0 .6 1"'),
       TEAL, move("2.4s", "10 0;52 0;10 0",
                  'calcMode="spline" keyTimes="0;0.5;1" keySplines=".4 0 .6 1;.4 0 .6 1"')))

# 10 -------------------------------------------------------------- server blink
leds = []
for i, (x, y, colour) in enumerate([(20, 20, TEAL), (27, 20, AMBER), (20, 42, TEAL), (27, 42, AMBER)]):
    leds.append('<circle cx="%d" cy="%d" r="2.4" fill="%s">%s</circle>'
                % (x, y, colour, loop("1.2s", "1;.2;1", 'begin="%ss"' % (i * 0.3))))
write("server-blink.svg", "Server blink", """
  <rect x="12" y="12" width="40" height="16" rx="4" stroke="%s" stroke-width="3"/>
  <rect x="12" y="34" width="40" height="16" rx="4" stroke="%s" stroke-width="3"/>
  %s
""" % (BLUE, BLUE, "\n  ".join(leds)))

# 11 ----------------------------------------------------------------- wifi pulse
write("wifi-pulse.svg", "Wifi pulse", """
  <circle cx="32" cy="46" r="3.6" fill="%s"/>
  <g stroke="%s" stroke-width="3.2" stroke-linecap="round">
    <path d="M29 19a5 5 0 0 1 6 0">%s</path>
    <path d="M24 26a12 12 0 0 1 16 0">%s</path>
    <path d="M18 33a20 20 0 0 1 28 0">%s</path>
  </g>
""" % (TEAL, TEAL,
       loop("1.8s", ".2;1;.2", 'begin="0.6s"'),
       loop("1.8s", ".2;1;.2", 'begin="0.3s"'),
       loop("1.8s", ".2;1;.2", 'begin="0s"')))

# 12 ------------------------------------------------------------------ key turn
write("key-turn.svg", "Key turn", """
  <g>
    %s
    <circle cx="22" cy="22" r="8.5" stroke="%s" stroke-width="3.2"/>
    <path d="M28 28 48 48" stroke="%s" stroke-width="5" stroke-linecap="round"/>
    <path d="m41 45 4-4M45 49l4-4" stroke="%s" stroke-width="3.4" stroke-linecap="round"/>
  </g>
""" % (spin("2.6s", "-16 22 22;16 22 22;-16 22 22",
            'calcMode="spline" keyTimes="0;0.5;1" keySplines=".4 0 .6 1;.4 0 .6 1"'),
       AMBER, AMBER, AMBER))

# 13 ---------------------------------------------------------------- chart grow
bars = []
for x, h, colour in [(13, 14, BLUE), (27, 26, TEAL), (41, 38, AMBER)]:
    bars.append('<rect x="%d" y="50" width="9" height="0" rx="2" fill="%s">'
                '<animate attributeName="height" values="0;%d;%d" keyTimes="0;0.6;1" dur="2.4s" repeatCount="indefinite"/>'
                '<animate attributeName="y" values="50;%d;%d" keyTimes="0;0.6;1" dur="2.4s" repeatCount="indefinite"/>'
                '</rect>' % (x, colour, h, h, 50 - h, 50 - h))
write("chart-grow.svg", "Chart grow", """
  <path d="M8 54h48" stroke="rgba(28,32,51,.35)" stroke-width="2.5" stroke-linecap="round"/>
  %s
""" % "\n  ".join(bars))

# 14 ----------------------------------------------------------------- bell ring
write("bell-ring.svg", "Bell ring", """
  <g>
    %s
    <path d="M32 11a3.5 3.5 0 0 1 3.5 3.5V17c6.5 2.2 9 8 9 14.5V38l4 6H19.5l4-6v-6.5C23.5 25 26 19.2 32.5 17v-2.5A3.5 3.5 0 0 1 32 11Z"
          stroke="%s" stroke-width="3" stroke-linejoin="round"/>
    <path d="M27 48a5 5 0 0 0 10 0" stroke="%s" stroke-width="3" stroke-linecap="round"/>
  </g>
  <g stroke="%s" stroke-width="2.6" stroke-linecap="round" opacity=".7">
    <path d="M13 22 8 18">%s</path>
    <path d="M51 22 56 18">%s</path>
  </g>
""" % (spin("1.8s", "-13 32 14;13 32 14;-13 32 14",
            'calcMode="spline" keyTimes="0;0.5;1" keySplines=".4 0 .6 1;.4 0 .6 1"'),
       AMBER, AMBER, AMBER,
       loop("1.8s", ".2;1;.2", 'begin="0.2s"'),
       loop("1.8s", ".2;1;.2", 'begin="0.45s"')))

# 15 ---------------------------------------------------------------- search scan
write("search-scan.svg", "Search scan", """
  <g>%s
    <circle cx="27" cy="27" r="13" stroke="%s" stroke-width="3.4"/>
    <path d="m37 37 11 11" stroke="%s" stroke-width="5" stroke-linecap="round"/>
  </g>
  <g fill="%s">
    <path d="M50 10l1.6 4.4L56 16l-4.4 1.6L50 22l-1.6-4.4L44 16l4.4-1.6Z">%s</path>
  </g>
""" % (move("3.4s", "0 0;7 5;0 0;-5 7;0 0",
            'calcMode="spline" keyTimes="0;0.25;0.5;0.75;1" '
            'keySplines=".4 0 .6 1;.4 0 .6 1;.4 0 .6 1;.4 0 .6 1"'),
       BLUE, BLUE, AMBER, loop("1.4s", "1;.3;1")))

# 16 ---------------------------------------------------------------- user verify
write("user-verify.svg", "User verify", """
  <circle cx="32" cy="23" r="9.5" stroke="%s" stroke-width="3.2"/>
  <path d="M13 53a19 19 0 0 1 38 0" stroke="%s" stroke-width="3.2" stroke-linecap="round"/>
  <path d="m23 38 7 7 14-15" stroke="%s" stroke-width="4" stroke-linecap="round"
        stroke-linejoin="round" stroke-dasharray="34" stroke-dashoffset="34">
    <animate attributeName="stroke-dashoffset" values="34;0;0" keyTimes="0;0.55;1"
             dur="2.2s" repeatCount="indefinite"/>
  </path>
""" % (BLUE, BLUE, TEAL))

# 17 -------------------------------------------------------------- database pulse
write("database-pulse.svg", "Database pulse", """
  <g stroke="%s" stroke-width="3" stroke-linejoin="round">
    <path d="M16 18v28c0 3.3 7.2 6 16 6s16-2.7 16-6V18"/>
    <ellipse cx="32" cy="18" rx="16" ry="6"/>
    <path d="M16 32c0 3.3 7.2 6 16 6s16-2.7 16-6" opacity=".55"/>
  </g>
  <g stroke="%s" stroke-width="2" fill="none">
    <ellipse cx="32" cy="34" rx="16" ry="8" opacity=".6">
      <animate attributeName="rx" values="15;27" dur="2.2s" repeatCount="indefinite"/>
      <animate attributeName="ry" values="7;14" dur="2.2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".6;0" dur="2.2s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="32" cy="34" rx="16" ry="8" opacity=".6">
      <animate attributeName="rx" values="15;27" dur="2.2s" begin="1.1s" repeatCount="indefinite"/>
      <animate attributeName="ry" values="7;14" dur="2.2s" begin="1.1s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".6;0" dur="2.2s" begin="1.1s" repeatCount="indefinite"/>
    </ellipse>
  </g>
""" % (BLUE, TEAL))

# 18 ---------------------------------------------------------------- rocket launch
write("rocket-launch.svg", "Rocket launch", """
  <g>%s
    <path d="M32 6c7 7 10 16 10 24l-10 8-10-8c0-8 3-17 10-24Z"
          stroke="%s" stroke-width="3" stroke-linejoin="round"/>
    <circle cx="32" cy="24" r="4.2" stroke="%s" stroke-width="3"/>
    <path d="M22 30l-6 8 8-1M42 30l6 8-8-1" stroke="%s" stroke-width="3"
          stroke-linejoin="round" stroke-linecap="round"/>
  </g>
  <path d="M27 41c0 5 5 13 5 13s5-8 5-13Z" fill="%s" opacity=".9">
    <animate attributeName="opacity" values=".9;.35;.9" dur=".45s" repeatCount="indefinite"/>
    <animateTransform attributeName="transform" type="scale" values="1 1;1 1.35;1 1"
                      dur=".45s" repeatCount="indefinite" additive="sum"/>
  </path>
""" % (move("1.8s", "0 1;0 -2;0 1",
            'calcMode="spline" keyTimes="0;0.5;1" keySplines=".4 0 .6 1;.4 0 .6 1"'),
       BLUE, TEAL, BLUE, AMBER))

print("done")