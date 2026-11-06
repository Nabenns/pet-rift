# Pet Rift

Game Roblox genre **RNG pet collector**. Satu tombol: putar Kiln, dapat pet, koleksi 42 wujud (14 pet x 3 varian), kejar Divine yang peluangnya 1 banding 2.000.

Status: **pra-kode**. Isi repo sekarang: dokumen desain lengkap, tabel ekonomi (satu sumber angka), generator modul Luau dari tabel itu, simulator odds yang sudah lulus gate G1, dan satu pet contoh yang benar-benar dibangun di Roblox Studio.

## Dokumen

| File | Isi |
|---|---|
| `docs/00-DECISIONS.md` | Keputusan terkunci + alasannya, keputusan terbuka + default |
| `docs/01-PRD.md` | Masalah, pemain, prinsip, ruang lingkup v1/nanti/tidak akan pernah, gate G1-G10 berangka |
| `docs/02-TRD.md` | Stack + pin, topologi, algoritma roll (bobot integer + luck + pity) dengan pseudocode, rate limit, kontrak remote, performa, strategi uji |
| `docs/03-APP-FLOW.md` | Peta 4 layar, state machine roll, spesifikasi tiap layar, layout responsif, bukti capture per layar |
| `docs/04-DESIGN-BRIEF.md` | Palet hex + OKLCH, tipografi, aturan bentuk pet, motion, suara, aksesibilitas, anti-pola |
| `docs/05-BACKEND-SCHEMA.md` | Skema profil (inventori sebagai hitungan, bukan daftar item), operasi + invarian, migration, volume |
| `docs/06-IMPLEMENTATION-PLAN.md` | F0-F8, anggaran 10 hari, gate per fase, urutan commit, apa yang dikorbankan kalau molor |
| `docs/07-ART-PIPELINE.md` | Roster 14 pet + palet, parameter spec, anggaran part, style test 3 iterasi, audit otomatis |

## Struktur

```
design/economy.json     satu-satunya sumber angka (tier, bobot, pet, varian, harga, pity)
design/tokens.json      token warna UI
tools/gen_economy.py    economy.json -> src/shared/Economy.luau
tools/sim_rolls.py      100.000 roll x 3 skenario luck -> captures/G1-sim.csv (gate G1)
src/shared/Economy.luau HASIL GENERASI, jangan diedit tangan
src/pets/EmberFox.luau  pet contoh (Mythic), dibangun dari primitif
docs/                   dokumen di atas
captures/               screenshot iterasi + bukti gate
```

## Menjalankan

```bash
python3 tools/gen_economy.py     # regenerate Economy.luau dari economy.json
python3 tools/sim_rolls.py       # verifikasi distribusi roll (gate G1)
```

`sim_rolls.py` memakai algoritma yang sama dengan `Economy.luau`: bobot integer per 10.000, luck mengali tier chase lalu renormalisasi, pity memaksa Divine. Hasil terakhir: **G1 PASS** di luck 1,0 / 2,0 / 3,0 (100.000 roll per skenario, semua tier dalam toleransi). Bukti: `captures/G1-sim.csv`.

## Kendali Studio dari VPS

Studio berjalan di Mac, repo ini di VPS. Jalurnya MCP `roblox-studio` lewat reverse tunnel Tailscale:

1. Studio di Mac: Assistant > Manage MCP Servers > **Enable Studio as MCP server** (indikator harus 1 client).
2. Di VPS: `bash scripts/mac_roblox_mcp.sh` membuka tunnel ke `127.0.0.1:8790`.
3. Rebuild dari sumber: `python3 scripts/mcpcall.py call execute_luau '{"datamodel_type":"Edit","code":"..."}'`.

Repo sengaja menyimpan pet sebagai **kode Luau**, bukan `.rbxm`. Instance di Studio bisa hilang (pernah kejadian: place ter-reload, id Studio berubah), sedangkan file di repo tinggal dijalankan ulang.

## Kondisi seni (jujur)

Emberfox sudah dibangun di Studio dari 44 primitif: `src/pets/EmberFox.luau`. Review visual eksternal: **3-5 dari 10**. Geometri benar (4 kaki menyentuh lantai, telinga simetris, mata rata, kalung tidak tertutup kepala) — dibuktikan raycast, bukan opini — tapi belum terasa premium.

Rencananya ada di `docs/07-ART-PIPELINE.md` bagian 4: tiga iterasi gaya (proporsi -> penyederhanaan bentuk -> material dan cahaya), dinilai di 3 jarak. Kalau setelah T3 tetap di bawah 7/10, tier Mythic dan Divine pindah ke mesh; itu satu-satunya pengecualian aturan "primitif saja". Keputusan diambil sebelum F4, bukan setelah 14 pet dibangun.

![Emberfox](captures/hero-16.jpg)

## Kolaborasi

- Branch `main` lurus, commit kecil dan deskriptif, satu fase satu commit (`docs/06-IMPLEMENTATION-PLAN.md`).
- Dokumen di `docs/` adalah sumber kebenaran desain. Kalau kode dan dokumen berbeda, dokumen menang sampai diubah lewat commit yang jelas.
- Angka hanya boleh hidup di `design/economy.json`. Kalau angkanya berubah: ubah JSON, jalankan `gen_economy.py`, lalu perbarui tabel di `docs/01-PRD.md` dan `docs/02-TRD.md` dalam commit yang sama.
- Jangan commit file `.rbxl`, kredensial, atau token apa pun. Place file masuk release, bukan git.
