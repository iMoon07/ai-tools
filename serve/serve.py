#!/usr/bin/env python3
"""Static preview server for local testing.

Satu perintah untuk semua repo: situs di /, dokumen markdown di /docs/, dan
opsi HTTPS supaya service worker / kamera / clipboard bisa diuji di localhost.

  python3 ai-tools/serve/serve.py                # http  pada 0.0.0.0:8080
  python3 ai-tools/serve/serve.py --port 8443 --tls
  python3 ai-tools/serve/serve.py --host 127.0.0.1 --no-docs

URL:
  http://localhost:8080/read.html
  http://localhost:8080/read.html?url=/docs/Experiments/.../file-en.md
  https://localhost:8443/...            (sertifikat self-signed, --tls)
"""
import argparse
import http.server
import os
import socket
import socketserver
import ssl
import subprocess
import sys
import threading
from functools import partial

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, "imoon07.github.io")
DOCS = os.path.join(ROOT, "Penjelajah-CyberSecurity")


class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = path.split("?", 1)[0].split("#", 1)[0]
        if path.startswith("/docs/"):
            rel = path[len("/docs/"):]
            return os.path.normpath(os.path.join(DOCS, rel))
        return super().translate_path(path)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def make_cert(directory):
    key = os.path.join(directory, "key.pem")
    crt = os.path.join(directory, "cert.pem")
    if os.path.exists(crt):
        return crt, key
    subj = "/CN=localhost"
    alt = "DNS:localhost,IP:127.0.0.1"
    cmd = ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
           "-keyout", key, "-out", crt, "-days", "365", "-subj", subj,
           "-addext", f"subjectAltName={alt}"]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    return crt, key


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--tls", action="store_true")
    ap.add_argument("--no-docs", action="store_true")
    args = ap.parse_args()

    if args.no_docs:
        Handler.translate_path = http.server.SimpleHTTPRequestHandler.translate_path
    os.chdir(SITE)

    srv = Server((args.host, args.port), partial(Handler, directory=SITE))
    if args.tls:
        cert_dir = "/tmp/alur-probes"
        os.makedirs(cert_dir, exist_ok=True)
        crt, key = make_cert(cert_dir)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(crt, key)
        srv.socket = ctx.wrap_socket(srv.socket, server_side=True)

    scheme = "https" if args.tls else "http"
    ip = lan_ip()
    print(f"site  : {scheme}://localhost:{args.port}/", flush=True)
    print(f"docs  : {scheme}://localhost:{args.port}/docs/", flush=True)
    if not args.no_docs:
        print(f"        {scheme}://{ip}:{args.port}/docs/  (LAN)", flush=True)
    print(f"lan   : {scheme}://{ip}:{args.port}/", flush=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()