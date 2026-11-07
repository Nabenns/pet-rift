# 10 — PROTOKOL UPDATE (3D -> owner)

Tujuan: setiap kali pekerjaan 3D bergerak, owner bisa **melihat** tanpa harus bertanya, dan tidak ada kiriman yang masuk tanpa angka.

Aturannya satu: **selesai satu hal = satu commit + satu PR + satu status di `pet-assets.json`.** Laporan lewat chat tidak dihitung, karena hilang dan tidak bisa diaudit.

## 1. Rutinitas 5 menit setelah selesai satu pet

```bash
# sekali di awal
git clone https://github.com/Nabenns/pet-rift
cd pet-rift
git config user.name "nama-teman"
git config user.email "email-teman"

# setiap kali selesai satu pet
git checkout main && git pull
git checkout -b asset/mochi
mkdir -p assets/pets/mochi
# copy: model.glb colormap-normal.png colormap-gold.png colormap-dark.png
#        render-08.png render-30.png render-88.png meta.json
python3 tools/check_assets.py          # harus 0 error sebelum commit
git add assets/pets/mochi design/pet-assets.json
git commit -m "asset(mochi): mesh + 3 colormaps"
git push -u origin asset/mochi
```

Lalu buka PR dengan judul `asset(mochi): mesh + 3 colormaps` dan isi badan PR:

```text
Closes #<nomor issue Mochi>

- tri: 3120
- tinggi: 2.70 stud (chibi)
- lebar x kedalaman: 2.10 x 2.90 stud
- colormap: normal / gold / dark (512px, tanpa lighting bake)
- 3 jarak: 8 stud ok, 30 stud ok, 88px ok
- catatan: <apa yang belum, kalau ada>
```

Begitu PR dibuka, bot akan otomatis mengomentari PR dengan tabel cek dan **gambar preview 3 jarak**. Itu yang dilihat owner.

## 2. Yang owner lihat (tanpa tanya)

| Tempat | Isi | Kapan berubah |
|---|---|---|
| https://github.com/Nabenns/pet-rift/issues?q=label%3A3d | papan 14 pet, satu issue per pet, tertutup otomatis saat PR di-merge | setiap PR merge |
| Tab Pull requests | preview gambar 3 jarak + tabel cek otomatis | setiap PR dibuka |
| `python3 tools/check_assets.py` | tabel status semua pet di terminal | kapan saja |
| `design/pet-assets.json` | status per pet: `todo` / `wip` / `review` / `done` | setiap commit |

Kalau ingin melihat gambar tanpa buka GitHub: `assets/pets/<petid>/render-88.png` sudah ada di repo, tinggal dibuka di editor.

## 3. Commit kecil, push tiap hari

Yang bikin owner buta bukan kurang kerja, tapi kerja yang tidak pernah di-push. Aturan:

- Boleh commit WIP: `asset(mochi): wip blocking` lalu push ke branch `asset/mochi`. Owner bisa lihat progres walau belum selesai.
- Jangan menumpuk 4 pet dalam satu branch. Satu pet satu branch, supaya satu pet bermasalah tidak menahan tiga lainnya.
- Jangan pernah `git push --force` ke `main`.
- Jangan commit: `*.rbxm`, `*.rbxl`, file `.blend` besar (taruh link di PR kalau perlu), screenshot desktop penuh.

## 4. Kalau belum bisa pakai git

Jangan diam. Pakai jalur drop, tetap kelihatan:

1. Upload `model.glb` + 3 colormap + 3 render ke folder Drive/Dropbox.
2. Tulis komentar di issue pet-nya: link folder + angka tri/tinggi + tanggal.
3. Status di `pet-assets.json` tidak diubah; owner yang commit file dan mengisi asset id.
4. Ini jalur darurat, bukan jalur utama. Kalau dipakai lebih dari 3 pet, pindah ke git.

## 5. Status yang jujur

`pet-assets.json` bukan papan prestasi, tapi papan kebenaran:

| Status | Arti | Boleh di-merge? |
|---|---|---|
| `todo` | belum mulai | ya (tidak ada file) |
| `wip` | mesh ada, belum lolos audit | ya, di branch |
| `review` | file lengkap, menunggu audit owner | ya |
| `done` | lolos audit + asset id sudah terisi | ya |

Jangan menaikkan status ke `done` sebelum owner mengisi asset id. Status yang terlalu cepat naik membuat jadwal terlihat aman padahal tidak.

## 6. Ritme laporan

- **Harian:** satu baris di issue pet yang dikerjakan, mis. "hari ini: cleanup ekor, sisa pivot".
- **Per pet:** PR (otomatis kelihatan owner).
- **Mingguan:** owner jalankan `check_assets.py`, ambil keputusan jalur A/B/C di `08` bagian 7.

Tidak perlu laporan panjang. Angka + gambar + link sudah cukup.