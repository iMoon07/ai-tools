#!/usr/bin/env python3
"""Sort the security-enterprise folder into sub-groups.

The flat folder grew past 250 files, so every mark now lives in a group that
says what the product actually is:

  siem/  siem, log analytics, soar, soc platforms
  tip/   threat intelligence, brand protection, exposure intel
  ids-ips/ ids, ips, ndr, network detection
  waf/   waf, cdn, edge protection
  iam/   identity, sso, pam, secrets, password managers
  xdr-edr/ edr, xdr, mdr, mss
  cloud/ cloud, container, kubernetes, cspm, cnapp
  appsec/ sast, dast, sca, secrets scanning, supply chain
  pentest/ pentest platforms, red team, c2, bug bounty
  forensics/ forensics, ir, malware analysis, reverse engineering
  email/ email security
  grc/  compliance, risk, audit
  data-security/ dspm, dlp, data discovery
  fraud/ identity verification and fraud
  network/ firewalls, ndr appliances, network vendors
  endpoint/ endpoint protection and device control
  misc/  anything that fits nowhere else

Usage:
  python3 ai-tools/generators/regroup_company_logos.py --logo-dir /home/moon/Projects/logo
  python3 ai-tools/generators/regroup_company_logos.py --dry-run
"""
import argparse
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

DEFAULT_LOGO = Path("/home/moon/Projects/logo")
GROUPS = ("siem", "tip", "ids-ips", "waf", "iam", "xdr-edr", "cloud", "appsec",
          "pentest", "forensics", "e-discovery", "email", "grc", "data-security",
          "fraud", "network", "endpoint", "misc")

# slug -> group. Anything missing falls through to the keyword rules below.
EXPLICIT = {
    # siem / soar
    "splunk-soar": "siem", "microsoft-sentinel": "siem", "google-secops": "siem",
    "qradar": "siem", "arcsight": "siem", "logpoint": "siem", "sumo-logic": "siem",
    "chronicle": "siem", "elastic-siem": "siem", "elastic-security": "xdr-edr",
    "cribl": "siem", "scalyr": "siem", "humio": "siem", "logz-io": "siem",
    "mezmo": "siem", "papertrail": "siem", "panther": "siem", "exabeam": "siem",
    "securonix": "siem", "devo": "siem", "splunk": "siem",
    # threat intelligence
    "misp": "tip", "opencti": "tip", "anomali": "tip", "recorded-future": "tip",
    "recorded-future-2": "tip", "flashpoint": "tip", "flashpoint-2": "tip",
    "threatconnect": "tip", "threatquotient": "tip", "intel-471": "tip",
    "cybersixgill": "tip", "darkowl": "tip", "dataminr": "tip",
    "lookingglass": "tip", "eclypsium": "tip", "cybelangel": "tip",
    "bolster": "tip", "kela": "tip", "blight": "tip", "zerofox": "tip",
    "shodan": "tip", "censys": "tip",
    # ids / ips / ndr
    "alert-logic": "ids-ips", "arbor-networks": "ids-ips", "stamus": "ids-ips",
    "selks": "ids-ips", "malcolm": "ids-ips", "lastline": "ids-ips",
    "ironnet": "ids-ips", "cisco-firepower": "ids-ips", "cisco-securex": "ids-ips",
    "cisco-secure": "ids-ips", "darktrace": "ids-ips", "vectra": "ids-ips",
    "corelight": "ids-ips", "extrahop": "ids-ips", "netscout": "ids-ips",
    "tufin": "ids-ips", "algosec": "ids-ips", "tripwire": "ids-ips",
    "netresec": "ids-ips",
    # waf / cdn
    "cloudflare": "waf", "wordfence": "waf", "sucuri": "waf", "stackpath": "waf",
    "signal-sciences": "waf", "wallarm": "waf", "aws-waf": "waf",
    "azure-front-door": "waf", "gcore": "waf", "section-io": "waf",
    "edgecast": "waf", "edgio": "waf", "imperva": "waf", "imperva-waf": "waf",
    "modshield": "waf", "barikode": "waf", "naxsi": "waf", "shadowd": "waf",
    "libinjection": "waf",
    # identity
    "auth0": "iam", "onelogin": "iam", "jumpcloud": "iam", "zitadel": "iam",
    "ory": "iam", "fusionauth": "iam", "keycloak": "iam", "openiam": "iam",
    "midpoint": "iam", "microsoft-entra": "iam", "rsa-securid": "iam",
    "thales-safenet": "iam", "hid-digitalpersona": "iam", "silverfort": "iam",
    "semperis": "iam", "authomize": "iam", "authomize-2": "iam", "veza": "iam",
    "empowerid": "iam", "helloid": "iam", "okta-asa": "iam", "ping-da": "iam",
    "ping-identity": "iam", "cyberark": "iam", "cyberark-conjur": "iam",
    "beyondtrust": "iam", "delinea": "iam", "delinea-secret-server": "iam",
    "strongdm": "iam", "akeyless": "iam", "one-identity": "iam",
    "sailpoint": "iam", "saviynt": "iam", "keeper-security": "iam",
    "dashlane": "iam", "1password": "iam", "hashicorp-vault": "iam",
    "aws-secrets-manager": "iam", "azure-key-vault": "iam",
    "gcp-secret-manager": "iam", "okta": "iam",
    # edr / xdr / mdr
    "sentinelone": "xdr-edr", "cortex-xdr": "xdr-edr", "cortex-xsoar": "xdr-edr",
    "palo-alto-cortex": "xdr-edr", "trend-micro": "xdr-edr", "eset": "xdr-edr",
    "eset-protect": "xdr-edr", "withsecure": "xdr-edr", "huntress": "xdr-edr",
    "cylance": "xdr-edr", "carbon-black": "xdr-edr", "cybereason": "xdr-edr",
    "tanium": "xdr-edr", "threatlocker": "xdr-edr", "f-secure": "xdr-edr",
    "ahnlab": "xdr-edr", "gdata": "xdr-edr", "comodo": "xdr-edr",
    "kasm": "xdr-edr", "arctic-wolf": "xdr-edr", "red-canary": "xdr-edr",
    "expel": "xdr-edr", "critical-start": "xdr-edr", "deepwatch": "xdr-edr",
    "esentire": "xdr-edr", "reliaquest": "xdr-edr", "binary-defense": "xdr-edr",
    "proficio": "xdr-edr", "defender-for-cloud": "cloud",
    # cloud / container
    "wiz": "cloud", "orca": "cloud", "orca-security": "cloud",
    "aqua-security": "cloud", "sysdig": "cloud", "lacework": "cloud",
    "armo": "cloud", "upwind": "cloud", "cyscale": "cloud", "kubescape": "cloud",
    "kubearmor": "cloud", "sweet-security": "cloud", "dig-security": "cloud",
    "gem-security": "cloud", "token-security": "cloud", "aim-security": "cloud",
    "noname-security": "cloud", "salt-security": "cloud", "traceable": "cloud",
    "stacklet": "cloud", "capsule8": "cloud", "inland": "cloud",
    "ermetic": "cloud", "er metic": "cloud", "prisma-cloud": "cloud", "aws-security-hub": "cloud",
    "guardduty": "cloud", "aws-inspector": "cloud", "inspector-2": "cloud",
    "security-command-center": "cloud", "cloudrise": "cloud",
    # appsec
    "checkmarx": "appsec", "veracode": "appsec", "blackduck": "appsec",
    "mend": "appsec", "aikido": "appsec", "socket": "appsec", "socket-2": "appsec",
    "socket-security": "appsec", "contrast-security": "appsec", "stackhawk": "appsec",
    "gitleaks": "appsec", "trufflehog": "appsec", "detect-secrets": "appsec",
    "gitguardian": "appsec", "spectral": "appsec", "opengrep": "appsec",
    "osv-scanner": "appsec", "dependency-check": "appsec",
    "dependency-track": "appsec", "semgrep": "appsec", "fortify": "appsec",
    "synopsys": "appsec", "coverity": "appsec", "rapid7": "appsec",
    "appdeep": "appsec", "bearer": "appsec", "jericho": "appsec",
    "cycode": "appsec", "cycode-2": "appsec", "armorcode": "appsec",
    "legit-security": "appsec", "apiiro": "appsec", "endor-labs": "appsec",
    "phylum": "appsec", "invicti": "appsec", "acunetix": "appsec",
    # pentest / red team
    "cobalt-strike": "pentest", "brute-ratel": "pentest", "core-impact": "pentest",
    "outflank": "pentest", "scythe": "pentest", "picus-security": "pentest",
    "safebreach": "pentest", "sliver": "pentest", "mythic": "pentest",
    "empire": "pentest", "caldera": "pentest", "atomic-red-team": "pentest",
    "infection-monkey": "pentest", "stratus-red-team": "pentest",
    "cobalt-io": "pentest", "hackerone": "pentest", "bugcrowd": "pentest",
    "synack": "pentest", "yeswehack": "pentest", "intigriti": "pentest",
    "detectify": "pentest", "intruder": "pentest", "probely": "pentest",
    "immuniweb": "pentest", "pentest-tools": "pentest", "outpost24": "pentest",
    "holm-security": "pentest", "cycraft": "pentest",
    # forensics / malware analysis / re
    "magnet-forensics": "forensics", "magnet-axiom-2": "forensics",
    "axiom": "forensics", "encase": "forensics", "opentext": "forensics",
    "ftk": "forensics", "exterro": "forensics", "x-ways": "forensics",
    "belkasoft": "forensics", "cellebrite": "forensics", "cellebrite-2": "forensics",
    "oxygen-forensics": "forensics", "binalyze": "forensics",
    "accessdata": "forensics", "sumuri": "forensics", "nuix": "forensics",
    "msab-xry": "forensics", "passware": "forensics", "elcomsoft": "forensics",
    "anyrun": "forensics", "joe-sandbox": "forensics",
    "hybrid-analysis": "forensics", "cape-sandbox": "forensics",
    "ida-pro": "forensics", "binary-ninja": "forensics", "ghidra": "forensics",
    # email
    "proofpoint": "email", "mimecast": "email", "abnormal-security": "email",
    "material-security": "email", "hornetsecurity": "email", "avanan": "email",
    "perception-point": "email", "ironscales": "email", "spamhaus": "email",
    "mailprotector": "email", "valimail": "email", "agari": "email",
    "twilio-sendgrid": "email",
    # grc
    "vanta": "grc", "drata": "grc", "secureframe": "grc", "hyperproof": "grc",
    "auditboard": "grc", "logicgate": "grc", "servicenow-irm": "grc",
    "sprinto": "grc", "anecdotes": "grc", "thoropass": "grc", "safebase": "grc",
    "conveyor": "grc", "eramba": "grc", "onetrust": "grc",
    # data security
    "bigid": "data-security", "cyera": "data-security", "sentra": "data-security",
    "varonis": "data-security", "normalyze": "data-security",
    "polar-security": "data-security", "trusta": "data-security",
    "titaniam": "data-security",
    # fraud / identity verification
    "socure": "fraud", "alloy": "fraud", "persona": "fraud", "onfido": "fraud",
    "jumio": "fraud", "id-me": "fraud", "clear": "fraud",
    "adf-solutions": "forensics",
    "binary-ninja-cloud": "forensics",
    "capa": "forensics",
    "celebrite-mobile": "forensics",
    "cellebrite-cloud": "forensics",
    "cellebrite-pathfinder": "forensics",
    "cellebrite-premium": "forensics",
    "cellebrite-ufed": "forensics",
    "cuckoo": "forensics",
    "cybertriage": "forensics",
    "dfir-iris": "forensics",
    "dumpzilla": "forensics",
    "encase-endpoint": "forensics",
    "encase-enterprise": "forensics",
    "eric-zimmerman-tools": "forensics",
    "flare-floss": "forensics",
    "ftk-enterprise": "forensics",
    "ftk-lab": "forensics",
    "guidance-software": "forensics",
    "hindsight": "forensics",
    "hybrid-analysis-2": "forensics",
    "imhex": "forensics",
    "iris": "forensics",
    "katana-forensics": "forensics",
    "lantern": "forensics",
    "magnet-ai": "forensics",
    "magnet-respond": "forensics",
    "magnet-verdict": "forensics",
    "mandiant-advantage": "forensics",
    "mftecmd": "forensics",
    "mobiledit": "forensics",
    "mobiledit-forensic": "forensics",
    "mvt": "forensics",
    "nuix-discover": "forensics",
    "nuix-workstation": "forensics",
    "ontrack": "forensics",
    "oxygen-corporate": "forensics",
    "oxygen-detective": "forensics",
    "oxygen-phone-detective": "forensics",
    "paraben-e3": "forensics",
    "paraben-p2": "forensics",
    "pecmd": "forensics",
    "prodiscover": "forensics",
    "registry-explorer": "forensics",
    "remnux": "forensics",
    "remnux-2": "forensics",
    "r-studio": "forensics",
    "salvationdata": "forensics",
    "sandboxie": "forensics",
    "sift-workstation": "forensics",
    "sumuri-artifact": "forensics",
    "teel-technologies": "forensics",
    "timeline-explorer": "forensics",
    "ufs-explorer": "forensics",
    "velociraptor-ir": "forensics",
    "virustotal-2": "forensics",
    "volatility3": "forensics",
    "yara-x": "forensics",
    "yeti": "forensics",
    "yeti-2": "forensics",
    "alienvault": "tip",
    "intelowl": "tip",
    "opencti-2": "tip",
    "crowdstrike-falcon-x": "xdr-edr",
    "trustedsec": "pentest",
    "disco-e": "e-discovery",
    "everlaw": "e-discovery",
    "kcura": "e-discovery",
    "logikcull": "e-discovery",
    "relativity": "e-discovery",
    "onelog": "e-discovery",
    "exterro-review": "e-discovery",
    # network / firewall
    "ermetic": "cloud", "er metic": "cloud", "cortex-analyser": "siem", "ibm-resilient": "siem",
    "swimlane": "siem", "tines": "siem", "torq": "siem", "whitesource": "appsec",
    "datadog": "siem",
    "palo-alto-networks": "network", "fortigate": "network", "checkpoint": "network",
    "juniper-networks": "network", "watchguard": "network", "forcepoint": "network",
    "barracuda": "network", "radware": "network", "f5": "network",
}

# keyword fallbacks, checked in order
RULES = (
    ("siem", ("siem", "soar", "log-", "log-", "analytics", "soc")),
    ("waf", ("waf", "cdn", "edge")),
    ("iam", ("identity", "iam", "pam", "sso", "secret", "password", "key-vault")),
    ("xdr-edr", ("edr", "xdr", "mdr", "endpoint", "antivirus", "defender")),
    ("cloud", ("cloud", "kubernetes", "container", "cspm", "cnapp", "k8s")),
    ("appsec", ("appsec", "sast", "dast", "sca", "snyk", "code", "devsecops")),
    ("pentest", ("pentest", "red-team", "c2", "bug", "vulnerab")),
    ("forensics", ("forensic", "incident", "malware", "sandbox", "reverse", "dfir")),
    ("email", ("email", "mail")),
    ("grc", ("grc", "compliance", "risk", "audit")),
    ("data-security", ("dspm", "dlp", "data")),
    ("fraud", ("fraud", "verification", "identity-verif")),
    ("network", ("firewall", "network", "switch", "router", "proxy")),
    ("tip", ("threat", "intel", "recon", "osint")),
)


def group_for(slug):
    if slug in EXPLICIT:
        return EXPLICIT[slug]
    for group, keys in RULES:
        if any(k in slug for k in keys):
            return group
    return "misc"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--logo-dir", default=str(DEFAULT_LOGO))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = Path(args.logo_dir)
    src = root / "security-enterprise"
    if not src.is_dir():
        raise SystemExit("no security-enterprise folder in %s" % root)

    plan = defaultdict(list)
    for path in sorted(src.iterdir()):
        if not path.is_file():
            continue
        plan[group_for(path.stem.lower())].append(path)

    for group in GROUPS:
        files = plan.get(group, [])
        print("%-16s %3d  %s" % (group, len(files),
                                 " ".join(f.name for f in files[:6]) + (" ..." if len(files) > 6 else "")))

    unmapped = plan.get("misc", [])
    if unmapped:
        print("\nmisc (%d): %s" % (len(unmapped), " ".join(f.stem for f in unmapped)))

    if args.dry_run:
        print("\ndry-run, nothing moved")
        return

    for group, files in plan.items():
        target = src / group
        target.mkdir(parents=True, exist_ok=True)
        for path in files:
            shutil.move(str(path), str(target / path.name))
    print("\nmoved %d files into %d groups" % (sum(len(v) for v in plan.values()), len(plan)))


if __name__ == "__main__":
    main()