from pathlib import Path

en = Path('template-for-you-en.md').read_text()
start = en.index('### 18.8')
end = en.index('## Conclusion')
base = en[start:end].rstrip()

T = {
'id': {
 '### 18.8 Logo library — security tools': '### 18.8 Pustaka logo — tools keamanan',
 'All 575 logos from `iMoon07/logo-svg` are available to every node (`"logo": "security:nmap"`). This section groups the security catalogue by hacking phase: recon, exploitation, post-exploitation, and forensics. Every node is a tool; the logo is the catalogue entry.':
 'Semua 575 logo dari `iMoon07/logo-svg` tersedia untuk setiap node (`"logo": "security:nmap"`). Bagian ini mengelompokkan katalog keamanan menurut fase hacking: recon, eksploitasi, pasca-eksploitasi, dan forensik. Setiap node adalah tool; logo adalah entri katalog.',
 '#### Recon & enumeration': '#### Recon & enumerasi',
 'How to read: this is a gallery, not a flow. Each column is a recon phase. Top to bottom, the tools move from network discovery to DNS/OSINT to web enumeration. Every node is a tool; the logo is from the local security catalogue.':
 'Cara membaca: ini galeri, bukan alur. Setiap kolom adalah fase recon. Dari atas ke bawah, tool bergerak dari penemuan jaringan ke DNS/OSINT lalu enumerasi web. Setiap node adalah tool; logo berasal dari katalog keamanan lokal.',
 '#### Exploitation': '#### Eksploitasi',
 'How to read: this is a gallery, not a flow. Each column is an exploitation phase. Frameworks launch, web tools attack web targets, scanners find issues, and payloads deliver. The groups label the phase; the footer repeats the security context.':
 'Cara membaca: ini galeri, bukan alur. Setiap kolom adalah fase eksploitasi. Framework meluncurkan, tool web menyerang target web, scanner menemukan masalah, dan payload dikirim. Grup menandai fase; footer mengulang konteks keamanan.',
 '#### Post-exploitation': '#### Pasca-eksploitasi',
 'How to read: this is a gallery, not a flow. Each column is a post-exploitation phase. Credentials first, then lateral movement, password attacks, and wireless/MITM. Follow the group labels to keep the phases straight.':
 'Cara membaca: ini galeri, bukan alur. Setiap kolom adalah fase pasca-eksploitasi. Kredensial dulu, lalu pergerakan lateral, serangan kata sandi, dan wireless/MITM. Ikuti label grup agar fase tetap jelas.',
 '#### Forensics & reverse engineering': '#### Forensik & rekayasa balik',
 'How to read: this is a gallery, not a flow. Each column is an analysis phase. Disk artifacts, file carving, reverse engineering, and malware triage. Use the group labels to see which phase a tool belongs to.':
 'Cara membaca: ini galeri, bukan alur. Setiap kolom adalah fase analisis. Artefak disk, file carving, rekayasa balik, dan triase malware. Gunakan label grup untuk melihat fase sebuah tool.',
 '#### Network & wireless': '#### Jaringan & nirkabel',
 'How to read: this is a gallery, not a flow. Each column is a network phase. Capture and MITM first, then TLS, tunnels/anonymity, and wireless. The group labels keep the phases straight.':
 'Cara membaca: ini galeri, bukan alur. Setiap kolom adalah fase jaringan. Capture dan MITM dulu, lalu TLS, tunnel/anonimitas, dan wireless. Label grup menjaga fase tetap jelas.',
 '## 19 — Topology Visual Lab': '## 19 — Lab Visual Topologi',
 '`topology` is the static renderer for article diagrams. It has no toolbar, panel, or zoom: the diagram follows the article column width and stacks vertically on narrow screens. Node logos can use the local Alur catalogue (575 logos from iMoon07/logo-svg), for example `"icon": "security:nmap"`.':
 '`topology` adalah renderer statis untuk diagram artikel. Tidak ada toolbar, panel, atau zoom: diagram mengikuti lebar kolom artikel dan menumpuk secara vertikal di layar sempit. Logo node dapat memakai katalog Alur lokal (575 logo dari iMoon07/logo-svg), misalnya `"icon": "security:nmap"`.',
 '### 19.1 Restaurant as a server request': '### 19.1 Restoran sebagai permintaan server',
 'Read left → right. Solid arrows are the order/request path; the dashed arrow is the return/response. The footer repeats the direction legend and the place chips, so the picture is not just a picture.':
 'Baca dari kiri → kanan. Panah solid adalah jalur order/request; panah putus-putus adalah return/response. Footer mengulang legenda arah dan chip tempat, jadi gambarnya bukan sekadar gambar.',
 'How to read: `Customer → Waiter → Chef → Pantry`. The return arrow `Pantry → Chef` is the response path. Colors group the kitchen side; the footer repeats the legend and the place chips.':
 'Cara membaca: `Customer → Waiter → Chef → Pantry`. Panah balik `Pantry → Chef` adalah jalur response. Warna mengelompokkan sisi dapur; footer mengulang legenda dan chip tempat.',
 '### 19.2 Hospital platform': '### 19.2 Platform rumah sakit',
 'A hospital platform: WAF and cloud edge, PHP runtime stacks (LAMP, LEMP, WAMP, WIMP, FAMP, FIMP), patient data, and a SOC fed by Wazuh and ELK. Solid arrows are the request path; the dashed arrow is the response.':
 'Platform rumah sakit: WAF dan edge cloud, runtime stack PHP (LAMP, LEMP, WAMP, WIMP, FAMP, FIMP), data pasien, dan SOC yang diberi makan oleh Wazuh dan ELK. Panah solid adalah jalur request; panah putus-putus adalah response.',
},
'ms': {
 '### 18.8 Logo library — security tools': '### 18.8 Pustaka logo — alat keselamatan',
 'All 575 logos from `iMoon07/logo-svg` are available to every node (`"logo": "security:nmap"`). This section groups the security catalogue by hacking phase: recon, exploitation, post-exploitation, and forensics. Every node is a tool; the logo is the catalogue entry.':
 'Semua 575 logo daripada `iMoon07/logo-svg` tersedia untuk setiap nod (`"logo": "security:nmap"`). Bahagian ini mengelompokkan katalog keselamatan mengikut fasa penggodaman: recon, eksploitasi, pasca-eksploitasi, dan forensik. Setiap nod ialah alat; logo ialah entri katalog.',
 '#### Recon & enumeration': '#### Recon & enumerasi',
 'How to read: this is a gallery, not a flow. Each column is a recon phase. Top to bottom, the tools move from network discovery to DNS/OSINT to web enumeration. Every node is a tool; the logo is from the local security catalogue.':
 'Cara membaca: ini galeri, bukan aliran. Setiap lajur ialah fasa recon. Dari atas ke bawah, alat bergerak dari penemuan rangkaian ke DNS/OSINT kemudian penghitungan web. Setiap nod ialah alat; logo datang dari katalog keselamatan setempat.',
 '#### Exploitation': '#### Eksploitasi',
 'How to read: this is a gallery, not a flow. Each column is an exploitation phase. Frameworks launch, web tools attack web targets, scanners find issues, and payloads deliver. The groups label the phase; the footer repeats the security context.':
 'Cara membaca: ini galeri, bukan aliran. Setiap lajur ialah fasa eksploitasi. Rangka kerja dilancarkan, alat web menyerang sasaran web, pengimbas mencari isu, dan muatan dihantar. Kumpulan menandakan fasa; footer mengulang konteks keselamatan.',
 '#### Post-exploitation': '#### Pasca-eksploitasi',
 'How to read: this is a gallery, not a flow. Each column is a post-exploitation phase. Credentials first, then lateral movement, password attacks, and wireless/MITM. Follow the group labels to keep the phases straight.':
 'Cara membaca: ini galeri, bukan aliran. Setiap lajur ialah fasa pasca-eksploitasi. Kelayakan dahulu, kemudian pergerakan lateral, serangan kata laluan, dan wayarles/MITM. Ikut label kumpulan supaya fasa kekal jelas.',
 '#### Forensics & reverse engineering': '#### Forensik & kejuruteraan songsang',
 'How to read: this is a gallery, not a flow. Each column is an analysis phase. Disk artifacts, file carving, reverse engineering, and malware triage. Use the group labels to see which phase a tool belongs to.':
 'Cara membaca: ini galeri, bukan aliran. Setiap lajur ialah fasa analisis. Artifak cakera, file carving, kejuruteraan songsang, dan triase perisian hasad. Gunakan label kumpulan untuk melihat fasa sesuatu alat.',
 '#### Network & wireless': '#### Rangkaian & wayarles',
 'How to read: this is a gallery, not a flow. Each column is a network phase. Capture and MITM first, then TLS, tunnels/anonymity, and wireless. The group labels keep the phases straight.':
 'Cara membaca: ini galeri, bukan aliran. Setiap lajur ialah fasa rangkaian. Tangkap dan MITM dahulu, kemudian TLS, terowong/anonimiti, dan wayarles. Label kumpulan mengekalkan fasa yang jelas.',
 '## 19 — Topology Visual Lab': '## 19 — Makmal Visual Topologi',
 '`topology` is the static renderer for article diagrams. It has no toolbar, panel, or zoom: the diagram follows the article column width and stacks vertically on narrow screens. Node logos can use the local Alur catalogue (575 logos from iMoon07/logo-svg), for example `"icon": "security:nmap"`.':
 '`topology` ialah pemaparan statik untuk rajah artikel. Tiada toolbar, panel, atau zum: rajah mengikut lebar lajur artikel dan bertindan secara menegak pada skrin sempit. Logo nod boleh menggunakan katalog Alur setempat (575 logo daripada iMoon07/logo-svg), contohnya `"icon": "security:nmap"`.',
 '### 19.1 Restaurant as a server request': '### 19.1 Restoran sebagai permintaan pelayan',
 'Read left → right. Solid arrows are the order/request path; the dashed arrow is the return/response. The footer repeats the direction legend and the place chips, so the picture is not just a picture.':
 'Baca dari kiri → kanan. Anak panah pejal ialah laluan pesanan/permintaan; anak panah putus-putus ialah laluan pulangan/sambutan. Footer mengulang legenda arah dan cip tempat, jadi gambar itu bukan sekadar gambar.',
 'How to read: `Customer → Waiter → Chef → Pantry`. The return arrow `Pantry → Chef` is the response path. Colors group the kitchen side; the footer repeats the legend and the place chips.':
 'Cara membaca: `Customer → Waiter → Chef → Pantry`. Anak panah pulangan `Pantry → Chef` ialah laluan sambutan. Warna mengumpulkan bahagian dapur; footer mengulang legenda dan cip tempat.',
 '### 19.2 Hospital platform': '### 19.2 Platform hospital',
 'A hospital platform: WAF and cloud edge, PHP runtime stacks (LAMP, LEMP, WAMP, WIMP, FAMP, FIMP), patient data, and a SOC fed by Wazuh and ELK. Solid arrows are the request path; the dashed arrow is the response.':
 'Platform hospital: WAF dan edge awan, timbunan runtime PHP (LAMP, LEMP, WAMP, WIMP, FAMP, FIMP), data pesakit, dan SOC yang disuap oleh Wazuh dan ELK. Anak panah pejal ialah laluan permintaan; anak panah putus-putus ialah sambutan.',
},
'tl': {
 '### 18.8 Logo library — security tools': '### 18.8 Logo library — mga tool sa seguridad',
 'All 575 logos from `iMoon07/logo-svg` are available to every node (`"logo": "security:nmap"`). This section groups the security catalogue by hacking phase: recon, exploitation, post-exploitation, and forensics. Every node is a tool; the logo is the catalogue entry.':
 'Lahat ng 575 logo mula sa `iMoon07/logo-svg` ay available sa bawat node (`"logo": "security:nmap"`). Ang seksyong ito ay nagpo-grupo ng security catalogue ayon sa hacking phase: recon, exploitation, post-exploitation, at forensics. Bawat node ay isang tool; ang logo ay ang catalogue entry.',
 'How to read: this is a gallery, not a flow. Each column is a recon phase. Top to bottom, the tools move from network discovery to DNS/OSINT to web enumeration. Every node is a tool; the logo is from the local security catalogue.':
 'Paano basahin: ito ay gallery, hindi flow. Bawat column ay isang recon phase. Mula sa itaas pababa, ang mga tool ay gumagalaw mula network discovery papuntang DNS/OSINT hanggang web enumeration. Bawat node ay isang tool; ang logo ay mula sa lokal na security catalogue.',
 'How to read: this is a gallery, not a flow. Each column is an exploitation phase. Frameworks launch, web tools attack web targets, scanners find issues, and payloads deliver. The groups label the phase; the footer repeats the security context.':
 'Paano basahin: ito ay gallery, hindi flow. Bawat column ay isang exploitation phase. Naglulunsad ang frameworks, inaatake ng web tools ang web targets, nahahanap ng scanners ang issues, at naghahatid ang payloads. Ang groups ay naglalabel ng phase; inuulit ng footer ang security context.',
 'How to read: this is a gallery, not a flow. Each column is a post-exploitation phase. Credentials first, then lateral movement, password attacks, and wireless/MITM. Follow the group labels to keep the phases straight.':
 'Paano basahin: ito ay gallery, hindi flow. Bawat column ay isang post-exploitation phase. Credentials muna, tapos lateral movement, password attacks, at wireless/MITM. Sundan ang group labels para manatiling malinaw ang phases.',
 'How to read: this is a gallery, not a flow. Each column is an analysis phase. Disk artifacts, file carving, reverse engineering, and malware triage. Use the group labels to see which phase a tool belongs to.':
 'Paano basahin: ito ay gallery, hindi flow. Bawat column ay isang analysis phase. Disk artifacts, file carving, reverse engineering, at malware triage. Gamitin ang group labels para makita kung saang phase nabibilang ang isang tool.',
 'How to read: this is a gallery, not a flow. Each column is a network phase. Capture and MITM first, then TLS, tunnels/anonymity, and wireless. The group labels keep the phases straight.':
 'Paano basahin: ito ay gallery, hindi flow. Bawat column ay isang network phase. Capture at MITM muna, tapos TLS, tunnels/anonymity, at wireless. Pinapanatiling malinaw ng group labels ang phases.',
 '## 19 — Topology Visual Lab': '## 19 — Topology Visual Lab',
 '`topology` is the static renderer for article diagrams. It has no toolbar, panel, or zoom: the diagram follows the article column width and stacks vertically on narrow screens. Node logos can use the local Alur catalogue (575 logos from iMoon07/logo-svg), for example `"icon": "security:nmap"`.':
 'Ang `topology` ay ang static renderer para sa mga diagram ng artikulo. Wala itong toolbar, panel, o zoom: sumusunod ang diagram sa lapad ng article column at nag-iistack nang patayo sa makitid na screen. Ang node logos ay maaaring gumamit ng lokal na Alur catalogue (575 logos mula sa iMoon07/logo-svg), halimbawa `"icon": "security:nmap"`.',
 '### 19.1 Restaurant as a server request': '### 19.1 Restaurant as a server request',
 'Read left → right. Solid arrows are the order/request path; the dashed arrow is the return/response. The footer repeats the direction legend and the place chips, so the picture is not just a picture.':
 'Basahin mula kaliwa → kanan. Ang solid arrows ay ang order/request path; ang dashed arrow ay ang return/response. Inuulit ng footer ang direction legend at ang place chips, kaya hindi lang larawan ang larawan.',
 'How to read: `Customer → Waiter → Chef → Pantry`. The return arrow `Pantry → Chef` is the response path. Colors group the kitchen side; the footer repeats the legend and the place chips.':
 'Paano basahin: `Customer → Waiter → Chef → Pantry`. Ang return arrow `Pantry → Chef` ay ang response path. Pinip pangkat ng colors ang kitchen side; inuulit ng footer ang legend at place chips.',
 '### 19.2 Hospital platform': '### 19.2 Hospital platform',
 'A hospital platform: WAF and cloud edge, PHP runtime stacks (LAMP, LEMP, WAMP, WIMP, FAMP, FIMP), patient data, and a SOC fed by Wazuh and ELK. Solid arrows are the request path; the dashed arrow is the response.':
 'Isang hospital platform: WAF at cloud edge, PHP runtime stacks (LAMP, LEMP, WAMP, WIMP, FAMP, FIMP), patient data, at isang SOC na pinapakain ng Wazuh at ELK. Ang solid arrows ay ang request path; ang dashed arrow ay ang response.',
},
}

for lang, repl in T.items():
    block = base
    for old, new in repl.items():
        if old not in block:
            print('MISSING', lang, old[:80])
        block = block.replace(old, new)
    path = f'template-for-you-{lang}.md'
    text = Path(path).read_text()
    a = text.index('### 18.8')
    b = text.index('## Conclusion')
    out = text[:a] + block + '\n\n' + text[b:]
    Path(path).write_text(out)
    print(lang, 'written', len(out), 'delta', len(out)-len(text))
