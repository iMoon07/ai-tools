#!/usr/bin/env python3
import json, os, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path('/home/moon/Projects/logo')
SEC = ROOT/'security'
BASE = 'https://raw.githubusercontent.com/l0gicx/kali-flat-icons/main/'

# existing stems/names normalized
existing = set()
for sub in ['security','programming','stack']:
    p = ROOT/sub
    if p.exists():
        for f in p.iterdir():
            if f.is_file():
                existing.add(f.stem.lower().replace('_','-'))

d = json.load(open('/tmp/kali_tree.json'))
paths = [x['path'] for x in d.get('tree',[]) if x.get('type')=='blob' and x['path'].lower().endswith(('.svg','.png'))]

def normbase(path):
    return path.split('/')[-1].rsplit('.',1)[0].lower().replace('_','-')

hack_kw = [
 'kali','exploit','vuln','forensic','sniff','spoof','wireless','password','crack','brute','fuzz','scan','enum',
 'recon','osint','phish','social','meterpreter','shell','payload','backdoor','trojan','rat','c2','cobalt','empire',
 'psexec','smb','ldap','kerb','ntlm','hash','dump','creds','mimikatz','blood','responder','impacket','evil','winrm',
 'sql','xss','inject','burp','zap','proxy','mitm','etter','arp','dns','dhcp','wifi','wpa','wps','wep','air','deauth',
 'packet','pcap','tcp','nmap','masscan','nikto','dirb','gobuster','wpscan','joom','drupal','cms','web','http',
 'stego','steg','exif','metadata','binwalk','firmware','reverse','disasm','debug','ghidra','radare','ida','yara','malware',
 'virus','clam','rootkit','audit','hardening','pentest','pwntools','rop','heap','overflow','fuzzer','afl',
 'snort','suricata','zeek','bro','ids','ips','waf','modsec','firewall','siem','ossec','wazuh','openvas','nessus',
 'lynis','rkhunter','chkroot','autopsy','sleuth','volatility','memory','carve','recover','ddrescue','guymager',
 'macchanger','tor','proxychain','anonym','onion','i2p','vpn','tunnel','chisel','socat','netcat','ncat','ssh',
 'wordlist','cewl','crunch','hydra','medusa','patator','john','hashcat','ophcrack','rainbow',
 'setoolkit','beef','evilgrade','king-phisher','phishing','gophish',
 'metasploit','armitage','msf','faraday','dradis','pipal','magictree','keepnote','cherrytree',
 'burpsuite','webscarab','paros','w3af','skipfish','wapiti','arachni','uniscan','davtest','cadaver','joomscan',
 'droopescan','whatweb','httprint','sslscan','sslyze','testssl','nikto',
 'reaver','bully','pixiewps','fern','wifite','kismet','mdk3','airgeddon','hostapd','wifiphisher',
 'multimon','rtl','sdr','hackrf','gqrx',
 'nasm','shellcode','msfvenom','veil','shellter','hyperion',
 'apk','jadx','dex2jar','bytecode','androguard','mobsf','drozer',
 'ike-scan','ssldump','sslsplit','stunnel','iodine','dns2tcp','ptunnel','udptunnel','proxytunnel','pwnat','nishang','powersploit','empire','starkiller','covenant','havoc','sliver','mythic','poshc2','merlin',
 'seclists','dirbuster','dirsearch','ffuf','wfuzz','ferox','amass','sublist3r','theharvester','maltego','recon-ng','spiderfoot','dnsrecon','dnsenum','fierce','dmitry','netdiscover','nbtscan','enum4linux','smbmap','crackmapexec','evil-winrm','bloodhound',
 'radare','cutter','ollydbg','edb','gdb','objdump','strings','ltrace','strace',
 'sakis3g','macchanger','ifconfig','wireshark','tcpdump','tshark','bettercap','mitmproxy','sslstrip','dsniff','arpspoof','driftnet','urlsnarf','webspy','hamster','ferret','macof','yersinia',
 'truecrypt','veracrypt','cryptsetup','keepass','bitwarden','hashdeep','hashid','fcrackzip','pdfcrack','rarcrack','sucrack','crowbar',
 'sleuthkit','dc3dd','ddrescue','foremost','scalpel','bulk','photorec','testdisk','magicrescue','recoverjpeg','extundelete',
 'ncat','socat','proxychain','chisel','ligolo','impacket','responder','coercer','certipy','kerbrute','rubeus',
 'hexedit','bless','okteta','wxhexeditor','ghidra','cutter','hopper','binja',
 'affcat','tsk','mmcat','mmls','mmstat','fls','icat','istat','ifind','ffind','blkcalc','blkcat','blkls','blkstat','fsstat','img_cat','img_stat','jcat','jls','hfind','srch_strings','sorter','sigfind',
 'afl','honggfuzz','boofuzz','spike',
 'router','firmware','binwalk','sasquatch','jefferson',
 'wordlists','rockyou','seclists',
 'termineter','thc','voiphopper','sidguesser','onesixtyone','oscanner','smtp-user-enum','tnscmd10g','ike-scan','sslh','swaks','websploit'
]

# blacklist obvious non-hacking/generic app noise
black_sub = [
 'abrowser','accessories-calculator','accessories-character','accessories-dictionary','accessories-text-editor',
 'airplane-mode','akregator','amarok','audacious','audacity','bittorrent','brave-browser','chrome-store',
 'com.github.','computerjanitor','dconf-editor','deadbeef','deepin-cloud-print','deepin-cloud-scan','deepin-feedback',
 'distributor-logo-arch','distributor-logo-centos','distributor-logo-chakra','distributor-logo-debian','distributor-logo-elementary',
 'distributor-logo-fedora','distributor-logo-freebsd','distributor-logo-gentoo','distributor-logo-kaos','distributor-logo-korora',
 'distributor-logo-kubuntu','distributor-logo-linuxmint','distributor-logo-lubuntu','distributor-logo-mageia','distributor-logo-manjaro',
 'distributor-logo-neon','distributor-logo-opensuse','distributor-logo-pop','distributor-logo-rhel','distributor-logo-ubuntu',
 'dropbox','hitori','krdc','ktorrent','kturtle','marsshooter','masterpdfeditor','maxthon-browser','navicat',
 'network-wireless-connected','network-wireless-disconnected','network-wireless-hotspot','notification-microphone',
 'notification-network-wireless','pairs','pcbcalculator','pdfeditor','phatch-inspector','preferences-desktop-theme-window',
 'preferences-web-browser-cookies','pushbullet-indicator','qreator','qtractor','rapidsvn','rclone-browser','regedit','resharper',
 'riot-web','scantailor','scanner','session-properties','software-properties','software-store','sound','spotify','steam',
 'subtitleeditor','texmaker','thermal-monitor','torcs','tortoisehg','touchpad-indicator','transmission','ue4editor','unity-editor-icon',
 'usb-creator','utilities-system-monitor','victor-vran','vidcutter','web-browser','webtorrent-desktop','wesnoth_editor','wordpress',
 'wps-office-pdf','yandex-browser','4kslideshowmaker'
]

def is_blacklisted(base):
    bl = base.lower()
    if bl.startswith('kali-'):
        return False
    if bl == 'distributor-logo-kali':
        return False
    for s in black_sub:
        if s in bl:
            return True
    return False

candidates = []
for p in paths:
    b = normbase(p)
    if b in existing or b.replace('-','') in {e.replace('-','') for e in existing}:
        continue
    bl = b.lower()
    is_kali = bl.startswith('kali-') or bl == 'distributor-logo-kali'
    is_hack = is_kali or any(k in bl for k in hack_kw)
    if not is_hack:
        continue
    if is_blacklisted(bl):
        continue
    candidates.append(p)

candidates = sorted(set(candidates))

def valid_img(data, suffix):
    if len(data) < 60: return False
    h = data[:512].lstrip().lower()
    if suffix == '.svg':
        return b'<svg' in h or b'<?xml' in h
    if suffix == '.png':
        return data.startswith(b'\x89PNG\r\n\x1a\n')
    return b'<svg' in h or b'<?xml' in h or data.startswith(b'\x89PNG')

results = []
for p in candidates:
    name = p.split('/')[-1]
    base = p.rsplit('.',1)[0].split('/')[-1]
    suf = '.' + name.rsplit('.',1)[-1].lower()
    out_name = (base.lower().replace('_','-')) + suf
    dest = SEC / out_name
    if dest.exists():
        results.append((out_name,'EXISTS',p))
        continue
    url = BASE + urllib.parse.quote(p)
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'logo-fetcher/1.0'})
        with urllib.request.urlopen(req, timeout=25) as r:
            data = r.read()
        if not valid_img(data, suf):
            results.append((out_name,'FAIL','invalid '+p))
            continue
        dest.write_bytes(data)
        results.append((out_name,'DOWNLOADED',f'{len(data)}b {p}'))
    except Exception as e:
        results.append((out_name,'FAIL',f'{e} {p}'))

ok = sum(1 for r in results if r[1] in ('DOWNLOADED','EXISTS'))
print(f'CAND={len(candidates)} OK={ok}')
for r in results:
    print('|'.join(r))
