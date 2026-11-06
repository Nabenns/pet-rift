# 04 — DESIGN BRIEF

Arah visual: **malam ungu, benda bercahaya, bentuk yang kebaca dari jauh.** Bukan cute pastel, bukan neon cyberpunk. Referensi rasa: mainan plastik matte di bawah lampu hangat sore hari, di atas meja gelap.

Aturan yang menentukan semua keputusan di bawah: **satu pet harus kebaca sebagai makhluk yang sama dari jarak 30 stud dan dari thumbnail 88 px.** Kalau sebuah detail hilang di salah satu ukuran itu, detail tersebut dibuang, bukan diperkecil.

## 1. Palet

Warna dasar UI (bukan warna pet). Semua dari `design/tokens.json`.

| Token | Hex | OKLCH | Pakai untuk |
|---|---|---|---|
| `ink` | `#160F2B` | oklch(0.18 0.06 285) | latar layar, kartu |
| `dusk` | `#221C42` | oklch(0.26 0.07 285) | panel, panggung |
| `dusk2` | `#2D2852` | oklch(0.32 0.08 285) | kartu terangkat, hover |
| `line` | `#57508F` | oklch(0.48 0.10 285) | border 1 px, pemisah |
| `text` | `#F4F1FF` | oklch(0.96 0.02 285) | teks utama |
| `textMid` | `#D6D0F5` | oklch(0.87 0.04 285) | teks sekunder |
| `textDim` | `#9A93C4` | oklch(0.68 0.06 285) | label, hint |
| `gold` | `#FFD24A` | oklch(0.87 0.16 90) | shard, aksi utama, kalung |
| `danger` | `#FF5C7A` | oklch(0.66 0.20 15) | error, jual (konfirmasi) |
| `ok` | `#5FD08A` | oklch(0.78 0.15 150) | sukses, dimiliki |

Warna tier (dipakai konsisten di HUD, kartu, index, papan skor):

| Tier | Hex | Kenapa warna itu |
|---|---|---|
| Common | `#8FA0B8` | abu kebiruan, sengaja tidak menarik |
| Uncommon | `#5FD08A` | hijau muda, "lumayan" |
| Rare | `#4FA8FF` | biru terang, terbaca di latar ungu |
| Epic | `#B36BFF` | ungu terang, satu langkah dari latar |
| Legendary | `#FFC24A` | emas, kontras tertinggi terhadap ungu |
| Mythic | `#FF6B4A` | oranye-merah, panas |
| Divine | `#7CF6FF` | sian pucat, hampir putih, glow |

Aturan kontras: teks utama di atas `ink` = 13,8:1; teks tier di atas `ink` minimal 4,8:1. Divine `#7CF6FF` di atas `ink` = 12,1:1, jadi aman untuk teks; Legendary `#FFC24A` = 11,4:1.

## 2. Tipografi

| Peran | Font | Ukuran (px @1080p) | Weight | Catatan |
|---|---|---|---|---|
| Judul layar | Gotham SSm (built-in Roblox) | 40 | Bold | hanya satu per layar |
| Nama pet di kartu | Gotham SSm | 28 | Bold | huruf kapital di awal, bukan all-caps |
| Angka besar (odds, shard) | Gotham SSm | 32 | Bold | angka rata kanan supaya sejajar |
| Body / label | Gotham SSm | 16 | Medium | tidak pernah di bawah 14 |
| Hint | Gotham SSm | 14 | Regular | `textDim` |

Tidak memakai font kustom. Font butuh aset, aset butuh upload, upload butuh akun; Gotham SSm sudah ada di engine dan sudah terbaca di semua device. Ini keputusan biaya, bukan selera.

## 3. Bentuk dan material pet

Tiga aturan bentuk yang membuat 14 pet terasa satu keluarga:

1. **Kepala besar, badan pendek.** Rasio tinggi kepala : badan = 1 : 1,1 untuk `build: chibi`, 1 : 1,5 untuk `build: long`. Ini yang membuat semua pet terbaca "chibi", bukan "hewan realistis".
2. **Mata rata dan lebar.** Mata adalah `Part` pipih (tebal 0,18) yang ditanam di permukaan kepala, bukan bola yang menonjol. Mata menonjol terlihat seperti kelereng dan langsung menghancurkan gaya di thumbnail.
3. **Tidak ada sudut tajam.** Semua part memakai `SmoothPlastic` (varian Golden: `Metal`). Sudut dibiarkan kotak — itu gaya blocky — tapi warna dibuat matte supaya tidak terlihat seperti prototipe.

Komponen standar (sama untuk semua pet, yang berubah cuma parameter):

| Komponen | Boleh berubah | Tidak boleh berubah |
|---|---|---|
| Kepala | lebar, tinggi, warna | harus 1 part, harus di atas badan |
| Mata | lebar, warna, posisi | tebal 0,18, selalu 2, selalu rata |
| Telinga | tipe (`tall`/`round`/`fin`), sudut, warna | selalu simetris kiri-kanan, selalu 2 part |
| Badan | lebar, panjang, warna | selalu lebih lebar dari kepala |
| Perut | lebar, warna terang | selalu lebih terang dari badan |
| Kaki | jumlah 4, ketebalan | selalu 4, selalu menyentuh `y=0` |
| Ekor | tipe (`plume`/`puff`/`fan`), warna | selalu di belakang, selalu di atas `y=0,3` |
| Kalung | ada/tidak, warna | hanya untuk Legendary ke atas, warna `gold` |
| Permata dahi | ada/tidak | hanya Mythic dan Divine |

## 4. Varian

| Varian | Cara render | Efek yang diizinkan |
|---|---|---|
| Normal | warna asli pet, `SmoothPlastic` | - |
| Golden | semua part `Metal`, tint `#FFE08A` dikalikan warna asli | tidak ada glow (biar tidak norak) |
| Dark | warna asli x 0,35, mata jadi `Neon` warna `#FF6B4A`, aura ungu tipis | satu `PointLight` lemah di dada (range 6, brightness 0,3) |

Varian **tidak** mengubah bentuk. Pet Golden bukan pet baru; dia pet yang sama dengan material berbeda. Itu sebabnya 14 model menghasilkan 42 hasil.

## 5. Tata letak panggung (preview)

Yang sudah terbukti di Studio dan dipakai sebagai default:

| Elemen | Nilai |
|---|---|
| Panggung | `Part` 30 x 0,6 x 30 @ `CFrame.new(0, -0.2, 22)`, warna `#221C42` |
| Posisi pet | dihitung dari `GetBoundingBox()` supaya dasar menyentuh `y = 0.1` |
| Kamera | `CFrame.lookAt(pet + Vector3.new(0, 2.2, 7.5), pet + Vector3.new(0, 1.7, 0))` |
| Lighting | `ClockTime 15.2`, `Brightness 1.7`, `ExposureCompensation 0.1`, `GlobalShadows true` |
| Ambient | `rgb(96,92,120)`, `OutdoorAmbient rgb(130,128,155)` |
| Lampu kunci | `PointLight` hangat di atas-depan, range 18, brightness 1,2, warna `#FFD9B0` |

Kalau panggung dipindah, hitung ulang pivot dari bounding box — jangan mengasumsikan `PrimaryPart` ada di `y=0`. Ini bug yang sudah terjadi sekali dan membuat seluruh pet tenggelam 1,4 stud.

## 6. Gerak

| Animasi | Durasi | Easing | Catatan |
|---|---|---|---|
| Pet bob (idle) | 1,6 s loop | sinus | ±0,06 stud vertikal, ekor ±4 derajat |
| Pet follow | 0,35 s | lerp 0,15/frame | jarak target 4 stud, tidak pernah menempel ke karakter |
| Reveal spin | 2,4 s | 3 fase: 1,2 s cepat, 0,7 s melambat, 0,5 s berhenti | fase terakhir yang menahan tier |
| Kartu masuk | 0,25 s | `Quad Out` | dari 92% ke 100% skala + fade |
| Cooldown ring | sesuai durasi | linear | tidak pernah "melompat" |
| Tombol press | 0,08 s | - | skala 0,96 saat `InputBegan` |

Tidak ada animasi lebih dari 2,5 detik selain reveal. Tidak ada animasi yang bisa memperlambat pemain (tidak ada layar yang dikunci lebih dari yang tertulis).

## 7. Suara

| Kejadian | Suara | Volume |
|---|---|---|
| Tap roll | klik pendek | 0,4 |
| Reveal Common/Rare | ding lembut | 0,5 |
| Reveal Epic/Legendary | ding + shimmer | 0,6 |
| Reveal Mythic | naik 3 nada | 0,7 |
| Reveal Divine | chord + reverb panjang 1,4 s | 0,8 |
| Jual | koin pendek | 0,4 |
| Error | buzz rendah 120 ms | 0,5 |

Musik latar: satu loop 60 detik, ambient, volume 0,25, bisa dimatikan di Pengaturan. Tidak ada suara saat AFK atau saat game tidak fokus.

## 8. Aksesibilitas

- Semua target sentuh >= 44 px; tombol utama 160-200 px.
- Tidak ada informasi yang **hanya** disampaikan lewat warna: tier selalu punya label teks, bukan cuma border.
- Teks minimal 14 px; angka odds 16 px minimum.
- Kontras teks minimal 4,5:1 terhadap latar kartu.
- Efek layar (flash Divine, shake) bisa dimatikan di Pengaturan; tidak ada flash lebih dari 3 kali per detik.
- Animasi tidak pernah memblokir input lebih dari 0,6 detik kecuali reveal (yang boleh di-skip).

## 9. Anti-pola (jangan dilakukan)

- Gradient ungu-biru "AI startup" di latar, glow berlebihan, atau drop shadow tebal di semua elemen.
- Emoji di UI game. Ikon dibuat dari bentuk (`Frame` + `UICorner` + `ImageLabel` yang sudah ada), bukan teks emoji.
- Outline hitam tebal + hard shadow di semua komponen (neo-brutalism) — itu bertabrakan dengan pet yang bertekstur lembut.
- Kartu dengan 5 warna aksen. Satu aksen per layar.
- Teks placeholder seperti "Lorem" atau angka `0` yang tidak pernah terisi.
- Menaruh pet di tengah layar belakang UI; pet harus punya ruang sendiri atau jadi bagian dari kartu.

## 10. Yang diukur, bukan dirasa

| Klaim | Cara bukti |
|---|---|
| "Pet kebaca dari jauh" | capture pada jarak 30 stud + thumbnail 88 px; harus dikenali tanpa nama |
| "Warna tier beda jelas" | pasangan warna diuji buta huruf warna (deuteranopia): Rare vs Uncommon harus tetap beda **bentuk label**, bukan cuma warna |
| "UI tidak penuh" | maksimum 5 elemen interaktif terlihat di HUD |
| "Konsisten" | 3 pet terakhir (Mythic, Divine, satu Common) dibangun dari spec yang sama; kalau butuh part khusus di luar daftar komponen, spec-nya salah |

Skor review vision yang sekarang 3-5/10 adalah masalah nyata, bukan noise. Rencana penanganannya ada di `07-ART-PIPELINE.md` bagian style test: tiga iterasi dengan aturan berbeda sebelum gaya dikunci, dan kalau tetap gagal, tier Mythic/Divine pindah ke mesh (satu-satunya pengecualian aturan "primitif saja").