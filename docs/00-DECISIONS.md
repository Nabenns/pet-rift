# 00 — Keputusan

Dokumen ini mencatat apa yang sudah **dikunci** dan kenapa, plus apa yang masih **terbuka** beserta default yang akan dipakai kalau tidak ada yang membantah sampai fase yang disebutkan.

Aturan: keputusan yang dikunci hanya berubah lewat commit yang menyebut alasannya. "Kayaknya lebih bagus X" tanpa angka bukan alasan.

## Dikunci

### D1 — Genre RNG pet collector

Satu mekanik inti: tekan tombol, tunggu animasi, dapat satu pet dari tabel peluang. Tidak ada pertarungan, tidak ada misi, tidak ada ekonomi pemain di v1.

Alasan: RNG adalah bentuk loop termurah yang bisa dibuat satu orang — semua nilainya ada di **tabel peluang + kejutan + koleksi**, bukan di konten level. Biaya tambah konten = tambah satu baris di tabel, bukan bikin level baru.

Yang secara sadar dikorbankan: pemain yang datang untuk gameplay akan bosan dalam 20 menit. Kita menerima itu, karena target kita pemain yang datang untuk koleksi dan kejutan.

### D2 — Tema pet, gaya blocky dari primitif

Pet punya badan: ikut jalan di samping pemain, bisa dilihat pemain lain, bisa dikasih nama. Ini yang bikin hasil roll terasa milik pemain, bukan sekadar kartu.

Bentuk dibuat dari `Part` primitif, bukan mesh, dengan tiga alasan berangka:

1. 14 pet x 3 varian = **42 hasil roll** dari **14 model**. Varian cuma ganti warna + material, jadi tidak ada model baru.
2. Waktu bikin satu pet blocky: **45-90 menit** (terbukti: Emberfox, 44 part, 5 iterasi dalam satu malam). Satu pet mesh custom: 4-8 jam kalau bisa modeling, atau biaya artis.
3. Bentuk primitif tetap kebaca di layar HP 5 inci karena siluetnya besar dan tebal, bukan detail kecil.

Catatan jujur: hasil review Emberfox sekarang **3-5 dari 10** untuk standar pet RNG berbayar. Gaya ini belum terbukti cukup. Gerbang keputusannya ada di `07-ART-PIPELINE.md` (3 style test sebelum F4). Kalau gagal, kita pindah ke mesh untuk tier atas saja, bukan bongkar seluruh rencana.

### D3 — Tabel berbobot, jumlah 100, bukan rarest-first

Bobot tier: Common 45, Uncommon 30, Rare 15, Epic 7,5, Legendary 2, Mythic 0,45, Divine 0,05. Total 100.

Alasan: pada tabel rarest-first (tiap tier = 1/N dari tier di atasnya), luck multiplier merusak tabel. Simulasi yang sudah dijalankan: dengan urutan 2/8/45/300/2000/15000 dan luck 2x, tier Uncommon jadi **pasti kena** dan Divine jatuh dari 0,0028% ke 0,0000%. Tabel berbobot + renormalisasi tidak punya masalah itu karena setelah bobot dikali luck, semua bobot dibagi ulang ke total 100.

### D4 — Luck hanya menyentuh tier chase

Luck mengalikan bobot **Legendary, Mythic, Divine** saja, lalu seluruh tabel direnormalisasi. Efeknya: peluang tier bawah ikut turun sedikit, dan itu memang yang diinginkan — luck membeli kesempatan kejar tier atas, bukan membuang hasil jelek.

`luck.stack_max = 3.0`. Tidak ada cara resmi melewati 3,0.

### D5 — Pity di 8.000 roll

Counter `rolls_since_divine` per pemain, reset saat dapat Divine. Kalau mencapai 8.000, roll berikutnya dipaksa Divine.

Angka 8.000 dipilih karena: peluang Divine 0,05% → peluang **tidak** dapat Divine dalam 8.000 roll adalah `(1-0,0005)^8000 ≈ 1,83%`. Artinya pity ini hanya menyentuh 1-2 dari 100 pemain paling apes, jadi tidak merusak scarcity, tapi berhasil menghapus skenario "main 6 jam, tidak dapat apa-apa, uninstall".

### D6 — Roll dihitung di server

Klien hanya mengirim niat (`RequestRoll`) dan memutar animasi. Angka keluar dari `Random.new()` di server, inventori ditulis di server. Klien tidak pernah menerima tabel bobot mentah dan tidak pernah mengirim hasil.

Alasan: satu klien yang bisa mengirim "aku dapat Divine" merusak seluruh ekonomi game. Semua game RNG yang di-exploit punya bug yang sama.

### D7 — Varian sebagai pengali konten

Tiap pet punya 3 varian: Normal (85%), Golden (12%), Dark (3%). Varian dipilih roll kedua yang independen dari tier.

Nilai jual: Normal x1,00, Golden x1,25, Dark x1,60.

Alasan: satu baris kode varian menghasilkan 3x konten yang bisa dikejar, tanpa satu part baru. Golden dan Dark juga jadi alasan alami untuk memperkenalkan material baru di masa depan (Neon, ForceField) tanpa mengubah geometri.

### D8 — Jangan jual hasil acak dengan uang

Yang dijual v1: kecepatan (Fast Roll 299 R$), otomatisasi (Auto Roll 599 R$), luck server-side (+1 Luck 399 R$), dan VIP 499 R$ (+15% shard, 3 slot equip). Roll tambahan **tidak** dijual.

Alasan: menjual roll berpeluang = menjual judi ke anak di platform yang punya kebijakan khusus soal itu. Roblox punya `PolicyService:GetPolicyInfoForPlayerAsync` yang mengembalikan `ArePaidRandomItemsRestricted`; begitu kita mulai menjual roll atau pet box, kita masuk wilayah itu dan harus fail-closed per region. v1 tidak masuk wilayah itu sama sekali, jadi lebih aman dan lebih cepat rilis.

Kalau nanti kita jual, gerbangnya jelas: persentase tampil sebelum beli, tombol Details, odds live, cek kebijakan di server, tolak transaksi kalau `ArePaidRandomItemsRestricted = true`.

### D9 — Simpan pakai ProfileStore, bukan DataStore mentah

Profil pemain disimpan lewat ProfileStore (MadStudioRoblox, session locking), vendored sebagai satu ModuleScript di `src/packages/`.

Alasan: DataStore punya `GetAsync`/`SetAsync` tanpa penguncian sesi. Dua server yang menyimpan profil pemain yang sama pada saat yang sama = item duplikat atau item hilang. Menulis session lock sendiri untuk menghindari satu library adalah cara memperbaiki bug yang sudah diperbaiki orang lain. Ini satu-satunya pengecualian dari aturan "tanpa dependensi pihak ketiga".

### D10 — Sumber kebenaran adalah repo, bukan Studio

Pet disimpan sebagai kode Luau yang membangun model (`src/pets/*.luau`). Instance di place Roblox bukan sumber kebenaran.

Alasan: sudah kejadian di sesi pertama — place ter-reload, id Studio berubah dari `dc1fcacd…` ke `c9d4d5b1…`, dan semua instance yang cuma ada di Edit datamodel hilang. Rebuild dari repo = satu panggilan fungsi.

### D11 — Mobile-first

Semua target sentuh minimal 44 px, tidak ada fitur yang butuh hover, tidak ada teks di bawah 14 px pada skala UI 1080p, satu tangan bisa main.

Alasan: mayoritas pemain Roblox main di HP. Game RNG yang tombolnya kecil akan mati di hari pertama.

### D12 — Dua jalur aset: mesh untuk rilis, primitif sebagai fallback wajib

Bentuk pet boleh datang dari mesh hasil AI (Astra) yang dirapikan di Blender, tapi **jalur primitif tetap dibangun** dan tetap jadi default kalau aset belum ada.

Mekanismenya satu tabel: `design/pet-assets.json` -> `src/shared/PetAssets.luau`. Loader bertanya "pet ini punya mesh berstatus `done`?". Kalau ya, bangun `MeshPart`; kalau tidak, `Pets/Builder.build()`. Kode tidak pernah bercabang di tempat lain.

Alasan:

1. D2 benar soal biaya, tapi salah soal mutu: review Emberfox primitif 3-5/10, dan 3-5/10 tidak cukup untuk game yang menjual koleksi. Kalau ada orang yang bisa menghasilkan mesh, memaksakan primitif hanya mempertahankan kelemahan.
2. Dua jalur menghilangkan blocking. 3D bisa telat tanpa menahan rilis, dan kode tidak perlu menunggu aset untuk diuji.
3. Varian tetap murah: 14 mesh x 3 colormap = 42 tampilan. Yang berubah dari D2 hanya "ganti material" jadi "ganti colormap", bukan jumlah pekerjaan varian.

Konsekuensi yang diterima:

- Aset di-upload dari akun pemilik place, bukan akun pembuat. Teman menyerahkan file, owner yang import.
- Tekstur tidak boleh punya lighting bake, kalau tidak varian Golden/Dark mustahil tanpa generate ulang.
- Anggaran tri jadi angka baru yang harus dijaga: <= 5.000 per pet (batas engine ±20.000).
- Kalau mesin 3D berhenti di tengah jalan, game tetap rilis dengan campuran gaya. Itu diterima, bukan disembunyikan.

Kontrak teknis lengkap ada di `09-3D-CONTRACT.md`, pembagian tugas di `08-TASK-SPLIT.md`.

## Terbuka (default kalau tidak dibantah)

| # | Pertanyaan | Default yang akan dipakai | Diputuskan sebelum |
|---|---|---|---|
| O1 | Gaya final: blocky dipertahankan atau pindah mesh untuk tier atas? | Diukur di gate, bukan dirasa: mesh kalau G3D-3 lulus (14 mesh di H+8), hybrid kalau cuma 8, primitif kalau kurang dari 8 | H+6 |
| O2 | Nama game "Pet Rift" dipakai? | Ya, sementara. Ganti nama = ganti judul + ikon, bukan arsitektur | F1 |
| O3 | Harga gamepass disesuaikan pasar Indonesia? | Ya, angka di PRD adalah batas atas; boleh turun, tidak boleh naik | F6 |
| O4 | Ada trading antar pemain? | Tidak di v1, tidak di v2. Kalau nanti, butuh audit duplikasi penuh dulu | setelah v1 rilis |
| O5 | Pet punya stat/power? | Tidak. Itu pintu masuk ke genre Pet Simulator yang butuh ekonomi + zona + musuh | setelah v1 rilis |
| O6 | Event musiman pertama | Tidak ada di rilis. Tambah setelah 30 hari data retensi | setelah v1 rilis |

## Yang sengaja tidak dibangun di v1

| Tidak dibangun | Alasan |
|---|---|
| Pertarungan pet | Butuh musuh, stat, balancing, dan UI baru. Bukan satu orang dua minggu |
| Trading | Risiko duplikasi item paling tinggi di genre ini. Butuh audit dan rate limit sendiri |
| Fusion / crafting | Menambah tabel kedua yang harus dijaga konsisten dengan tabel roll |
| Zona kedua | Satu zona + satu tombol sudah cukup untuk mengukur apakah loop-nya seru |
| Leaderboard global lintas server | Butuh OrderedDataStore + pemeliharaan; v1 cukup papan per server |
| Sistem level pemain | Menambah sumber angka yang harus di-balance tanpa menambah keseruan |
| Pet AI mengikuti pemain dengan pathfinding | Cukup trailing offset; pathfinding mahal dan tidak terlihat bedanya di layar HP |
