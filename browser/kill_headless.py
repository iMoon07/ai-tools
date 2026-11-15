#!/usr/bin/env python3
"""Kill leftover headless browser instances left behind by probe runs.

Every CDP probe in `verify/` and `browser/` starts Chromium with
`--headless=new --user-data-dir=/tmp/...`. When a probe dies before its
`finally` block runs, the browser keeps running: the process list fills up with
headless instances that hold hundreds of megabytes each and slowly eat the CPU.

A process tree is a candidate only when all of these hold:

1. the executable is a known browser (chromium, chrome, msedge, firefox);
2. the tree is headless: either a headless flag is still visible in its command
   line, or one of its processes listens on a loopback debugging port;
3. if the profile is readable it must live under an allowed prefix
   (default `/tmp`); an interactive browser has its profile under `~/.config`,
   so it is never touched.

Chromium rewrites its own argv once it starts, so for a normally launched probe
the main process shows no arguments at all. That is why the tool also looks at
listening sockets, and why it reads the profile from any process of the tree
that still carries it.

Usage:
    python3 browser/kill_headless.py                 # list, kill nothing
    python3 browser/kill_headless.py --kill          # SIGTERM, then SIGKILL
    python3 browser/kill_headless.py --kill -v       # same, with details
    python3 browser/kill_headless.py --kill --older-than 300
    python3 browser/kill_headless.py --json

Exit codes: 0 = done (also when nothing matched), 1 = bad usage, 3 = some
processes survived SIGKILL.
"""

import argparse
import json
import os
import re
import signal
import sys
import time

# Executable basenames we recognise as browsers.
BROWSERS = (
    "chromium", "chromium-browser", "chrome", "google-chrome",
    "google-chrome-stable", "msedge", "microsoft-edge", "firefox", "firefox-bin",
)
HEADLESS_FLAGS = ("--headless", "-headless", "--remote-debugging-port=")
PROFILE_RE = re.compile(r"(?:--user-data-dir|--profile|-profile)[= ]([^\s]+)")
PORT_RE = re.compile(r"--remote-debugging-port=(\d+)")
PROFILE_PREFIXES = ("/tmp",)
HZ = os.sysconf("SC_CLK_TCK") if hasattr(os, "sysconf") else 100


def read_text(path):
    try:
        with open(path, "rb") as fh:
            return fh.read().decode("utf-8", "replace")
    except OSError:
        return None


def read_link(path):
    try:
        return os.readlink(path)
    except OSError:
        return ""


def browser_name(pid):
    exe = os.path.basename(read_link("/proc/%d/exe" % pid))
    low = exe.lower()
    return exe if any(name in low for name in BROWSERS) else ""


def cmdline(pid):
    raw = read_link("/proc/%d/cmdline" % pid)
    try:
        with open("/proc/%d/cmdline" % pid, "rb") as fh:
            raw = fh.read().decode("utf-8", "replace")
    except OSError:
        return []
    return [p for p in raw.split("\0") if p]


def stat_fields(pid):
    data = read_text("/proc/%d/stat" % pid)
    if not data:
        return None
    try:
        return data[data.rindex(")") + 2:].split()
    except (ValueError, IndexError):
        return None


def ppid_of(pid):
    fields = stat_fields(pid)
    if not fields:
        return 0
    try:
        return int(fields[1])
    except (ValueError, IndexError):
        return 0


def age_seconds(pid):
    fields = stat_fields(pid)
    uptime = read_text("/proc/uptime")
    if not fields or not uptime:
        return None
    try:
        start_ticks = int(fields[19])
        return max(0.0, float(uptime.split()[0]) - start_ticks / float(HZ))
    except (ValueError, IndexError):
        return None


def profile_of(parts):
    """Read the profile from argv. Chromium can rewrite argv into one blob, so
    match anywhere in the joined command line, not only at an argument start."""
    match = PROFILE_RE.search(" ".join(parts))
    return match.group(1) if match else ""


def port_of(parts):
    match = PORT_RE.search(" ".join(parts))
    return match.group(1) if match else ""


def listen_ports():
    """Loopback TCP ports with the inode of their listening socket."""
    ports = {}
    for path in ("/proc/net/tcp", "/proc/net/tcp6"):
        text = read_text(path)
        if not text:
            continue
        for line in text.splitlines()[1:]:
            cols = line.split()
            if len(cols) < 10 or cols[3] != "0A":
                continue
            local, inode = cols[1], cols[9]
            if not local.upper().startswith("0100007F") and not local.upper().startswith("00000000000000000000000001000000"):
                continue
            try:
                ports[inode] = int(local.split(":")[1], 16)
            except (ValueError, IndexError):
                continue
    return ports


def socket_inodes(pid):
    out = []
    try:
        fds = os.listdir("/proc/%d/fd" % pid)
    except OSError:
        return out
    for fd in fds:
        target = read_link("/proc/%d/fd/%s" % (pid, fd))
        if target.startswith("socket:["):
            out.append(target[8:-1])
    return out


def collect(names, prefixes, port):
    """Group browser processes into instances (rooted at the topmost browser
    process) and return (candidates, skipped)."""
    procs = {}
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        exe = browser_name(pid)
        if not exe:
            continue
        if names and not any(n in exe.lower() or n in " ".join(cmdline(pid)).lower()
                             for n in names):
            continue
        parts = cmdline(pid)
        line = " ".join(parts)
        procs[pid] = {
            "exe": exe,
            "line": line,
            "parts": parts,
            "ppid": ppid_of(pid),
            "profile": profile_of(parts),
            "headless": any(f in line for f in HEADLESS_FLAGS),
            "port": port_of(parts),
        }

    # Chromium hides --user-data-dir on the main process: borrow the profile
    # from any descendant that still carries it.
    kids = {}
    for pid, proc in procs.items():
        kids.setdefault(proc["ppid"], []).append(pid)
    for pid, proc in procs.items():
        if proc["profile"]:
            continue
        queue, seen = list(kids.get(pid, [])), set()
        while queue:
            cur = queue.pop()
            if cur in seen:
                continue
            seen.add(cur)
            if procs[cur]["profile"]:
                proc["profile"] = procs[cur]["profile"]
                break
            queue.extend(kids.get(cur, []))

    # Group the tree: walk up while the parent is a browser process too.
    groups = {}
    for pid in procs:
        root, cur, guard = pid, pid, 0
        while guard < 64:
            parent = procs[cur]["ppid"]
            if parent not in procs:
                break
            cur = parent
            root = parent
            guard += 1
        groups.setdefault(root, []).append(pid)

    listeners = listen_ports()
    candidates, skipped = [], []
    for root, members in groups.items():
        headless = any(procs[m]["headless"] for m in members)
        ports = [procs[m]["port"] for m in members if procs[m]["port"]]
        for m in members:
            for inode in socket_inodes(m):
                if inode in listeners and str(listeners[inode]) not in ports:
                    ports.append(str(listeners[inode]))
                    headless = True
        profiles = [procs[m]["profile"] for m in members if procs[m]["profile"]]
        profile = profiles[0] if profiles else ""
        if not headless:
            continue
        if profile and not any(profile.startswith(p) for p in prefixes):
            skipped.append((root, "profile outside " + ",".join(prefixes)))
            continue
        if port and str(port) not in ports:
            continue
        candidates.append({
            "pid": root,
            "exe": procs[root]["exe"],
            "members": sorted(members),
            "age": age_seconds(root),
            "profile": profile or "(hidden by chromium)",
            "port": ports[0] if ports else "",
            "cmd": procs[root]["line"] or "(no argv)",
        })
    candidates.sort(key=lambda r: r["pid"])
    skipped.sort(key=lambda r: r[0])
    return candidates, skipped


def fmt_age(seconds):
    if seconds is None:
        return "?"
    seconds = int(seconds)
    if seconds < 60:
        return "%ds" % seconds
    if seconds < 3600:
        return "%dm%02ds" % (seconds // 60, seconds % 60)
    return "%dh%02dm" % (seconds // 3600, (seconds % 3600) // 60)


def alive(pid):
    return os.path.exists("/proc/%d" % pid)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Kill leftover headless browser instances from probe runs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Usage:", 1)[-1].strip())
    ap.add_argument("--kill", action="store_true",
                    help="actually terminate the candidates (default: list only)")
    ap.add_argument("--signal", choices=("TERM", "KILL"), default="TERM",
                    help="signal for the first pass (default: TERM)")
    ap.add_argument("--grace", type=float, default=3.0,
                    help="seconds to wait before SIGKILL of survivors (default: 3)")
    ap.add_argument("--name", default="", metavar="LIST",
                    help="comma separated browser names (default: every known browser)")
    ap.add_argument("--prefix", action="append", default=None, metavar="DIR",
                    help="allowed profile prefix, repeatable (default: /tmp)")
    ap.add_argument("--port", type=int, default=0,
                    help="only instances opened on this debugging port")
    ap.add_argument("--older-than", type=float, default=0.0, metavar="SEC",
                    help="skip instances younger than SEC (default: 0)")
    ap.add_argument("--json", action="store_true", help="machine readable output")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print the full command line and every pid of each instance")
    args = ap.parse_args(argv)

    names = tuple(n.strip().lower() for n in args.name.split(",") if n.strip())
    prefixes = tuple(args.prefix) if args.prefix else PROFILE_PREFIXES

    found, skipped = collect(names, prefixes, args.port)
    if args.older_than > 0:
        kept = []
        for r in found:
            if r["age"] is not None and r["age"] < args.older_than:
                skipped.append((r["pid"], "younger than %gs" % args.older_than))
            else:
                kept.append(r)
        found = kept

    if args.json:
        print(json.dumps({
            "instances": found,
            "skipped": [{"pid": p, "why": why} for p, why in skipped],
        }, indent=2))
    else:
        print("headless browser instances: %d" % len(found))
        for r in found:
            print("  %7d  %-14s %6s  %s%s  (%d procs)" % (
                r["pid"], r["exe"], fmt_age(r["age"]), r["profile"],
                ("  port " + r["port"]) if r["port"] else "", len(r["members"])))
            if args.verbose:
                print("           pids %s" % ",".join(str(m) for m in r["members"]))
                print("           %s" % r["cmd"])
        if skipped:
            print("skipped: %d" % len(skipped))
            for pid, why in skipped:
                print("  %7d  %s" % (pid, why))

    if not found:
        return 0
    if not args.kill:
        print("\nnothing killed. re-run with --kill")
        return 0

    sig = signal.SIGKILL if args.signal == "KILL" else signal.SIGTERM
    targets = [m for r in found for m in r["members"]]
    for pid in targets:
        try:
            os.kill(pid, sig)
        except OSError as err:
            print("  %7d  failed: %s" % (pid, err), file=sys.stderr)
    time.sleep(0.5 if sig == signal.SIGKILL else max(0.0, args.grace))
    survivors = [pid for pid in targets if alive(pid)]
    for pid in survivors:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    time.sleep(0.5)
    left = [pid for pid in survivors if alive(pid)]
    if not args.json:
        print("killed %d of %d processes, survivors %d" % (
            len(targets) - len(left), len(targets), len(left)))
    return 3 if left else 0


if __name__ == "__main__":
    sys.exit(main())