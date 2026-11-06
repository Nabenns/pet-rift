# 01 — PRD

Produk: **Pet Rift** (nama kerja). Platform: Roblox. Genre: RNG pet collector. Tim: 1 orang. Target rilis v1: 10 hari kerja.

Rujukan: keputusan yang mengikat di `00-DECISIONS.md`, angka peluang di `design/economy.json`, cara membangun di `02-TRD.md`.

## 1. Masalah

Pemain Roblox yang suka koleksi tidak punya alasan untuk kembali tiap hari kalau tidak ada yang dikejar. Game koleksi yang ada menuntut waktu belajar (pertarungan, crafting, ekonomi), dan sebagian besar menagih uang di depan sebelum pemain tahu dia suka.

RNG menyerang dua hal itu sekaligus: **tidak ada yang perlu dipelajari** (satu tombol) dan **hasil pertama datang dalam 3 detik**. Yang membuatnya bertahan bukan mekaniknya, tapi dua hal yang murah bagi pembuat: rasa penasaran ("satu roll lagi") dan koleksi yang kelihatan (42 slot, sebagian masih siluet).

Diferensiasi Pet Rift terhadap RNG Roblox lain: **pet-nya punya badan dan ikut jalan di samping pemain**. Hasil roll tidak berhenti jadi kartu di menu, tapi jadi wujud yang bisa dipamerkan ke pemain lain di server yang sama. Itu satu-satunya alasan tema pet lebih baik daripada tema kartu atau aura untuk genre ini.

## 2. Pemain

| Segmen | Umur | Yang dicari | Yang harus didapat dalam 60 detik pertama |
|---|---|---|---|
| Kolektor kasual (utama, ~70%) | 9-14 | Kejutan dan koleksi | Roll pertama, pet pertama, slot index berikutnya yang masih kosong |
| Pemburu tier (~20%) | 12-17 | Chase, papan skor, gengsi | Angka odds jelas (1 in 2.000) dan pet pemain lain yang lebih bagus |
| Pembelanja (~10%) | 13-18 | mempercepat, bukan membeli hasil | Tombol upgrade dengan harga kelihatan, gamepass yang jelas gunanya |

Asumsi yang harus diuji setelah rilis: apakah segmen 2 benar-benar ada di game satu-tombol, atau mereka semua pindah ke game yang ada pertarungannya.

## 3. Prinsip produk

1. **Satu tombol utama.** Semua layar lain pendukung tombol itu. Kalau sebuah fitur butuh dua navigasi untuk dipakai, fitur itu salah tempat.
2. **Angka odds selalu kelihatan.** Tier, persen, dan sisa pity tampil di layar utama, bukan disembunyikan di menu.
3. **Pet terlihat, bukan cuma tercatat.** Pet yang di-equip jalan di samping pemain dan terlihat pemain lain.
4. **Tidak ada hasil acak yang dijual.** Yang dijual kecepatan, otomatisasi, dan kosmetik (D8).
5. **Kalau ragu, kurangi.** Fitur yang tidak menambah alasan untuk roll berikutnya tidak masuk v1.

## 4. Ruang lingkup

### v1 (dibangun sekarang)

| Fitur | Kriteria penerimaan |
|---|---|
| Roll di Kiln | 1 roll = 1 tap, animasi 2,4 detik, cooldown 3,0 detik, hasil keluar di kartu reveal. Dihitung server |
| 42 hasil roll | 14 pet x 3 varian, semuanya bisa keluar, semuanya punya slot index |
| Index koleksi | Grid 42 slot; yang belum dapat = siluet + warna tier; yang sudah = warna asli. Counter "12/42" di header |
| Equip pet | 1 slot gratis (VIP 3). Pet mengikuti pemain, jarak 4 stud, animasi bob |
| Jual duplikat | "Jual semua duplikat" + jual per item. Shard masuk saldo |
| Upgrade | Luck 10 level (150 -> 10.309 shard, +0,15 luck/level); Roll speed 8 level (100 -> 1.708 shard, -8% cooldown/level) |
| Pity | Counter tampil "2.341 / 8.000". Di 8.000 roll, roll berikutnya dipaksa Divine |
| 4 gamepass | Fast Roll 299 R$, Auto Roll 599 R$, +1 Luck 399 R$, VIP 499 R$ |
| Papan skor | Per server: 10 pemain dengan nilai koleksi tertinggi (bobot tier x varian) |
| Simpan | Profil tahan kill server, tanpa duplikat |
| Tutorial | 3 layar, bisa dilewati, selesai di bawah 20 detik |
| Nama pet | Pemain bisa menamai pet yang di-equip (maks 16 karakter, lewat filter teks Roblox) |

### Nanti (v2, setelah 30 hari data)

Pet power dan zona pertarungan; fusion 3 pet sejenis jadi varian atas; event musiman; trading (hanya setelah audit duplikasi); reward index bertingkat; papan skor global.

### Tidak akan pernah

Menjual jackpot roll berbayar; menjual pet langsung dengan Robux (menghancurkan alasan orang roll); sistem energi yang memaksa menunggu atau bayar; pet yang lebih kuat dari pet lain di v1 (pay-to-win).

## 5. Monetisasi dan urutan alasannya

| Produk | Harga | Jenis | Risiko kebijakan |
|---|---|---|---|
| Fast Roll | 299 R$ | Pass, kecepatan (cooldown / 2) | Nol, tidak mengubah odds |
| Auto Roll | 599 R$ | Pass, otomatisasi | Nol |
| +1 Luck | 399 R$ | Pass, +0,5 luck server-side | Rendah, panel odds wajib hitung ulang live |
| VIP | 499 R$ | Pass, +15% shard, 3 slot equip | Nol |

Urutan peluncuran: Fast Roll -> Auto Roll -> VIP -> +1 Luck. Luck dijual **terakhir** karena itu satu-satunya produk yang mengubah peluang, jadi panel odds dan label `1 in N` harus terbukti benar dulu (gate G1).

Pendapatan v1 datang dari ketidaksabaran dan penampilan. Itu lebih kecil dari menjual roll, dan diterima sadar: menjual roll berpeluang membuka lingkup paid random items, yang artinya cek kebijakan per region dan risiko penurunan produk. v1 tidak masuk ke sana.

## 6. Gate kelulusan (berangka, semua wajib)

Build tidak boleh rilis kalau salah satu gagal. Bukti tiap gate disimpan di `captures/` sebagai file, bukan klaim.

| # | Gate | Ambang | Cara ukur |
|---|---|---|---|
| G1 | Distribusi roll sesuai tabel | 100.000 roll per skenario luck {1,0; 2,0; 3,0}: tiap tier dengan p > 1% dalam +/-5% relatif dari teoretis; Divine dalam 3 sigma (lambda 50 per 100.000, sigma 7,07) | Harness roll di Studio -> CSV -> dihitung di VPS |
| G2 | Roll dihitung server | 1.000 panggilan remote cacat (payload salah, spam 500/menit, klaim hasil) -> 0 perubahan inventori | Uji abuse lokal |
| G3 | Integritas simpan | 200 siklus join/leave + 50 kill server paksa saat menulis -> 0 duplikat, 0 kehilangan | Uji beban lokal |
| G4 | Latensi roll | p95 <= 120 ms, p99 <= 250 ms | MicroProfiler, 3 sesi |
| G5 | Performa klien | 60 fps di kelas iPhone SE 2020; <= 25 ModuleScript; memori <= 250 MB | Stats di device kelas bawah |
| G6 | Mobile | Semua target sentuh >= 44 px; tidak ada hover-only; teks >= 14 px pada skala 1080p | Inspeksi UI + sesi main di HP |
| G7 | Ukuran dan load | Place <= 25 MB; load pertama di 4G <= 12 detik | Asset manager + stopwatch |
| G8 | Pity | Counter 7.999 + 1 roll -> hasil Divine, counter reset 0 | Uji unit di Studio |
| G9 | Nol kehilangan data | Kill server saat roll dan saat sell; rejoin: saldo dan index konsisten | 20 percobaan manual |
| G10 | Kejujuran angka | Jumlah persen di panel odds = 100,0000% +/-0,0001; tiap label `1 in N` cocok dengan bobot sampai 3 angka penting | Bandingkan panel vs `economy.json` |

## 7. Metrik yang dipantau setelah rilis

Bukan gate build, tapi angka yang menentukan v1 dianggap berhasil.

| Metrik | Target | Kalau di bawah target |
|---|---|---|
| Retensi D1 | >= 25% | Loop habis terlalu cepat: tambah reward index, jangan tambah tier |
| Retensi D7 | >= 8% | Chase terlalu jauh: turunkan pity ke 5.000, jangan naikkan odds Divine |
| Roll per sesi | >= 40 | Animasi atau cooldown terlalu panjang |
| Konversi gamepass | >= 2% | Perbaiki harga dan penempatan tombol, bukan menambah paywall |
| Rasio jual/keep | 0,6-0,8 | Kalau > 0,9 pemain menjual semua: nilai shard tier bawah terlalu tinggi |

## 8. Definisi selesai v1

v1 selesai kalau 42 hasil roll bisa keluar dan tercatat, pet yang di-equip terlihat jalan di samping pemain lain, jual dan upgrade mengubah saldo dengan benar, 4 gamepass berfungsi, profil tahan kill server, dan G1-G10 lulus dengan bukti file yang bisa dibuka.

## 9. Risiko produk

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Gaya blocky tidak cukup menarik (skor review sekarang 3-5/10) | Pet tidak layak dijual, tema gagal | 3 style test sebelum F4; kalau gagal, mesh untuk Mythic/Divine saja (`07-ART-PIPELINE.md`) |
| Pemain bosan karena tidak ada gameplay | Retensi D1 < 15% | Index reward + daily rift sebagai tambalan murah di v1.1 |
| Inflasi shard | Upgrade jadi gratis, tidak ada alasan main | Nilai jual dan harga upgrade diikat di `economy.json`; pantau rasio jual/keep |
| Satu orang, 10 hari | Rilis molor | Titik berhenti berguna di F5 (`06-IMPLEMENTATION-PLAN.md`) |
| Nama "Pet Rift" bentrok | Harus ganti judul setelah aset dibuat | Cek pencarian Roblox sebelum F1 selesai |