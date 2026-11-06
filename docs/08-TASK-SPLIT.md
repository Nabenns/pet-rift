# 08 — PEMBAGIAN TUGAS (2 ORANG)

Satu owner (kode) + satu teman (3D, pakai Astra). Dokumen ini mengikat: siapa boleh menyentuh file apa, apa yang harus diserahkan, dinilai dengan angka apa, dan apa yang terjadi kalau salah satu sisi telat.

## 1. Aturan dasar

1. **Satu file, satu pemilik.** Butuh perubahan di file orang lain? Kirim PR kecil dengan alasan. Jangan edit langsung.
2. **Interface dulu, isi belakangan.** `design/pet-assets.json` sudah ada sebelum mesh pertama. Kode bisa jalan dengan primitif sementara mesh menyusul.
3. **Tidak ada blocking.** Kalau mesh belum ada, loader pakai `Pets/Builder` (primitif). Game harus bisa dimainkan sejak hari pertama.
4. **Batas kerja:** 3D tidak menyentuh `src/**.luau`. Kode tidak menyentuh `assets/`. Angka ekonomi hanya di `design/economy.json`, milik owner.
5. **Semua keputusan visual dinilai di 3 jarak**, bukan di viewport Blender: 8 stud, 30 stud, 88 px.

## 2. Kepemilikan file

| Path | Pemilik | Catatan |
|---|---|---|
| `src/**` | owner | server, client, UI, `Pets/Builder` (primitif), loader |
| `tools/**` | owner | generator, simulator, audit |
| `design/economy.json` | owner | 3D boleh usul lewat issue, tidak edit |
| `design/pet-assets.json` | 3D | isi `mesh`, `colormaps`, `tris`, `status`; owner validasi lewat generator |
| `assets/pets/**` | 3D | `.glb` + colormap `.png` + render bukti |
| `captures/3d/**` | 3D | screenshot 3 jarak per pet |
| `docs/09-3D-CONTRACT.md` | 3D | boleh menambah klarifikasi; mengubah spesifikasi = PR + alasan |
| `docs/00-08` | owner | 3D baca, tidak edit |

Tabrakan yang paling sering terjadi di proyek dua orang: dua-duanya mengedit `economy.json` lalu saling menimpa. Itu sebabnya angka dipisah dari aset.

## 3. Pembagian per hari

H+1 adalah hari pertama kerja bareng, bukan tanggal kalender.

| Hari | Owner (kode) | Teman (3D, Astra) |
|---|---|---|
| H+1 | F0: registry aset + loader + generator jalan; `Pets/Builder` minimal (1 pet primitif) | Baca `07` + `09` + `04`. Setup pipeline Astra -> Blender -> GLB. **Deliverable: Emberfox mesh pertama (proof of pipeline)** |
| H+2 | F1: server roll + ProfileStore + rate limit | Revisi Emberfox (gate G3D-0), mulai Mochi + Pip |
| H+3 | F1 lanjut: inventori, equip, sell, pity | Mochi, Pip, Bonbon, Nori (4 Common = 4 kombinasi ekstrem) |
| H+4 | F2: UI factory (HUD, ROLL, index) | Revisi wave 1; mulai Kobo, Fernpup, Marble |
| H+5 | F3: reveal sequence + follow + bob | Kobo, Fernpup, Marble, Tide (wave 2 selesai) |
| H+6 | F4: index 42 slot + thumbnail + nama pet | **Gate G3D-2**: 8 mesh selesai = jalur aman aktif. Mulai Zephyr, Vesper |
| H+7 | F5: gamepass + PolicyService + shard | Zephyr, Vesper, Aurelia, Volt (wave 3) |
| H+8 | F6: Kiln (mesin roll) integrasi + SFX | Emberfox final, Astraeon. **14 mesh selesai** |
| H+9 | F7: polish, mobile pass, audit performa | 42 colormap (3 varian x 14) + thumbnail 88 px |
| H+10 | F8: rilis privat, soak test 2 jam | Fix temuan audit; dokumentasi aset |

Beban 3D: 14 mesh / 9 hari kerja = **1,5 mesh per hari**. Kalau teman lo sekolah/kuliah, itu realistis hanya kalau tiap mesh 45-70 menit. Kalau ternyata 2 jam per mesh, pakai jalur aman di bagian 7, jangan dipaksa.

## 4. Definisi selesai per pet (angka, bukan opini)

Sebuah mesh dihitung selesai kalau **semua** ini benar:

| # | Syarat | Diperiksa oleh |
|---|---|---|
| 1 | Tri <= 5.000 (batas engine ±20.000; kita sisakan ruang untuk HP) | laporan export + Asset Manager |
| 2 | Satu objek mesh (aksesori ikut di dalam mesh, bukan part terpisah) | owner, `auditBounds` |
| 3 | Tinggi 2,4-3,2 stud; lebar <= 3,0; kedalaman <= 3,6 | `auditBounds` |
| 4 | Titik pivot di tengah telapak kaki, bukan di perut | `auditBounds` (bottom = 0) |
| 5 | Menghadap -Z (depan pet searah LookVector) | cek visual dengan marker |
| 6 | Tekstur dasar 512x512 atau 1024x1024, **tanpa bayangan/AO yang dipanggang** | inspeksi PNG |
| 7 | Palet <= 3 warna + mata, sesuai tabel `07` | bandingkan hex |
| 8 | Lolos 3 jarak: kebaca di 8 stud, 30 stud, dan 88 px | 3 pertanyaan di `07` bagian 4 |
| 9 | 3 colormap: Normal, Golden, Dark (bukan tint runtime) | daftar file |
| 10 | Nama file sesuai kontrak | `ls` |

Poin 6 dan 9 itu yang paling sering dilanggar generator AI: hasilnya cantik tapi warnanya sudah dipanggang di tekstur, jadi varian Golden/Dark tidak bisa dibuat tanpa generate ulang. Solusinya: minta output **flat matte, tanpa lighting bake**, lalu varian dibuat dari colormap.

## 5. Gate 3D

| Gate | Kapan | Lulus kalau | Kalau gagal |
|---|---|---|---|
| G3D-0 | akhir H+2 | 1 mesh Emberfox masuk repo, lolos 10 syarat, dan bisa dibangun dari registry di Studio | ganti alat/pipeline sekarang, bukan di H+8 |
| G3D-1 | H+4 | 4 Common lolos, dan keempatnya **beda siluet** di 88 px | revisi bentuk, bukan warna |
| G3D-2 | H+6 | 8 mesh selesai | jalur aman (bagian 7) |
| G3D-3 | H+8 | 14 mesh, 42 colormap | tier atas tetap primitif |
| G3D-4 | H+10 | audit performa: 3 pet aktif x 5.000 tri = 15.000 tri, tidak ada frame drop di HP | kurangi tri atau LOD |

Gate dinilai owner, tapi buktinya dari teman: 3 screenshot + angka tri + tinggi. Tanpa bukti, gate tidak dihitung lulus.

## 6. Protokol handoff

- Branch: `asset/<petid>` (contoh `asset/mochi`). Satu pet satu branch, satu PR.
- Commit: `asset(mochi): mesh + 3 colormaps` lalu `asset(mochi): thumbnail 88px`.
- Isi PR wajib: angka tri, tinggi/lebar/kedalaman, 3 screenshot (8/30/88), checklist 10 syarat.
- Review maksimal 24 jam. Kalau lewat, anggap lulus sementara dan lanjut; jangan menunggu.
- Merge dilakukan owner setelah generator jalan tanpa error dan `status` di JSON berubah ke `done`.
- Pertanyaan cepat: issue GitHub dengan label `3d`. Jangan lewat chat pribadi, karena keputusan yang hilang di chat akan diulang.

## 7. Kalau 3D telat atau berhenti

Tiga jalur, dipilih di checkpoint, bukan di akhir:

| Jalur | Syarat | Konsekuensi |
|---|---|---|
| A — penuh | 14 mesh di H+8 | 42 hasil, semua tier mesh |
| B — hybrid | 8 mesh di H+6 | Common-Rare mesh, Epic ke atas primitif. Rilis tetap 10 hari, campuran gaya terlihat, diterima |
| C — primitif | < 8 mesh di H+6 | Semua primitif seperti rencana awal `07`; mesh masuk setelah rilis sebagai update |

Jalur C bukan kegagalan: `Pets/Builder` memang dibangun lebih dulu supaya opsi ini selalu hidup. Yang tidak boleh: menunggu mesh sampai H+9 lalu memutuskan.

## 8. Pesan siap kirim ke teman

```text
Halo! Gw lagi bikin game Roblox RNG pet namanya Pet Rift, dan gw butuh lo di bagian 3D.

Repo: https://github.com/Nabenns/pet-rift

Baca 3 file ini dulu, urutannya penting:
1. docs/07-ART-PIPELINE.md  -> roster 14 pet, palet, proporsi, aturan bentuk
2. docs/09-3D-CONTRACT.md   -> spek mesh dari Astra: tri, skala, pivot, varian, cara upload
3. docs/04-DESIGN-BRIEF.md  -> arah visual dan palet UI

Intinya: 14 pet, tiap pet 3 varian (Normal/Golden/Dark) yang dibuat dari colormap,
jadi 42 tampilan dari 14 mesh. Semua gaya harus konsisten: chibi, matte, maksimal
3 warna, kebaca dari jauh.

Tugas pertama (deadline 2 hari): Emberfox. Mesh rubah api, chibi, tinggi 2,7 stud,
<= 5.000 tri, pivot di telapak kaki, menghadap -Z, tekstur flat tanpa bayangan
dipanggang. Simpan sebagai assets/pets/emberfox/model.glb + 3 colormap PNG,
lalu PR ke branch asset/emberfox.

Kalau pipeline Astra lo nggak bisa keluarin GLB bersih, bilang sekarang, jangan
diakalin di akhir. Gw punya jalur primitif sebagai cadangan, jadi nggak akan
nahan rilis.

Yang lo nggak perlu sentuh: kode Luau, ekonomi, UI. Fokus lo cuma bentuk dan warna.
```