# 09 — KONTRAK ASET 3D (Astra -> Roblox)

Dokumen ini menggantikan asumsi "semua pet primitif" di `07` untuk jalur mesh. Primitif tetap ada sebagai fallback dan sebagai prototipe. Yang berubah: bentuk boleh datang dari luar (Astra/Blender), tapi **cara masuk ke game tetap satu pintu**.

## 1. Kenapa dua jalur

| | Primitif (`Pets/Builder`) | Mesh (`assets/pets`) |
|---|---|---|
| Waktu per pet | 45-90 menit | 40-120 menit (Astra + cleanup) |
| Hasil visual | 3-5/10 (jujur) | potensi 7-9/10, tergantung cleanup |
| Varian | ganti material + warna, gratis | butuh 3 colormap per pet |
| Risiko | terlihat seperti prototipe | topologi AI berantakan, tekstur gepeng |
| Peran | fallback + prototipe cepat + semua tier kalau 3D telat | tampilan rilis |

Keduanya hidup bersamaan dan dipilih lewat satu tabel: `design/pet-assets.json`. Kode tidak pernah bertanya "ini mesh atau primitif"; kode bertanya "pet ini punya mesh?". Kalau tidak, bangun primitif.

## 2. Interface

```
design/pet-assets.json   ->  tools/gen_pet_assets.py  ->  src/shared/PetAssets.luau
                                  (validasi roster)         (dibaca loader)
```

Bentuk satu entri:

```json
{
  "id": "Mochi",
  "tier": "Common",
  "build": "chibi",
  "height": 2.7,
  "mesh": "rbxassetid://0",
  "colormaps": { "Normal": "rbxassetid://0", "Golden": "rbxassetid://0", "Dark": "rbxassetid://0" },
  "tris": 0,
  "status": "todo"
}
```

- `mesh` dan `colormaps` diisi **setelah** upload, bukan sebelumnya. Sebelum itu `null`.
- `status`: `todo` -> `wip` -> `review` -> `done`. Loader hanya memakai entri `done`; entri lain jatuh ke primitif.
- Generator menolak jalan kalau daftar `id` di sini beda dengan `design/economy.json`. Itu pengaman supaya roster tidak pernah bercabang dua.

Aturan upload dan kepemilikan:

> Semua aset di-upload dari **akun pemilik place** (owner), bukan akun teman. Mesh dan tekstur yang di-upload ke akun lain tidak selalu bisa dipakai di place orang. Teman menyerahkan file `.glb` + `.png`; owner yang meng-import. Ini bukan soal kepercayaan, ini soal izin aset Roblox.

## 3. Spesifikasi mesh

| Properti | Nilai | Alasan |
|---|---|---|
| Triangle | target 3.000-5.000, maksimum 8.000 | batas engine ±20.000 per mesh, tapi 3 pet aktif x 5.000 = 15.000 tri plus map |
| Material | 1 material set, tanpa tekstur metalik/roughness terpisah di v1 | map tambahan memakan memori HP |
| Colormap | 512x512 (boleh 1024 untuk Divine), PNG, **tanpa lighting bake** | varian dibuat dari colormap |
| Tinggi | chibi 2,6-2,9 stud; long 2,2-2,5 stud | konsisten dengan primitif supaya bisa dicampur |
| Lebar / kedalaman | <= 3,0 / <= 3,6 stud | muat di jalur sempit dan tidak menutupi pemain |
| Pivot | titik (0,0,0) di tengah antara kedua kaki, di lantai | `PivotTo` langsung benar tanpa koreksi manual |
| Orientasi | depan menghadap **-Z** | sama dengan LookVector, jadi `CFrame.lookAt` tidak perlu rotasi 180 |
| Skala | 1 unit Blender = 1 stud? **Tidak.** Ekspor dengan skala 0,28 supaya 1 m = 0,28 stud? Tidak dipakai; pakai tinggi final dalam stud | menghindari bug skala 100x khas impor FBX |

Catatan skala: cara paling aman adalah menentukan tinggi final (mis. 2,7 stud) lalu di Blender memakai tinggi itu sebagai angka ekspor dalam satuan yang sama dengan Roblox. Roblox mengimpor 1 unit = 1 stud untuk GLB. Jangan mengandalkan auto-scale.

Bentuk:

- **Siluet dulu, detail belakangan.** Sebuah pet harus dikenali dari bentuk luarnya saja pada 88 px. Detail yang cuma terlihat dari dekat dibuang.
- **Kepala besar, badan kecil.** Rasio chibi: kepala ±45% tinggi total.
- **Mata sebagai bidang gelap**, bukan bola menonjol. Bola menonjol adalah penyebab utama hasil terlihat seperti mainan murah.
- **Kaki menapak lantai**, minimal 2 titik kontak terlihat dari depan.
- **Tidak ada bagian mengambang** (floating geometry) dan tidak ada bagian menembus badan.
- **Tidak ada tulisan, logo, atau pola yang menyerupai merek lain.**

Palet: 3 warna per pet dari tabel `07`, plus mata `#1A1030`. Kalau Astra mengembalikan gradien atau tekstur rambut realistis, tolak dan generate ulang dengan prompt yang lebih datar.

## 4. Varian tanpa mesh baru

Tiga colormap per mesh. Tidak ada geometri varian.

| Varian | Aturan colormap | Tambahan runtime |
|---|---|---|
| Normal | warna asli pet | tidak ada |
| Golden | naikkan lightness +12, geser hue ke `#FFE08A`, saturasi +10 | `Material = Metal` di mesh |
| Dark | turunkan lightness -35, geser hue ke `#4A3A6B` | mata `Neon` `#FF6B4A`, satu `PointLight` range 6 brightness 0,3 |

Aturan ini harus diikuti di colormap, bukan hanya di kode, karena `MeshPart.Color` mengalikan tekstur dan hasilnya keruh kalau tekstur sudah berwarna penuh. Tekstur Normal dibuat sedikit lebih terang dari target akhir supaya tint Golden tidak jadi coklat.

Kalau teman hanya sanggup 1 colormap per pet, Golden dan Dark dibuat lewat tint runtime dan hasilnya diterima sebagai "varian murah". Itu keputusan owner, dicatat di PR, bukan diam-diam.

## 5. Prompt Astra

Template. Ganti 4 bagian dalam kurung. Sisanya jangan diubah, karena bagian itu yang menjaga 14 pet terlihat satu keluarga.

```text
A stylized chibi game creature: {species}. {feature}.
Single character, standing, facing forward, centered, symmetric.
Big head (45% of total height), small rounded body, short stubby legs,
small flat dark eyes (not spherical, not glossy), tiny rounded ears.
Flat matte colors, no gradients, no baked lighting, no ambient occlusion,
no fur texture, no outlines, no text, no logo.
Palette limited to 3 colors: {body_hex} body, {belly_hex} belly, {accent_hex} accents.
Clean silhouette readable at small size, mobile game asset, low poly,
under 5000 triangles, single mesh, no rig, no ground plane, no shadow catcher.
```

Negative prompt (kalau tool-nya punya kolom sendiri):

```text
photorealistic, fur, hair strands, glossy, metallic, subsurface scattering,
complex detail, spikes, extra limbs, human hands, background, floor, pedestal,
text, watermark, blurry, painterly, anime shading
```

Prompt per pet (tempel ke `{species}` dan `{feature}`):

| Pet | species | feature |
|---|---|---|
| Mochi | round rabbit | very long upright ears, tiny pink nose |
| Pip | baby chick | small orange beak, round fluffy head (smooth, not feather texture) |
| Bonbon | chubby bear cub | round ears, short muzzle, wide round belly |
| Nori | river otter | long slim body, flat wide tail, small round ears |
| Kobo | mint green bear cub | tiny round ears, big head, calm expression |
| Fernpup | grass puppy | long muzzle, floppy pointed ears, leafy tail tip |
| Marble | white cat | tall pointed ears, long fluffy tail, calm eyes |
| Tide | axolotl | three feathery gills on each side of head, wide flat tail |
| Zephyr | sky bird | small rounded wings, tail feather fan, tiny beak |
| Vesper | purple bat-cat | tall pointed ears, wide thin wings folded, long tail |
| Aurelia | golden deer | thin antlers, long neck, small hooves, elegant |
| Volt | electric mouse | round ears, zigzag tail, cheek patches |
| Emberfox | fire fox | large pointed ears, big fluffy tail, chest fluff |
| Astraeon | glowing sea lion | fin-like ears, long sleek body, small glowing halo above head |

Untuk Astraeon dan Emberfox, tambahkan setelah prompt: `soft emissive glow on the halo and forehead gem only, rest of body matte`.

## 6. Alur kerja

```text
Astra (gambar/mesh awal)
   -> Blender: perbaiki siluet, potong jadi satu mesh, rapikan pivot, skala ke tinggi target
   -> ekspor GLB + render 3 jarak (8 stud / 30 stud / 88 px)
   -> commit ke assets/pets/<petid>/
   -> owner import ke Studio (Asset Manager -> Meshes), catat asset id
   -> owner isi design/pet-assets.json, jalankan gen_pet_assets.py
   -> owner jalankan auditBounds di Studio, foto hasilnya
   -> status: done
```

Kenapa Blender di tengah: output generator hampir selalu perlu dipotong (bagian terpisah, pivot di tengah benda, skala tidak konsisten). Memperbaiki di Blender 10 menit jauh lebih murah daripada memperbaiki lewat kode Luau.

## 7. Audit

Dijalankan owner di Studio setelah import, hasil disimpan di `captures/3d/audit-<petid>.txt`:

| Audit | Yang diperiksa | Gagal kalau |
|---|---|---|
| `auditBounds` | `GetBoundingBox()` model | tinggi di luar 2,2-3,2 stud, lebar > 3,0, bawah < -0,01 |
| `auditPivot` | jarak pivot ke titik tengah bawah bounding box | > 0,15 stud |
| `auditParts` | jumlah `BasePart` di model | > 3 (mesh + aksesori), atau ada `Part` sisa impor |
| `auditTris` | angka dari Asset Manager (bukan API) | > 8.000 |
| `vision` | 3 pertanyaan di `07` bagian 4 | kurang dari 3 "ya" untuk build final |

Angka tri tidak bisa dibaca dari Luau; catat dari jendela import dan tulis di PR. Jangan mengarang.

## 8. Yang tidak boleh dilakukan

| Jangan | Kenapa |
|---|---|
| Meng-upload aset dari akun teman | izin aset bisa gagal di place owner |
| Memakai tekstur hasil bake lighting | varian Golden/Dark jadi mustahil tanpa generate ulang |
| Mengganti tinggi mesh per pet sesuka hati | pet besar menutupi pemain di layar HP |
| Menambah part terpisah (mahkota, sayap) di luar mesh | jumlah draw call naik, animasi jadi dua objek |
| Membuat 14 mesh sebelum 1 mesh lolos gate | satu kesalahan proporsi = 14 kali ulang |
| Memakai nama atau bentuk yang menyerupai merek lain | risiko moderasi Roblox |

## 9. Kalau hasil Astra tidak cukup

Urutan eskalasi, jangan langsung menyerah:

1. Generate ulang dengan prompt lebih sederhana (buang detail, perbesar kepala).
2. Blender manual di atas hasil Astra: potong, gabung, ratakan warna. Ini yang paling sering menyelamatkan.
3. Turunkan target: mesh hanya untuk Mythic dan Divine, sisanya primitif. Sudah diperhitungkan di `08` jalur B.
4. Kalau tetap di bawah 7/10 untuk semua pet, hentikan jalur mesh dan kembali ke primitif. Keputusan owner, dicatat sebagai D12 di `00-DECISIONS.md`.