import sys
sys.path.insert(0, "/tmp/kilo")
import convert2 as C

ROOT = C.ROOT
TGT = C.TGT

RESTORED_DIFFLIB = [
 ("/linux-investigation/LINUX-ENUMERATION-INVESTIGATION/linux-enumeration-investigation-id.md",
  "/LINUX-INVESTIGATION-FLOW/LINUX-ENUMERATION-INVESTIGATION/linux-enumeration-investigation-id.md"),
 ("/linux-post-exploitation/POST-EXPLOITATION-ENUMERATION/post-exploitation-enum-id.md",
  "/LINUX-ATTACK-CHAIN/POST-EXPLOITATION-ENUMERATION/post-exploitation-enum-id.md"),
 ("/linux-post-exploitation/POST-EXPLOITATION-FILE-SYSTEM-EXPLORE/post-exploitation-filesystemexplore-id.md",
  "/LINUX-ATTACK-CHAIN/POST-EXPLOITATION-FILE-SYSTEM-EXPLORE/post-exploitation-filesystemexplore-id.md"),
 ("/linux-post-exploitation/POST-EXPLOITATION-FOOTHOLD/post-exploitation-foothold-id.md",
  "/LINUX-ATTACK-CHAIN/POST-EXPLOITATION-FOOTHOLD/post-exploitation-foothold-id.md"),
 ("/linux-post-exploitation/POST-EXPLOITATION-LATERAL-MOVEMENT/post-exploitation-lateral-movement-id.md",
  "/LINUX-ATTACK-CHAIN/POST-EXPLOITATION-LATERAL-MOVEMENT/post-exploitation-lateral-movement-id.md"),
 ("/linux-post-exploitation/POST-EXPLOITATION-PERSISTENT/post-exploitation-persistence-id.md",
  "/LINUX-ATTACK-CHAIN/POST-EXPLOITATION-PERSISTENT/post-exploitation-persistence-id.md"),
 ("/linux-post-exploitation/POST-EXPLOITATION-PIVOTING/post-exploitation-pivoting-id.md",
  "/LINUX-ATTACK-CHAIN/POST-EXPLOITATION-PIVOTING/post-exploitation-pivoting-id.md"),
 ("/linux-post-exploitation/POST-EXPLOITATION-PRIVILEGE-ENUMERATION/post-exploitation-priv-enum-id.md",
  "/LINUX-ATTACK-CHAIN/POST-EXPLOITATION-PRIVILEGE-ENUMERATION/post-exploitation-priv-enum-id.md"),
 ("/linux-post-exploitation/POST-EXPLOITATION-PRIVILEGE-ESCALATION/post-exploitation-priv-esca-copyfail-id.md",
  "/LINUX-ATTACK-CHAIN/POST-EXPLOITATION-PRIVILEGE-ESCALATION/post-exploitation-priv-esca-copyfail-id.md"),
 ("/web-security/COMMAND-INJECTION-REVERSE-SHELL/command-injection-reverse-shell-id.md",
  "/LINUX-ATTACK-CHAIN/COMMAND-INJECTION-REVERSE-SHELL/command-injection-reverse-shell-id.md"),
 ("/web-security/WEBSHELL-REVERSE-SHELL/webshell-reverse-shell-id.md",
  "/LINUX-ATTACK-CHAIN/WEBSHELL-REVERSE-SHELL/webshell-reverse-shell-id.md"),
]

FLOW_USER_TXT = """User
  ↓
Terminal
  ↓
Login Time
  ↓
Source Address"""

FLOW_USER = """```mermaid
flowchart TD
    A["User"]
    B["Terminal"]
    C["Login Time"]
    D["Source Address"]

    A --> B --> C --> D

    classDef user fill:#e8f1ff,stroke:#2563eb,color:#172554,stroke-width:2px
    classDef session fill:#fff4e5,stroke:#ea580c,color:#7c2d12,stroke-width:2px
    classDef evidence fill:#ecfdf5,stroke:#059669,color:#064e3b,stroke-width:2px

    class A,B user
    class C session
    class D evidence
```"""

PIV_FLOW_ID_TXT = """Compromised Host
        │
        ▼
Network Enumeration
        │
        ▼
Create SOCKS5 Tunnel
        │
        ▼
Route Traffic via Pivot Host
        │
        ▼
Internal Network Discovery
        │
        ▼
Service Enumeration"""

PIV_FLOW_ID = """```mermaid
flowchart TD
    A["Compromised Host"]
    B["Network Enumeration"]
    C["Create SOCKS5 Tunnel"]
    D["Route Traffic via Pivot Host"]
    E["Internal Network Discovery"]
    F["Service Enumeration"]

    A --> B --> C --> D --> E --> F

    classDef entry fill:#e8f1ff,stroke:#2563eb,color:#172554,stroke-width:2px
    classDef tunnel fill:#fff4e5,stroke:#ea580c,color:#7c2d12,stroke-width:2px
    classDef discovery fill:#ecfdf5,stroke:#059669,color:#064e3b,stroke-width:2px

    class A entry
    class B,C,D tunnel
    class E,F discovery
```"""

PRIVESC_BOX_ID_TXT = """+----------------------+        +----------------------+
|     Kali Linux       |        |    Ubuntu Server     |
|      ATTACKER        | <----- |       TARGET         |
|                      |        |                      |
|  Reverse Shell       |        |  www-data            |
|  10.10.10.149        |        |  Linux Kernel        |
+----------------------+        +----------------------+
                                      │
                                      ▼
                              Copy.Fail
                              CVE-2026-31431
                                      │
                                      ▼
                                    root"""

PRIVESC_WWW_TXT = """www-data
    │
    ▼
  root"""

PRIVESC_FLOW_TXT = """Command Injection
        │
        ▼
Reverse Shell
        │
        ▼
www-data
        │
        ▼
Kernel Exploit
        │
        ▼
root"""

PRIVESC_BOX = """```mermaid
flowchart LR
    K["Kali Linux<br/>ATTACKER<br/>Reverse Shell<br/>10.10.10.149"]
    T["Ubuntu Server<br/>TARGET<br/>www-data<br/>Linux Kernel"]

    T -->|"Reverse Shell"| K
    T --> C["Copy.Fail<br/>CVE-2026-31431"]
    C --> R["root"]

    classDef attacker fill:#e8f1ff,stroke:#2563eb,color:#172554,stroke-width:2px
    classDef target fill:#fff4e5,stroke:#ea580c,color:#7c2d12,stroke-width:2px
    classDef exploit fill:#fef2f2,stroke:#dc2626,color:#7f1d1d,stroke-width:2px
    classDef result fill:#dcfce7,stroke:#16a34a,color:#14532d,stroke-width:2px

    class K attacker
    class T target
    class C exploit
    class R result
```"""

PRIVESC_WWW = """```mermaid
flowchart LR
    A["www-data"] --> B["root"]

    classDef user fill:#e8f1ff,stroke:#2563eb,color:#172554,stroke-width:2px
    classDef result fill:#dcfce7,stroke:#16a34a,color:#14532d,stroke-width:2px

    class A user
    class B result
```"""

PRIVESC_FLOW = """```mermaid
flowchart TD
    A["Command Injection"]
    B["Reverse Shell"]
    C["www-data"]
    D["Kernel Exploit"]
    E["root"]

    A --> B --> C --> D --> E

    classDef entry fill:#e8f1ff,stroke:#2563eb,color:#172554,stroke-width:2px
    classDef execution fill:#fff4e5,stroke:#ea580c,color:#7c2d12,stroke-width:2px
    classDef exploit fill:#fef2f2,stroke:#dc2626,color:#7f1d1d,stroke-width:2px
    classDef result fill:#dcfce7,stroke:#16a34a,color:#14532d,stroke-width:2px

    class A,B entry
    class C execution
    class D exploit
    class E result
```"""

LAT_FLOW_TXT = """Attacker
     │
     │ Proxychains (SOCKS5)
     ▼
Ubuntu Server01 (Pivot Host)
     │
     │ Forward Internal Traffic
     ▼
Debian Server02
     │
     │ Samba Print Subsystem
     ▼
CVE-2026-4480 Triggered
     │
     │ Reverse Connection
     ▼
Ubuntu Server01 (SOCAT Relay)
     │
     ▼
Attacker Listener"""

LAT_FLOW = """```mermaid
flowchart TD
    A["Attacker"]
    B["Ubuntu Server01 (Pivot Host)"]
    C["Debian Server02"]
    D["CVE-2026-4480 Triggered"]
    E["Ubuntu Server01 (SOCAT Relay)"]
    F["Attacker Listener"]

    A -->|"Proxychains (SOCKS5)"| B
    B -->|"Forward Internal Traffic"| C
    C -->|"Samba Print Subsystem"| D
    D -->|"Reverse Connection"| E
    E --> F

    classDef attacker fill:#e8f1ff,stroke:#2563eb,color:#172554,stroke-width:2px
    classDef pivot fill:#fff4e5,stroke:#ea580c,color:#7c2d12,stroke-width:2px
    classDef target fill:#ecfdf5,stroke:#059669,color:#064e3b,stroke-width:2px
    classDef exploit fill:#fef2f2,stroke:#dc2626,color:#7f1d1d,stroke-width:2px

    class A,F attacker
    class B,E pivot
    class C target
    class D exploit
```"""

CMD_FLOW_TXT = """Command Injection
        │
        ▼
Command Execution
        │
        ▼
Reverse Shell Payload
        │
        ▼
Outbound Connection
        │
        ▼
Interactive Shell"""

CMD_FLOW = """```mermaid
flowchart TD
    A["Command Injection"]
    B["Command Execution"]
    C["Reverse Shell Payload"]
    D["Outbound Connection"]
    E["Interactive Shell"]

    A --> B --> C --> D --> E

    classDef entry fill:#e8f1ff,stroke:#2563eb,color:#172554,stroke-width:2px
    classDef execution fill:#fff4e5,stroke:#ea580c,color:#7c2d12,stroke-width:2px
    classDef shell fill:#dcfce7,stroke:#16a34a,color:#14532d,stroke-width:2px

    class A,B entry
    class C,D execution
    class E shell
```"""

WS_FLOW_TXT = """Unsafe File Upload
        │
        ▼
   Webshell Upload
        │
        ▼
  Webshell Execution
        │
        ▼
  Command Execution
        │
        ▼
Reverse Shell Payload
        │
        ▼
 Outbound Connection
        │
        ▼
  Interactive Shell"""

WS_BOX_TXT = """+-------------------------------------------------+
|              LAB - 10.10.10.0/24                |
|                                                 |
|  +---------------+      +-------------------+   |
|  |  Kali Linux   |      |   Ubuntu Server   |   |
|  |  [ATTACKER]   |      |   [TARGET WEB]    |   |
|  |  Listener     | <--- |   Webshell        |   |
|  | 10.10.10.149  |      |   10.10.10.2      |   |
|  |   Port 9001   |      |   bWAPP           |   |
|  +---------------+      +-------------------+   |
|          ^                      |               |
|          |                      |               |
|          +--- Reverse Shell ----+               |
+-------------------------------------------------+"""

EXTRAS = [
 ("/linux-investigation/LINUX-ENUMERATION-INVESTIGATION/linux-enumeration-investigation-id.md",
  [(FLOW_USER_TXT, FLOW_USER)]),
 ("/linux-post-exploitation/POST-EXPLOITATION-LATERAL-MOVEMENT/post-exploitation-lateral-movement-id.md",
  [(LAT_FLOW_TXT, LAT_FLOW)]),
 ("/linux-post-exploitation/POST-EXPLOITATION-PIVOTING/post-exploitation-pivoting-id.md",
  [(PIV_FLOW_ID_TXT, PIV_FLOW_ID)]),
 ("/linux-post-exploitation/POST-EXPLOITATION-PRIVILEGE-ESCALATION/post-exploitation-priv-esca-copyfail-id.md",
  [(PRIVESC_BOX_ID_TXT, PRIVESC_BOX), (PRIVESC_WWW_TXT, PRIVESC_WWW), (PRIVESC_FLOW_TXT, PRIVESC_FLOW)]),
 ("/web-security/COMMAND-INJECTION-REVERSE-SHELL/command-injection-reverse-shell-id.md",
  [(CMD_FLOW_TXT, CMD_FLOW)]),
]


def apply_extras(rel, rules):
    path = TGT + rel
    tl = C.lines_of(C.read(path))
    for txt, mer in rules:
        if not C.replace_text_block(tl, txt, mer):
            print("   !! block not found in", rel)
    C.write(path, "".join(tl))


def webshell_en():
    src = ROOT + "/LINUX-ATTACK-CHAIN/WEBSHELL-REVERSE-SHELL/webshell-reverse-shell-id.md"
    sl = C.lines_of(C.read(src))
    mers = [l.rstrip("\r\n") for (a, b, ism) in C.fenced_blocks(sl) if ism for l in sl[a:b]]
    blocks = []
    for (a, b, ism) in C.fenced_blocks(sl):
        if ism:
            blocks.append([l.rstrip("\r\n") for l in sl[a:b]])
    path = TGT + "/web-security/WEBSHELL-REVERSE-SHELL/webshell-reverse-shell-en.md"
    tl = C.lines_of(C.read(path))
    # find diagram text blocks in order
    idxs = []
    i = 0
    while i < len(tl):
        if C.TEXT_OPEN.match(tl[i]):
            j = i + 1
            while j < len(tl) and not C.FENCE.match(tl[j]):
                j += 1
            content = C.norm(tl[i + 1:j])
            if any(ch in "\n".join(content) for ch in "│▼▲┌┐└┘├┤┬┴┼─↓↑→←") or any(
                    l.startswith("+---") for l in content):
                idxs.append((i, j))
            i = j + 1
        else:
            i += 1
    if len(idxs) != len(blocks):
        print("   !! webshell-en diagram count %d != source mermaid %d" % (len(idxs), len(blocks)))
        return
    for (i, j), blk in zip(reversed(idxs), reversed(blocks)):
        eol = C.eol_of(tl[i])
        tl[i:j + 1] = [l + eol for l in blk]
    C.write(path, "".join(tl))
    print("   webshell-en: %d blocks" % len(blocks))


def main():
    for rel, src in RESTORED_DIFFLIB:
        n = C.difflib_convert(TGT + rel, ROOT + src)
        print("%-2d %s" % (n, rel))
    for rel, rules in EXTRAS:
        apply_extras(rel, rules)
        print("extras", rel)
    webshell_en()
    print("done")


if __name__ == "__main__":
    main()