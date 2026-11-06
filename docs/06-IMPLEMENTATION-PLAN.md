# 06 — IMPLEMENTATION PLAN

Urutan kerja 10 hari untuk satu orang. Prinsip: **tiap fase berakhir dengan sesuatu yang bisa dilihat atau diukur**, bukan dengan "modul selesai ditulis". Kalau satu fase melewati anggarannya 50%, lanjut ke fase berikutnya dan catat utangnya — jangan mengejar fase yang tertinggal.

Fase yang ditandai **STOP POINT** adalah titik di mana proyek masih punya nilai kalau dihentikan: ada build yang bisa dimainkan.

## F0 — Fondasi repo (0,5 hari)

| Deliverable | Bukti |
|---|---|
| `tools/gen_economy.py` (baca `economy.json` -> `src/shared/Economy.luau`) | file hasil generate ada di repo, header "JANGAN EDIT" |
| `tools/sim_rolls.py` (100.000 roll x 3 luck -> CSV) | `captures/G1-sim.csv` |
| `src/Shared/Economy.luau` ter-generate | angka sama dengan tabel di `02-TRD.md` |
| ProfilStore vendored + SHA di header | `grep 45c9847 src/packages/ProfileStore.luau` |
| `Tests/Spec.luau` kerangka + 1 assert lulus | output `{passed=1,failed=0}` di Studio |

Commit: `feat(tools): generate economy module from single source`, `feat(tools): roll simulation for odds verification`.

Gate: **G1 lulus lebih dulu**, sebelum satu baris UI ditulis. Kalau tabel bobot salah, semua yang dibangun di atasnya salah.

## F1 — Roll di server (1 hari)

| Deliverable | Bukti |
|---|---|
| `RollService` (bobot, luck, pity, seed per pemain) | uji unit: 8 assert lulus |
| `EconomyService.grant` (inventori +1, isNew) | uji: grant 3x Mochi -> count 3, isNew hanya sekali |
| `ProfileService` dengan adapter palsu | uji: load gagal -> roll ditolak |
| Rate limiter token bucket | uji: 46 roll dalam 1 menit -> yang ke-46 ditolak |

Commit: `feat(server): authoritative roll with luck and pity`.

Gate: G2 (payload cacat tidak mengubah inventori) dan G8 (pity).

**STOP POINT 1**: server bisa roll dan mencatat, walau belum ada UI. Ini sudah bisa diuji lewat `execute_luau` tanpa Studio dibuka manual.

## F2 — Builder pet (1,5 hari)

| Deliverable | Bukti |
|---|---|
| `Pets/Specs.luau` 14 spec | satu tabel, tiap pet <= 12 parameter |
| `Pets/Builder.luau` `build(spec, variant) -> Model` | Memanggil builder untuk 14 pet menghasilkan 14 model tanpa error |
| Audit otomatis: raycast dari kamera per part | `captures/pet-audit.txt`: tiap part `visible=true` |
| Part budget | tiap pet <= 50 part; total <= 700 |

Audit raycast adalah bagian wajib, bukan tambahan: vision review pernah bilang kaki hilang padahal ada, dan sebaliknya. Yang dipercaya adalah raycast, yang dipakai untuk menilai estetika adalah capture.

Commit: `feat(pets): data-driven blocky pet builder`, `feat(tools): visibility audit for pet parts`.

**STOP POINT 2**: 14 pet bisa dibangun dari satu fungsi. Kalau gaya visual nanti diputuskan gagal, yang dibuang cuma `Specs.luau`, bukan sistem.

## F3 — Style test (0,5 hari)

3 iterasi gaya untuk satu pet (Emberfox, karena paling menuntut), dinilai dengan 3 kriteria di 3 jarak. Kriteria dan prosedurnya di `07-ART-PIPELINE.md` bagian 4.

| Iterasi | Yang diubah | Lulus kalau |
|---|---|---|
| T1 (sekarang) | baseline: chibi proporsional | skor >= 6/10 di jarak dekat DAN thumbnail |
| T2 | satu bentuk dominan, 2 warna per pet, mata lebih besar | skor >= 6/10 di ketiga jarak |
| T3 | material + pencahayaan (rim light, contact shadow, color grading) | skor >= 7/10 |

Keputusan yang keluar dari sini: **(a)** blocky dipakai untuk semua tier, **(b)** blocky untuk Common-Epic dan mesh untuk Mythic/Divine, atau **(c)** semua pindah ke mesh (artinya F2 dibuang dan jadwal molor 2-3 hari).

Jangan menunda keputusan ini sampai semua 14 pet dibangun. Gaya yang salah x 14 = kerja yang dibuang.

## F4 — UI inti (2 hari)

| Deliverable | Bukti |
|---|---|
| `UI/Factory` (deskripsi tabel -> instance) | satu modul, <= 200 baris, dipakai semua layar |
| HUD + Roll button + cooldown ring | `captures/HUD.png` |
| Reveal 3 fase + kartu hasil | `captures/reveal-common.png`, `reveal-legendary.png`, `reveal-divine.png` |
| Index 42 slot + filter | `captures/index-partial.png`, `index-full.png` |
| State sync server -> klien | setelah rejoin, index dan shard sama |

Commit: `feat(client): ui factory and roll screen`, `feat(client): collection index`.

Gate: G5 (fps + jumlah modul), G6 (target sentuh), G7 di awal (ukuran place masih kecil).

**STOP POINT 3**: loop inti bisa dimainkan. Ini build pertama yang layak dikasih ke orang lain untuk dicoba.

## F5 — Ekonomi dan upgrade (1 hari)

| Deliverable | Bukti |
|---|---|
| Jual satu + jual duplikat | uji: jual semua duplikat menyisakan 1 tiap key |
| Upgrade luck dan speed (10 + 8 level) | uji: harga cocok `economy.json`, level maksimum menolak |
| Shop 4 gamepass + `MonetizationService` | uji: receipt ganda tidak memberi dua kali |
| Papan skor per server | capture 2 pemain, urutan benar |

Commit: `feat(economy): sell, upgrades, and product grants`.

Gate: G3 (integritas simpan) dijalankan di akhir fase ini, karena sekarang ada dua jalur tulis (roll dan jual).

## F6 — Onboarding dan tepi (1 hari)

| Deliverable | Bukti |
|---|---|
| Tutorial 3 layar + skip | `captures/tutorial-1.png`, `tutorial-2.png` |
| Layar gagal muat | `captures/error-load.png` |
| Toast: rate limit, inventori penuh, error koneksi | uji manual 3 skenario |
| Layout HP portrait + landscape | `captures/mobile-portrait.png`, `mobile-landscape.png` |
| Pengaturan (musik, efek) | toggle persist dalam sesi |

Commit: `feat(client): onboarding and edge states`.

## F7 — Pengujian gate (1 hari)

| Gate | Cara | Bukti |
|---|---|---|
| G1 | `tools/sim_rolls.py` + harness roll in-game 100.000 | `captures/G1-sim.csv`, `G1-harness.txt` |
| G2 | klien palsu 1.000 payload cacat | `captures/G2-abuse.txt` |
| G3 | 200 join/leave + 50 kill paksa | `captures/G3-session.txt` |
| G4 | MicroProfiler 3 sesi | `captures/G4-latency.txt` |
| G5 | Stats di device kelas bawah | `captures/G5-perf.txt` |
| G6 | inspeksi UI + sesi HP | `captures/G6-mobile.jpg` |
| G7 | Asset manager + stopwatch | `captures/G7-size.txt` |
| G8 | uji pity 7.999 | `captures/G8-pity.txt` |
| G9 | 20 kill saat roll/jual | `captures/G9-integrity.txt` |
| G10 | bandingkan panel odds vs `economy.json` | `captures/G10-odds.txt` |
| Visual | 14 capture layar | `captures/*.png` di `03-APP-FLOW.md` bagian 7 |

Commit: `test: gate evidence G1-G10`.

## F8 — Rilis (0,5 hari)

| Deliverable | Catatan |
|---|---|
| Nama final dicek di pencarian Roblox | kalau bentrok, ganti sebelum publish, bukan sesudah |
| Deskripsi dan ikon place | ikon = satu pet Divine di panggung gelap, bukan teks |
| Gamepass dibuat di dashboard, ID dimasukkan `Products.luau` | ID tidak boleh placeholder |
| Publish, uji sekali dengan akun lain | beli 1 gamepass termurah, pastikan grant jalan |
| Tag `v1.0.0` di repo | isi place file (.rbxl) di release, bukan di git |

## Anggaran waktu

| Fase | Hari | Kumulatif |
|---|---|---|
| F0 | 0,5 | 0,5 |
| F1 | 1,0 | 1,5 |
| F2 | 1,5 | 3,0 |
| F3 | 0,5 | 3,5 |
| F4 | 2,0 | 5,5 |
| F5 | 1,0 | 6,5 |
| F6 | 1,0 | 7,5 |
| F7 | 1,0 | 8,5 |
| F8 | 0,5 | 9,0 |

Sisa 1 hari dari 10 adalah buffer untuk hal yang selalu terjadi: Studio reload, tunnel mati, satu bug sesi yang butuh setengah hari.

## Yang dikorbankan kalau waktu habis

Urutan yang dibuang dari belakang: (1) papan skor, (2) Auto Roll, (3) nama pet, (4) filter index, (5) tutorial animasi (teks statis masih lolos). Yang **tidak boleh** dibuang: roll server, pity, simpan, panel odds, 42 slot index. Empat hal itu adalah produknya.

## Definisi selesai teknis

Repo dianggap v1 selesai kalau: `git log` menunjukkan satu commit per fase, tiap gate punya file bukti di `captures/`, `grep -c ProcessReceipt src/` = 1, dan tidak ada file `Economy.luau` yang diedit tangan (dicek dari header hasil generate).