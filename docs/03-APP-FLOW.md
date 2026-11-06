# 03 — APP FLOW

Semua layar digambar oleh kode (`UI/Factory`), bukan instance manual. Dokumen ini yang jadi spesifikasi tata letak; yang tidak ada di sini tidak dibangun.

## 1. Peta layar

```
        +----------------+        tap PLAY         +----------------------+
        |  LOADING       |----------------------->|  TUTORIAL 1-3        |
        |  (bar + tips)  |                        |  (skip kapan saja)   |
        +----------------+                        +----------+-----------+
                                                              |
                                                              v
   +-----------------------------------------------------------------------+
   |                            HUD (persisten)                            |
   |  shard: 1.240     luck x1,30     pet: Emberfox      [=] menu         |
   |                                                                       |
   |                       +----------------------+                        |
   |                       |      ROLL            |  <- tombol utama        |
   |                       |    (cooldown ring)   |                        |
   |                       +----------------------+                        |
   |                     "Berikutnya dijamin Divine in 5.659"              |
   +-----------------------------------------------------------------------+
              |                  |                    |
          tap ROLL          tap INDEX           tap [=]
              v                  v                    v
   +------------------+  +------------------+  +--------------------------+
   |  REVEAL (2,4 s)  |  |  INDEX 42 slot   |  |  MENU                    |
   |  -> kartu hasil  |  |  filter tier     |  |  - Upgrade (luck/speed)  |
   |  Aksi:           |  |  tap slot ->     |  |  - Odds panel            |
   |  Equip / Simpan  |  |  detail + jual   |  |  - Shop (4 gamepass)     |
   |  / Jual          |  |                  |  |  - Papan skor            |
   +------------------+  +------------------+  |  - Pet saya (equip 1/3)  |
                                              |  - Pengaturan (musik, fx)|
                                              +--------------------------+
```

Empat layar, tidak lebih. Shop, odds, dan leaderboard adalah panel di dalam Menu, bukan layar sendiri, supaya tidak ada dua lapis navigasi dari tombol roll.

## 2. Alur roll (state machine)

```
IDLE ----tap----> REQUEST ----result----> REVEAL ----selesai----> RESULT
 ^                   |                      |                        |
 |                 timeout 3 s              | tap skip               |
 |                   v                      v                        |
 +--------------- ERROR (toast) <-----------+                  aksi pemain
                                                                     |
                          COOLDOWN (3,0 s, ring mengisi) <-----------+
                                     |
                                     +--> IDLE
```

Detail tiap state:

| State | Durasi | Yang terjadi | Kalau gagal |
|---|---|---|---|
| IDLE | - | Tombol penuh, ring kosong. Tap = kirim `RequestRoll` | - |
| REQUEST | maks 3 s | Tombol jadi spinner, tidak bisa di-tap ulang. **Tidak ada** animasi hasil sebelum server menjawab | Timeout -> toast "koneksi lambat", kembali IDLE tanpa memotong cooldown |
| REVEAL | 2,4 s (1,2 s kalau Fast Roll) | Kartu berputar, glow warna tier naik. Tier Mythic/Divine dapat sinar tambahan + suara berbeda | - |
| RESULT | sampai pemain bertindak | Kartu hasil + 3 tombol (Equip / Simpan / Jual). Kalau duplikat, tombol Jual jadi default | - |
| COOLDOWN | sisa dari 3,0 s | Ring mengisi. Tap diabaikan (bukan antre) | - |

Aturan yang mengikat:

- Animasi tidak boleh mulai sebelum hasil dari server ada. Kalau animasi jalan duluan, pemain bisa tahu hasil dari timing, dan itu membuka tebakan.
- Skip reveal diizinkan setelah 0,6 detik. Skip tidak mengubah odds, hanya mempercepat tampilan.
- Selama REVEAL, tombol roll nonaktif. Ini yang mencegah double-roll dari spam tap.
- Auto Roll (gamepass) mengulang siklus IDLE -> COOLDOWN otomatis, dan berhenti kalau: inventori penuh, pemain menekan Stop, atau 3 error berturut.

## 3. Spesifikasi layar

### 3.1 HUD

| Elemen | Posisi | Ukuran (px @1080p) | Isi |
|---|---|---|---|
| Shard counter | kiri atas, 24 px dari tepi | 220x56 | ikon + angka, animasi count-up 0,3 s saat berubah |
| Luck badge | kiri atas, di bawah shard | 180x40 | `luck x1,30`, ungu kalau > 1,0 |
| Equipped pet chip | kanan atas | 260x56 | potret kecil + nama pet + tier warna |
| Menu button | kanan atas pojok | 56x56 | ikon `=`, target sentuh 56 |
| Roll button | bawah tengah | 200x200 | lingkaran, teks `ROLL`, ring cooldown |
| Pity line | 12 px di atas roll button | lebar 320 | `Divine dijamin dalam 5.659 roll` |
| Toasts | bawah, 96 px dari dasar | maks 360x64 | antre maks 2, umur 2,5 s |

### 3.2 Reveal / Result card

| Elemen | Detail |
|---|---|
| Kartu | 340x460, sudut 16 px, border 3 px warna tier, latar `#160F2B` |
| Isi kartu | nama pet (28 px bold), tier chip, varian chip, label odds (`1 in 2.000`), wujud pet (render di viewport 3D kecil, bukan gambar) |
| Warna tier | Common `#8FA0B8`, Uncommon `#5FD08A`, Rare `#4FA8FF`, Epic `#B36BFF`, Legendary `#FFC24A`, Mythic `#FF6B4A`, Divine `#7CF6FF` |
| Efek | Epic: border pulse 1,2 s. Legendary: + 8 partikel. Mythic: + layar sedikit gelap di tepi. Divine: + flash putih 120 ms, sinar berputar |
| Tombol | `Equip` (primary), `Simpan` (secondary), `Jual +30 shard` (ghost). Ketiganya >= 44 px tinggi |

Kalau hasilnya duplikat: judul kartu jadi `Duplikat`, tombol `Jual` jadi primary dan menyebut jumlah shard, `Equip` tetap ada tapi secondary.

### 3.3 Index (42 slot)

- Grid 6 kolom x 7 baris, gap 12 px, sel 88x104. Di layar < 700 px lebar: 4 kolom, sel 76x92.
- Slot dimiliki: wujud pet berwarna, label nama, badge varian kalau Golden/Dark.
- Slot belum dimiliki: siluet hitam 15% opacity + border warna tier + label `???`.
- Header: `Index 12/42` + progress bar tipis.
- Filter: chip `Semua / Dimiliki / Belum` (3 chip, bukan dropdown).
- Tap slot -> panel detail 0,2 s slide-up: wujud lebih besar, tier, odds, jumlah duplikat, tombol Equip/Jual.
- Urutan slot **tetap** (tier dari bawah ke atas, lalu urutan pet di `economy.json`). Tidak pernah diurutkan ulang berdasarkan kepemilikan; pemain harus ingat posisi.

### 3.4 Menu

Lima baris, tinggi 72 px, ikon + label + chevron:

| Baris | Isi |
|---|---|
| Upgrade | 2 track: Luck (10 level), Roll Speed (8 level). Tiap baris: level sekarang, efek, harga, tombol. Tombol nonaktif kalau shard kurang, dengan selisih ditampilkan |
| Odds | tabel 7 tier, persen, `1 in N`, dan delta terhadap luck sekarang (`+0,0984%`) |
| Shop | 4 kartu gamepass: nama, harga R$, efek 1 baris, badge `Dimiliki` kalau sudah |
| Papan skor | top 10 server: nama, nilai koleksi, pet ikonik. Baris pemain sendiri selalu terlihat (di-highlight, sticky di bawah kalau di luar 10) |
| Pet saya | daftar pet + slot equip (1 gratis, 3 dengan VIP). Slot terkunci menampilkan harga VIP |

Pengaturan kecil di pojok bawah menu: toggle musik, toggle efek, tombol `Reset data` (2 konfirmasi, hanya untuk pemain yang minta sendiri lewat tombol, tidak pernah otomatis).

### 3.5 Loading & error

| Kondisi | Tampilan |
|---|---|
| Loading profil | bar tidak tentu + tips bergilir tiap 3 s (`Emberfox 1 in 2.222`) |
| Gagal load | layar penuh, teks besar `Data kamu gagal dimuat`, tombol `Coba lagi`, **tanpa** tombol roll. Tidak ada fallback ke profil baru |
| Koneksi putus saat roll | toast, kembali IDLE, cooldown tidak dipotong |
| Rate limited | toast `Terlalu cepat, tunggu sebentar`, tombol pulih sendiri |
| Inventori penuh (500) | toast `Inventori penuh, jual duplikat dulu`, tombol jual semua muncul di toast |

## 4. Tutorial

3 layar, total < 20 detik, bisa dilewati dengan tombol `Lewati` yang selalu terlihat di kanan atas.

| Layar | Teks | Aksi pemain |
|---|---|---|
| 1 | `Tap ROLL. Dapetin pet. Koleksi 42 wujud.` | tap roll pertama (dipaksa, hasilnya Common acak) |
| 2 | `Semua pet ikut jalan sama kamu.` | tap `Equip`, pet muncul di samping karakter |
| 3 | `Yang langka 1 in 2.000. Ada jaminan Divine tiap 8.000 roll.` | tap `Oke`, tutorial selesai, HUD normal |

Tutorial tidak memberi pet gratis khusus; pet pertama dari roll tutorial adalah roll normal dengan seed yang sudah ada. Itu menjaga integritas index (tidak ada slot yang cuma bisa didapat dari tutorial).

## 5. Layout responsif

| Kelas layar | Lebar acuan | Perubahan |
|---|---|---|
| HP portrait | 360-430 x 640-932 | 1 kolom; roll button 160 px; index 4 kolom; pity line 2 baris |
| HP landscape | 640-932 x 360-430 | HUD atas lebih tipis (48 px); roll button 140 px; index 6 kolom |
| Tablet / desktop | >= 1024 | konten maks 1180 px, di tengah; ukuran elemen sama dengan portrait supaya tidak ada dua desain |

Semua ukuran memakai skala dari `UIScale` yang dihitung sekali dari `AbsoluteSize` viewport, bukan angka tetap per device. Tidak ada `Offset` untuk posisi utama; posisi pakai `AnchorPoint` + `Scale`.

## 6. Yang dilarang di UI

- Tombol dengan teks `Beli` tanpa harga terlihat (kebijakan Roblox + kepercayaan).
- Modal lebih dari satu lapis.
- Countdown palsu, notifikasi merah dot yang tidak mengarah ke apa pun, atau angka "pemain online" palsu.
- Animasi lebih dari 0,4 s untuk transisi layar selain reveal.
- Efek suara otomatis tanpa toggle.
- Hover-only interaction (tidak ada di mobile).

## 7. Bukti per layar

Tiap layar di dokumen ini butuh capture di `captures/` sebelum F7 dianggap selesai:

`HUD.png`, `reveal-common.png`, `reveal-legendary.png`, `reveal-divine.png`, `index-partial.png`, `index-full.png`, `menu-upgrade.png`, `menu-odds.png`, `menu-shop.png`, `menu-leaderboard.png`, `tutorial-1.png`, `tutorial-2.png`, `error-load.png`, `mobile-portrait.png`.

Nama file dipakai apa adanya supaya gate G7 di `01-PRD.md` bisa dicek dengan `ls captures/`.