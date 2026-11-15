# ai-tools

Scripts, extracted assets, and working artifacts used to reproduce the Alur
assets (logos, icons, diagrams). Not an application: every folder stands on its
own and can be run from the repo root.

Only the generated output is published: the logo assets and the ` ```draw ` /
` ```topology ` blocks in articles. The scripts themselves are the reproducible
half of that pipeline, so they live here.

The generators expect the site checkout as a sibling directory
(`../imoon07.github.io`); every other script takes its paths as arguments.

**Total:** 7174 files.

## Requirements

- Python 3.9+
- `websocket-client` — CDP probes (`verify/`, `browser/`)
- `selenium`, `playwright` — browser automation (`browser/`, `verify/`)
- `Pillow` — image comparison (`verify/`, `renders/`)
- Chromium or Chrome for the headless probes

```bash
python3 -m pip install websocket-client selenium playwright pillow
python3 -m playwright install chromium
```

## Layout

| Folder | Contents | Key entry points |
| --- | --- | --- |
| `archive/` | Old documents and failed downloads, kept for audit | `backup-1/`, `backup-2/`, `failed-downloads/` |
| `assets/` | Extracted Unicons icons, plus the motion sources (`motion/`) and raw Lottie downloads (`lottie/`) | 573 SVG, `motion/svg-spinners`, `lottie/json` |
| `browser/` | CDP/Playwright scripts that open, drag, and inspect pages, plus browser process hygiene | `cdp-check*.js`, `cdp-dragdebug*.js`, `kill_headless.py` |
| `fetch/` | Source asset downloaders (Thridy, Devfolio, Kali) | `thridy_fetch.py`, `fetch_kali_*.py` |
| `generators/` | Logo and manifest builders, plus cross-language doc sync | `build_logo_manifest.py`, `build_topology_icons.py`, `sync_topology_templates.py`, `sync_server_stack_langs.py` |
| `icons/` | Redrawn interface icons, 64×64 | `app-window.svg`, `bug-crawl.svg` |
| `js-extracts/` | Site JS/HTML excerpts, flow captures, extraction notes | `alur-inline.js`, `alur-scene.md` |
| `layout/` | Layout experiments (columns, diagnostics) as HTML + Python | `cols.py`, `diag.py` |
| `renders/` | Render captures kept for visual comparison | PNG, `canvas/` |
| `renders/canvas/` | Screenshots captured by the `verify/canvas/` probes | `sticky.png`, `hittest*.png` |
| `snapshots/` | Page, DOM, and per-session captures, plus fetch evidence (`iconscout/`, `google/`, `logo/`, `lottiefiles/`) | `pages/`, `dom/`, `design/` |
| `snapshots/kilo-scratch/` | Fixtures, backups, logs, and HTML captures kept from the old scratch dir | `draw.html.bak`, `spec.json`, `topo_head.html` |
| `test/` | Visual and asset function tests | `test_all_shapes_*.py` |
| `vendor/` | Third-party libraries, mostly Unicons (line/solid/monochrome) | `unicons/`, `marked.min.js` |
| `verify/` | Result audits (shapes, lines, arrows, plates, touch gestures) | `verify.py`, `audit-*.html`, `mobile_touch_scroll.py` |
| `verify/canvas/` | Headless CDP probes for `draw.html` and `topology.html` (canvas, arrows, tables, charts, responsive). 393 scripts | `draw_everywhere.py`, `stickyfill.py`, `tablepanel.py`, `shot.py`, `topo_mobile.py` |

## Typical workflow

1. Fetch source assets into a scratch folder with the `fetch/` scripts.
2. Transform them with `generators/`, or a one-off script in `layout/`.
3. Verify the result with `verify/` and keep the evidence in `renders/`.
4. Save the original page and notes in `snapshots/` so the run can be repeated.

## Entry points

| Goal | Command |
| --- | --- |
| Download Thridy 3D icons (security groups) | `python3 fetch/thridy_fetch.py --group hack,crime` |
| Build the logo manifest for the site | `python3 generators/build_logo_manifest.py --site ../imoon07.github.io` |
| Build the topology icon sprite | `python3 generators/build_topology_icons.py` |
| Sync the template topology across en/id/ms/tl | `python3 generators/sync_topology_templates.py --check` |
| Sync the server-stack diagram across en/id/ms/tl | `python3 generators/sync_server_stack_langs.py --check` |
| Preview the site and docs over http or https | `python3 serve/serve.py --port 8123` |
| Test shape/line interleaving | `python3 test/test_all_shapes_line.py` |
| Check list scrolling on a touch viewport | `python3 verify/mobile_touch_scroll.py --url http://localhost:8000/draw.html --open ".mobile-fab,[data-mobile-panel='assets']" --control` |
| Run every canvas probe | `for f in verify/canvas/*.py; do python3 "$f"; done` |
| Kill the headless browsers that run leaves behind | `python3 browser/kill_headless.py --kill` |
| Search the web without solving a captcha | `python3 fetch/google_search.py "anubis lottie" --engines google,ddg` |
| Pull IconScout Lottie animations by tag | `python3 fetch/iconscout_pull.py --tag security --tag network --download` |
| Turn a Lottie JSON into an animated WebP | `python3 generators/lottie_to_webp.py in.json out.webp --size 128` |
| Import the rendered WebP clips into the logo set | `python3 generators/import_motion_webp.py` |
| Import the SMIL spinners into the logo set | `python3 generators/import_motion_svg.py --src assets/motion/svg-spinners` |

## Notes

- `fetch/thridy-candidates.json` is the Thridy slug index (groups `hack`,
  `crime`, `police`, `secure`) used by `thridy_fetch.py`; the script no longer
  depends on `/tmp`.
- `assets/` holds the source material: `assets/motion/svg-spinners` (46 SMIL
  spinners from n3r4zzurr0, MIT), `assets/motion/rendered-check` (the same files
  under their prefixed names, kept as the check set), `assets/motion/webp`
  (Lottie clips rendered to animated WebP) and `assets/lottie/json` (the raw
  IconScout downloads with `meta.json` credits).
- `snapshots/` keeps the evidence a run produced: `snapshots/iconscout` (listing
  HTML, JSON-LD, `links.json`, per-batch `lottie-meta/*.json`),
  `snapshots/google` (SERP dumps), `snapshots/logo` (deployed manifest copies),
  `snapshots/lottiefiles`, `snapshots/misc`.
- `verify/mobile_touch_scroll.py` drives Chromium over CDP with emulated touch.
  Pass `--control` for an A/B run: it restores `touch-action: none` and shows
  that the list cannot be scrolled without the fix.
- Names ending in `~2` are duplicates of an earlier attempt; safe to delete once
  confirmed unused.
- `browser/kill_headless.py` cleans up after the probes. Every probe starts
  Chromium with `--headless=new --user-data-dir=/tmp/...`; when a run dies
  before its `finally` block the browser survives, and a long audit leaves
  dozens of them holding hundreds of megabytes each. The tool lists the
  leftover instances and kills a whole tree with `--kill`.
  Chromium rewrites its own argv after start-up, so a probe launched the
  normal way shows no arguments in `/proc`; the tool therefore also detects
  an instance by its loopback debugging port and reads the profile from any
  process of the tree. A browser with a profile outside `/tmp` is reported
  and left alone, so an interactive session is never killed.
- Probe scripts keep their scratch (Chromium profiles, screenshots) in
  `/tmp/alur-probes/`, outside the repo. Override the port in the script when
  two runs collide.
- `google_search.py` opens Google in a headed Chromium on a persistent profile.
  When the IP is already flagged Google answers `/sorry/`, and waiting for a
  human is a dead end, so the tool falls through to DuckDuckGo's HTML endpoint
  (and Bing) over plain HTTPS in the same run. `--engines` sets the order,
  `--wait 0` (the default) skips the captcha wait entirely, and `--login` is
  opt-in because a signed-in Google session is not needed for search.
- `iconscout_pull.py` crawls the tag listings through JSON-LD (the listing has
  no `<a>` tags at all) and downloads the Lottie JSON behind the `Download
  Lottie JSON` button, which hydrates ~2 s after load. A free account has a
  daily download cap; when the limit dialog appears the batch stops instead of
  retrying every URL.
- `.pyc` files and `__pycache__/` are caches, not sources; they are ignored.