# serve/

Satu perintah untuk preview semua repo sekaligus, plus HTTPS kalau butuh
origin aman (service worker, kamera, clipboard, `crypto.subtle`).

```bash
python3 ai-tools/serve/serve.py                    # http  → :8080
python3 ai-tools/serve/serve.py --port 8123
python3 ai-tools/serve/serve.py --port 8443 --tls   # https (self-signed)
python3 ai-tools/serve/serve.py --host 127.0.0.1 --no-docs
```

## Peta URL

| Path | Isi |
| --- | --- |
| `/` | `imoon07.github.io/` (situs) |
| `/docs/…` | `Penjelajah-CyberSecurity/…` (markdown + gambar) |

Jadi artikel bisa diuji same-origin, tanpa CORS dan tanpa raw.githubusercontent:

```
http://localhost:8123/read.html
http://localhost:8123/read.html?url=/docs/Experiments/foundations/server-architecture/server-single-tier-stack-en.md
http://localhost:8123/blog.html
```

## HTTPS

`--tls` membuat cert self-signed di `/tmp/kilo/{cert,key}.pem` (CN=localhost,
SAN `DNS:localhost,IP:127.0.0.1`) dan memakainya ulang selama file masih ada.
Browser akan memperingatkan sekali; klik *Advanced → Proceed*. Untuk akses dari
HP/LAN, buka `https://<ip-lan>:8443/` dan tambahkan `--host 0.0.0.0` (default).

## Catatan

- `Cache-Control: no-store` supaya perubahan `js/*.js` selalu terbaca ulang.
- Bind default `0.0.0.0`: `localhost`, `127.0.0.1`, dan IP LAN semua jalan.
- Port bentrok → ganti `--port`, atau `ss -ltnp | grep <port>`.