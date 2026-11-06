# assets/pets — aset 3D

Satu folder per pet, nama folder huruf kecil tanpa spasi: `mochi`, `pip`, `emberfox`.

```
assets/pets/mochi/
  model.glb          mesh final, <= 5.000 tri, pivot di lantai, menghadap -Z
  colormap-normal.png  warna asli
  colormap-gold.png    varian Golden
  colormap-dark.png    varian Dark
  render-08.png      tangkapan 8 stud (close)
  render-30.png      tangkapan 30 stud (gameplay)
  render-88.png      thumbnail 88 x 88 px
  meta.json          angka tri, tinggi, lebar, kedalaman, tanggal, status
```

Aturan:

1. Tidak ada `lighting bake` / bayangan di colormap. Varian dibuat dari colormap, jadi tekstur yang sudah gelap tidak bisa diterangkan lagi.
2. Nama file persis seperti di atas. Huruf kecil, tanda hubung, tanpa spasi.
3. Satu pet satu PR. Branch `asset/<petid>`.
4. Setelah file masuk, isi `design/pet-assets.json` (mesh/colormaps masih `null` sampai owner upload) dan ubah `status` ke `review`.
5. Ukuran final ditentukan tinggi dalam stud, bukan skala Blender: `chibi` 2,6-2,9; `long` 2,2-2,5.

Spesifikasi lengkap: `docs/09-3D-CONTRACT.md`. Definisi selesai per pet: `docs/08-TASK-SPLIT.md` bagian 4.
