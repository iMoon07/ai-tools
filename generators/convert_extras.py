import re, os

TGT = "/home/moon/Projects/Penjelajah-CyberSecurity/Experiments"

ENUM = "linux-investigation/LINUX-ENUMERATION-INVESTIGATION/"
PIV = "linux-post-exploitation/POST-EXPLOITATION-PIVOTING/"
PRIVESC = "linux-post-exploitation/POST-EXPLOITATION-PRIVILEGE-ESCALATION/"
LAT = "linux-post-exploitation/POST-EXPLOITATION-LATERAL-MOVEMENT/"
WS = "web-security/WEBSHELL-REVERSE-SHELL/"
CMD = "web-security/COMMAND-INJECTION-REVERSE-SHELL/"

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

PIV_BOX = """```mermaid
flowchart LR
    K["Kali Linux<br/>10.10.10.149<br/>AdaptixC2"]
    U["Ubuntu Server01<br/>Pivot Host<br/>AdaptixC2 Agent<br/>ens33: 10.10.10.2<br/>ens37: 192.168.15.3"]
    D["Debian Server02<br/>192.168.15.2<br/>Internal Host"]

    K -->|"Attacker Network<br/>10.10.10.0/24"| U
    U -->|"Internal Network<br/>192.168.15.0/24"| D

    classDef attacker fill:#e8f1ff,stroke:#2563eb,color:#172554,stroke-width:2px
    classDef pivot fill:#fff4e5,stroke:#ea580c,color:#7c2d12,stroke-width:2px
    classDef target fill:#ecfdf5,stroke:#059669,color:#064e3b,stroke-width:2px

    class K attacker
    class U pivot
    class D target
```"""

PIV_ENUM = """```mermaid
flowchart TD
    A["Network Enumeration"]
    B["Identify Reachable Hosts"]
    C["Discover Available Services"]

    A --> B --> C

    classDef stage fill:#e8f1ff,stroke:#2563eb,color:#172554,stroke-width:2px

    class A,B,C stage
```"""

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

WS_FLOW = """```mermaid
flowchart TD
    A["Unsafe File Upload"]
    B["Webshell Upload"]
    C["Webshell Execution"]
    D["Command Execution"]
    E["Reverse Shell Payload"]
    F["Outbound Connection"]
    G["Interactive Shell"]

    A --> B --> C --> D --> E --> F --> G

    classDef entry fill:#e8f1ff,stroke:#2563eb,color:#172554,stroke-width:2px
    classDef upload fill:#fff4e5,stroke:#ea580c,color:#7c2d12,stroke-width:2px
    classDef execution fill:#ecfdf5,stroke:#059669,color:#064e3b,stroke-width:2px
    classDef shell fill:#dcfce7,stroke:#16a34a,color:#14532d,stroke-width:2px

    class A entry
    class B,C upload
    class D,E,F execution
    class G shell
```"""

WS_BOX = """```mermaid
flowchart TB
    subgraph LAB["LAB / VMware - 10.10.10.0/24"]
        direction LR

        A["Kali Linux<br/>ATTACKER<br/><br/>10.10.10.149<br/>Listener: Port 9001"]

        T["Ubuntu Server<br/>TARGET WEB<br/><br/>10.10.10.2<br/>bWAPP<br/>Webshell"]

        T -->|"Reverse Shell<br/>Outbound Connection"| A
    end

    classDef attacker fill:#e8f1ff,stroke:#2563eb,color:#172554,stroke-width:2px
    classDef target fill:#fff4e5,stroke:#ea580c,color:#7c2d12,stroke-width:2px

    class A attacker
    class T target
```"""

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

FLOW_USER_TXT = """User
  ↓
Terminal
  ↓
Login Time
  ↓
Source Address"""

PIV_BOX_TXT = """+----------------+          +----------------------+          +----------------+
| Kali Linux     |          | Ubuntu Server01      |          | Debian Server02|
| 10.10.10.149   |--------->| Pivot Host           |--------->| 192.168.15.2   |
| AdaptixC2      |          | AdaptixC2 Agent      |          | Internal Host  |
+----------------+          |                      |          +----------------+
                            | ens33 : 10.10.10.2   |
                            | ens37 : 192.168.15.3 |
                            +----------------------+

         Attacker Network                 Internal Network
            10.10.10.0/24                  192.168.15.0/24"""

PIV_ENUM_TXT = """Network Enumeration
        │
        ▼
Identify Reachable Hosts
        │
        ▼
Discover Available Services"""

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

PRIVESC_BOX_TXT = """+----------------------+        +----------------------+
|      Kali Linux      |        |    Ubuntu Server     |
|       ATTACKER       | <----- |       TARGET         |
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

RULES = [
 (ENUM + "linux-enumeration-investigation-en.md", [(FLOW_USER_TXT, FLOW_USER)]),
 (ENUM + "linux-enumeration-investigation-id.md", [(FLOW_USER_TXT, FLOW_USER)]),
 (PIV + "post-exploitation-pivoting-en.md", [(PIV_BOX_TXT, PIV_BOX), (PIV_ENUM_TXT, PIV_ENUM)]),
 (PIV + "post-exploitation-pivoting-id.md", [(PIV_FLOW_ID_TXT, PIV_FLOW_ID)]),
 (PRIVESC + "post-exploitation-priv-esca-copyfail-en.md", [(PRIVESC_BOX_TXT, PRIVESC_BOX), (PRIVESC_WWW_TXT, PRIVESC_WWW), (PRIVESC_FLOW_TXT, PRIVESC_FLOW)]),
 (PRIVESC + "post-exploitation-priv-esca-copyfail-id.md", [(PRIVESC_BOX_ID_TXT, PRIVESC_BOX), (PRIVESC_WWW_TXT, PRIVESC_WWW), (PRIVESC_FLOW_TXT, PRIVESC_FLOW)]),
 (LAT + "post-exploitation-lateral-movement-en.md", [(LAT_FLOW_TXT, LAT_FLOW)]),
 (LAT + "post-exploitation-lateral-movement-id.md", [(LAT_FLOW_TXT, LAT_FLOW)]),
 (WS + "webshell-reverse-shell-en.md", [(WS_FLOW_TXT, WS_FLOW), (WS_BOX_TXT, WS_BOX)]),
 (CMD + "command-injection-reverse-shell-en.md", [(CMD_FLOW_TXT, CMD_FLOW)]),
 (CMD + "command-injection-reverse-shell-id.md", [(CMD_FLOW_TXT, CMD_FLOW)]),
]

for rel, pairs in RULES:
    path = os.path.join(TGT, rel)
    t = open(path, encoding="utf-8").read()
    for txt, mer in pairs:
        old = "```text\n" + txt + "\n```"
        n = t.count(old)
        if n != 1:
            print("!! %s: found %d occurrences of block (expected 1)" % (rel, n))
            continue
        t = t.replace(old, mer)
    open(path, "w", encoding="utf-8").write(t)
print("done")