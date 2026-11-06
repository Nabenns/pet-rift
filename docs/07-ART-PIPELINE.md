# 07 — ART PIPELINE

Semua pet dibangun dari satu fungsi: `Pets/Builder.build(spec, variant) -> Model`. Tidak ada model yang dibangun manual di Studio. Ini yang membuat 14 pet x 3 varian = 42 hasil bisa dikelola satu orang.

## 1. Roster

14 pet, 7 tier, 4 Common / 2 Uncommon / 2 Rare / 2 Epic / 2 Legendary / 1 Mythic / 1 Divine. Warna: `body`, `belly`, `accent` (telinga dalam, moncong, ujung ekor).

| # | Pet | Tier | Build | Telinga | Ekor | body | belly | accent | Ciri |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Mochi | Common | chibi | tall | puff | `#F2E7D5` | `#FFF8EE` | `#E8A6B8` | kelinci, telinga panjang |
| 2 | Pip | Common | chibi | round | puff | `#F7C948` | `#FFE9A8` | `#F08A24` | anak ayam, moncong oranye |
| 3 | Bonbon | Common | chibi | round | fan | `#A9764F` | `#E0C39C` | `#6B4630` | beruang, badan bulat |
| 4 | Nori | Common | long | tall | fan | `#6F7C93` | `#C9D3E3` | `#3D4759` | berang-berang, badan panjang |
| 5 | Kobo | Uncommon | chibi | round | puff | `#7FD1AE` | `#D8F5E6` | `#3E8C6E` | beruang mint, telinga kecil |
| 6 | Fernpup | Uncommon | long | tall | fan | `#8FA84B` | `#DCE7B0` | `#4E6127` | anjing rumput, moncong panjang |
| 7 | Marble | Rare | chibi | tall | plume | `#EDEAF5` | `#FFFFFF` | `#7A6FA8` | kucing putih, ekor plume |
| 8 | Tide | Rare | long | fin | fan | `#58C3D6` | `#CFF3FA` | `#2A7C8C` | axolotl, insang |
| 9 | Zephyr | Epic | chibi | fin | plume | `#8FB8FF` | `#DCE9FF` | `#4A6FC4` | burung langit, sayap kecil |
| 10 | Vesper | Epic | long | tall | plume | `#8A6BC4` | `#D6C6F0` | `#4A3570` | kelelawar-kucing ungu |
| 11 | Aurelia | Legendary | chibi | tall | plume | `#F0C86A` | `#FFF0C9` | `#B07C28` | rusa emas + kalung |
| 12 | Volt | Legendary | chibi | round | fan | `#FFE45C` | `#FFF9C9` | `#C9A227` | tikus listrik + kalung |
| 13 | Emberfox | Mythic | chibi | tall | plume | `#E86F2B` | `#FFD9AE` | `#B85416` | rubah api + kalung + permata |
| 14 | Astraeon | Divine | long | fin | plume | `#2FA8B8` | `#DFF9FC` | `#7CF6FF` | singa laut bercahaya + kalung + permata + halo |

Tiga hal yang membedakan pet dalam satu tier supaya tidak terasa salinan: **tipe telinga (3 pilihan)**, **tipe ekor (3 pilihan)**, dan **proporsi (`chibi` vs `long`)**. Kombinasi 3 x 3 x 2 = 18, dipakai 14. Palet hanya 3 warna per pet; lebih dari itu tidak terbaca di thumbnail 88 px.

Komponen progresif per tier (bukan bentuk baru, tapi tambahan):

| Tier | Tambahan |
|---|---|
| Common-Uncommon | tidak ada |
| Rare-Epic | garis aksen 1 part di ekor |
| Legendary-Mythic | kalung emas (`#FFD24A`) |
| Mythic-Divine | permata dahi (`Neon`, warna tier) |
| Divine | halo 1 part (`Neon` `#7CF6FF`), tidak berputar di thumbnail |

## 2. Parameter spec (satu baris per pet)

```lua
export type PetSpec = {
    id: string, tier: string,
    build: "chibi" | "long",
    ears: "tall" | "round" | "fin",
    tail: "plume" | "puff" | "fan",
    body: Color3, belly: Color3, accent: Color3,
    eye: Color3?,            -- default #1A1030
    collar: boolean?,
    gem: boolean?,
    halo: boolean?,
}
```

Tidak ada field lain. Kalau sebuah pet butuh field di luar ini (mis. "sayap 3 part khusus"), pet itu salah desain, bukan spec-nya yang kurang.

## 3. Anggaran part

| Bagian | chibi | long |
|---|---|---|
| Badan + perut | 2 | 2 |
| Kepala + moncong | 2 | 2 |
| Mata | 2 | 2 |
| Blush | 2 | 2 |
| Telinga | 2 | 2 |
| Kaki + telapak | 8 | 8 |
| Ekor | 2-3 | 2-3 |
| Kalung (Legendary+) | 4 | 4 |
| Permata / halo | 1 | 1-2 |
| **Total** | **<= 28** | **<= 30** |

Emberfox yang sekarang 44 part karena telinga dan ekor dipecah jadi beberapa balok. Itu masih di bawah batas `02-TRD.md` (50), tapi untuk 14 pet, batas 30 lebih aman: 3 pet di layar x 30 = 90 part dinamis, jauh di bawah anggaran.

Aturan: **detail yang cuma kelihatan dari dekat dibuang.** Ujung ekor 3 balok tidak menambah apa pun di jarak 30 stud.

## 4. Style test (wajib sebelum F4)

Masalah nyata: review vision pet sekarang **3-5/10**. Penyebab yang paling sering muncul di review: proporsi (badan tertutup kepala), mata menonjol, dan material yang terlihat seperti prototipe. Tiga iterasi, satu pet (Emberfox), dinilai pada tiga jarak.

| Iterasi | Hipotesis | Yang diubah |
|---|---|---|
| T1 | proporsi chibi benar = cukup | baseline: kepala 1 : badan 1,1, mata pipih 0,18, 4 kaki menyentuh lantai |
| T2 | satu bentuk dominan lebih terbaca daripada banyak detail | kurangi part 44 -> 28; kepala +15%; mata +20%; dua warna per badan; buang detail ekor |
| T3 | material dan cahaya lebih menentukan daripada geometri | `SmoothPlastic` semua, rim light belakang `#7C6BFF` brightness 0,6, contact shadow (`Part` gelap pipih di bawah pet), `ColorCorrection` saturasi 1,1, `Bloom` threshold 1,2 intensity 0,4 |

Penilaian tiap iterasi (bukan opini, tapi tiga pertanyaan yang sama):

| Jarak | Pertanyaan | Lulus |
|---|---|---|
| 8 stud (close) | Apakah bentuknya disengaja, bukan kumpulan balok? | ya |
| 30 stud (gameplay) | Apakah masih dikenali sebagai hewan yang sama? | ya |
| 88 px (thumbnail index) | Apakah kebaca tanpa nama? | ya |

Ambang: minimal 2 dari 3 "ya" untuk T1 dan T2; 3 dari 3 untuk T3 sebelum gaya dikunci.

Keputusan yang harus diambil di akhir F3, tidak boleh ditunda:

1. **Blocky untuk semua tier** (kalau T3 >= 7/10). Jadwal tetap.
2. **Blocky untuk Common-Epic, mesh untuk Mythic/Divine** (kalau T2 lulus tapi T3 mentok). Tambah 1 hari, beli 2 aset.
3. **Semua ke mesh** (kalau T1/T2 gagal). F2 dibuang, jadwal +3 hari, dan seluruh alasan "42 hasil dari 14 model" hilang — varian jadi tekstur, bukan material.

## 5. Audit otomatis (bukan opsional)

Dua skrip kecil yang dipanggil dari `execute_luau`:

| Audit | Yang diperiksa | Gagal kalau |
|---|---|---|
| `auditVisibility` | raycast dari posisi kamera ke tiap part | ada part tidak terlihat (bug yang sudah pernah terjadi: 8 part kaki pindah ke world origin) |
| `auditBounds` | `GetBoundingBox()` tiap pet | ada bagian di bawah `y=0`, atau tinggi < 1,8 stud, atau lebar > 3,2 stud |
| `auditParts` | jumlah part, jumlah `Neon`, jumlah `PointLight` | part > 30, `PointLight` > 1 per pet |

Output audit disimpan ke `captures/pet-audit.txt`. Vision review dipakai untuk **estetika**; raycast dan bounds dipakai untuk **kebenaran**. Dua hal berbeda, jangan dicampur.

## 6. Varian

```
function applyVariant(model, variant)
    if variant == "Golden" then
        for part in parts: part.Material = Enum.Material.Metal; part.Color = part.Color:Lerp(Color3.fromHex("FFE08A"), 0.55)
    elseif variant == "Dark" then
        for part in parts: part.Color = part.Color:Lerp(Color3.fromHex("1A1030"), 0.55)
        eye.Material = Enum.Material.Neon; eye.Color = Color3.fromHex("FF6B4A")
        -- satu PointLight di dada: range 6, brightness 0.3, color FF6B4A
    end
end
```

Varian tidak boleh mengubah posisi, jumlah, atau ukuran part. Kalau sebuah varian butuh bentuk berbeda, itu pet baru, bukan varian.

## 7. Animasi

| Animasi | Implementasi | Biaya |
|---|---|---|
| Bob | `RunService.Heartbeat`, `sin(t*3)*0.06` pada `HumanoidRootPart`/`PrimaryPart` | 1 koneksi per pet aktif (maks 3) |
| Follow | `CFrame` lerp 0,15/frame ke titik 4 stud di belakang pemain | 1 koneksi per pemain |
| Ekor | rotasi `±4°` pada poros ekor, fase beda 0,4 s dari bob | digabung ke loop bob |
| Reveal spin | `TweenService` 3 fase, bukan loop | hanya saat reveal |

Tidak memakai `Animator`/`Animation` karena butuh aset animasi per rig, dan tiap pet akan butuh upload terpisah. Bob prosedural cukup untuk gaya ini dan nol aset.

## 8. Penamaan dan label

| Tempat | Format | Contoh |
|---|---|---|
| Nama pet | satu kata, huruf kapital di awal | `Emberfox`, bukan `Ember Fox` atau `EMBERFOX` |
| Tier | satu kata | `Mythic` |
| Varian | satu kata | `Golden` |
| Odds | `1 in N` dari tabel tier, bukan per pet | pet Mythic = `1 in 222` |
| Odds varian | hanya di panel odds, tidak di kartu | `Golden 12%` |

Nama pet harus bisa diucapkan anak 9 tahun dan tidak memakai kata yang sudah jadi merek (Pokemon, Digimon, Sanrio). Cek tiap nama di pencarian Roblox sebelum dipakai; kalau ada game populer dengan nama sama, ganti.

## 9. Urutan pembangunan

1. Emberfox (sudah ada) -> dipakai untuk T1-T3.
2. Empat Common (Mochi, Pip, Bonbon, Nori) -> menguji keempat kombinasi ekstrem: telinga tall/round, ekor puff/fan, build chibi/long.
3. Dua Uncommon, dua Rare -> memastikan aksen ekor tidak berlebihan.
4. Dua Epic, dua Legendary -> kalung pertama.
5. Mythic (Emberfox final), Divine (Astraeon) -> permata dan halo terakhir, karena butuh `Neon` + bloom.

Alasan urutan: setiap langkah menguji satu variabel baru. Kalau ke-14 dibangun sekaligus, satu kesalahan proporsi berarti 14 rebuild.