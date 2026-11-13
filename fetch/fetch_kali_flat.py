#!/usr/bin/env python3
import os, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path('/home/moon/Projects/logo')
SEC = ROOT/'security'
PROG = ROOT/'programming'
STACK = ROOT/'stack'
BASE = 'https://raw.githubusercontent.com/l0gicx/kali-flat-icons/main/'

# (repo_path, target_folder, out_name)
ITEMS = [
 # security tools
 ('N/nmap.svg', SEC, 'nmap.svg'),
 ('M/masscan.svg', SEC, 'masscan.svg'),
 ('Z/zaproxy.svg', SEC, 'zaproxy.svg'),
 ('S/sqlmap.svg', SEC, 'sqlmap.svg'),
 ('S/sqlninja.svg', SEC, 'sqlninja.svg'),
 ('S/sqlsus.svg', SEC, 'sqlsus.svg'),
 ('J/john.svg', SEC, 'john.svg'),
 ('H/hashcat.svg', SEC, 'hashcat.svg'),
 ('H/hydra.svg', SEC, 'hydra.svg'),
 ('N/nikto.svg', SEC, 'nikto.svg'),
 ('G/gobuster.svg', SEC, 'gobuster.svg'),
 ('D/dirb.svg', SEC, 'dirb.svg'),
 ('D/dirbuster.svg', SEC, 'dirbuster.svg'),
 ('W/wfuzz.svg', SEC, 'wfuzz.svg'),
 ('F/ffuf.svg', SEC, 'ffuf.svg'),
 ('W/whatweb.svg', SEC, 'whatweb.svg'),
 ('W/wpscan.svg', SEC, 'wpscan.svg'),
 ('A/amass.svg', SEC, 'amass.svg'),
 ('R/responder.svg', SEC, 'responder.svg'),
 ('I/impacket.svg', SEC, 'impacket.svg'),
 ('B/bloodhound.svg', SEC, 'bloodhound.svg'),
 ('C/crackmapexec.svg', SEC, 'crackmapexec.svg'),
 ('E/evil-winrm.svg', SEC, 'evil-winrm.svg'),
 ('E/enum4linux.svg', SEC, 'enum4linux.svg'),
 ('M/mimikatz.svg', SEC, 'mimikatz.svg'),
 ('S/setoolkit.svg', SEC, 'setoolkit.svg'),
 ('E/ettercap.svg', SEC, 'ettercap.svg'),
 ('B/bettercap.svg', SEC, 'bettercap.svg'),
 ('M/mitmproxy.svg', SEC, 'mitmproxy.svg'),
 ('A/aircrack-ng.svg', SEC, 'aircrack-ng.svg'),
 ('A/airgeddon.svg', SEC, 'airgeddon.svg'),
 ('R/reaver.svg', SEC, 'reaver.svg'),
 ('W/wifite.svg', SEC, 'wifite.svg'),
 ('K/kismet.svg', SEC, 'kismet.svg'),
 ('F/fern-wifi-cracker.svg', SEC, 'fern-wifi-cracker.svg'),
 ('B/bully.svg', SEC, 'bully.svg'),
 ('B/binwalk.svg', SEC, 'binwalk.svg'),
 ('R/radare2.svg', SEC, 'radare2.svg'),
 ('G/ghidra.svg', SEC, 'ghidra.svg'),
 ('C/cutter.svg', SEC, 'cutter.svg'),
 ('J/jadx.svg', SEC, 'jadx.svg'),
 ('A/apktool.svg', SEC, 'apktool.svg'),
 ('D/dex2jar.svg', SEC, 'dex2jar.svg'),
 ('J/jd-gui.svg', SEC, 'jd-gui.svg'),
 ('V/volatility.svg', SEC, 'volatility.svg'),
 ('Y/yara.svg', SEC, 'yara.svg'),
 ('O/openvas.svg', SEC, 'openvas.svg'),
 ('N/nessus.svg', SEC, 'nessus.svg'),
 ('L/lynis.svg', SEC, 'lynis.svg'),
 ('C/chkrootkit.svg', SEC, 'chkrootkit.svg'),
 ('C/clamav.svg', SEC, 'clamav.svg'),
 ('A/autopsy.svg', SEC, 'autopsy.svg'),
 ('S/sleuthkit.svg', SEC, 'sleuthkit.svg'),
 ('F/foremost.svg', SEC, 'foremost.svg'),
 ('S/steghide.svg', SEC, 'steghide.svg'),
 ('N/netcat.svg', SEC, 'netcat.svg'),
 ('N/ncat.svg', SEC, 'ncat.svg'),
 ('P/proxychains.svg', SEC, 'proxychains.svg'),
 ('A/armitage.svg', SEC, 'armitage.svg'),
 ('B/beef-xss.svg', SEC, 'beef-xss.svg'),
 ('C/commix.svg', SEC, 'commix.svg'),
 ('S/spiderfoot.svg', SEC, 'spiderfoot.svg'),
 ('M/maltego.svg', SEC, 'maltego.svg'),
 ('T/theharvester.svg', SEC, 'theharvester.svg'),
 ('R/recon-ng.svg', SEC, 'recon-ng.svg'),
 ('D/dnsenum.svg', SEC, 'dnsenum.svg'),
 ('D/dnsrecon.svg', SEC, 'dnsrecon.svg'),
 ('F/fierce.svg', SEC, 'fierce.svg'),
 ('P/patator.svg', SEC, 'patator.svg'),
 ('M/medusa.svg', SEC, 'medusa.svg'),
 ('H/hashid.svg', SEC, 'hashid.svg'),
 ('H/hash-identifier.svg', SEC, 'hash-identifier.svg'),
 ('C/crunch.svg', SEC, 'crunch.svg'),
 ('C/cewl.svg', SEC, 'cewl.svg'),
 ('W/webscarab.svg', SEC, 'webscarab.svg'),
 ('S/skipfish.svg', SEC, 'skipfish.svg'),
 ('P/paros.svg', SEC, 'paros.svg'),
 ('G/gvm.svg', SEC, 'gvm.svg'),
 ('B/bulk-extractor.svg', SEC, 'bulk-extractor.svg'),
 ('B/backdoor-factory.svg', SEC, 'backdoor-factory.svg'),
 ('M/msfpc.svg', SEC, 'msfpc.svg'),
 ('P/pipal.svg', SEC, 'pipal.svg'),
 ('S/starkiller.svg', SEC, 'starkiller.svg'),
 ('P/powershell-empire.svg', SEC, 'powershell-empire.svg'),
 ('P/powersploit.svg', SEC, 'powersploit.svg'),
 # programming / dev tools
 ('V/vim.svg', PROG, 'vim.svg'),
 ('N/nvim.svg', PROG, 'neovim.svg'),
 ('E/emacs.svg', PROG, 'emacs.svg'),
 ('S/sublime-text.svg', PROG, 'sublime-text.svg'),
 ('V/visual-studio-code.svg', PROG, 'vscode.svg'),
 ('C/code-insiders.svg', PROG, 'vscode-insiders.svg'),
 ('C/codeblocks.svg', PROG, 'codeblocks.svg'),
 ('Q/qt.svg', PROG, 'qt.svg'),
 ('C/CMakeSetup32.svg', PROG, 'cmake.svg'),
 ('M/mono.svg', PROG, 'mono.svg'),
 ('M/monodevelop.svg', PROG, 'monodevelop.svg'),
 ('J/java.svg', PROG, 'java-kali.svg'),
 ('P/php.svg', PROG, 'php-kali.svg'),
 ('P/python.svg', PROG, 'python-kali.svg'),
 ('R/rust.svg', PROG, 'rust-kali.svg'),
 ('G/gdb.svg', PROG, 'gdb.svg') if False else None,
]
ITEMS = [i for i in ITEMS if i]

def valid_svg(data: bytes) -> bool:
    if len(data) < 50: return False
    h = data[:512].lstrip().lower()
    return b'<svg' in h or b'<?xml' in h

results = []
for path, folder, out_name in ITEMS:
    dest = folder / out_name
    if dest.exists():
        results.append((out_name, folder.name, 'EXISTS', path))
        continue
    url = BASE + urllib.parse.quote(path)
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'logo-fetcher/1.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        if not valid_svg(data):
            results.append((out_name, folder.name, 'FAIL', f'invalid svg {path}'))
            continue
        dest.write_bytes(data)
        results.append((out_name, folder.name, 'DOWNLOADED', f'ok {len(data)}b {path}'))
    except Exception as e:
        results.append((out_name, folder.name, 'FAIL', f'{e} {path}'))

ok = sum(1 for r in results if r[2] in ('DOWNLOADED','EXISTS'))
print(f'OK={ok}')
for r in results:
    print('|'.join(r))
