# 02 — TRD

Rujukan: `01-PRD.md` (gate G1-G10), `00-DECISIONS.md` (D1-D11), `design/economy.json` (satu-satunya sumber angka).

## 1. Stack dan pin

| Komponen | Pin | Cara verifikasi |
|---|---|---|
| Roblox Studio + Studio MCP | versi terpasang di Mac pemilik | `python3 scripts/mcpcall.py list` -> `RobloxStudio 1.0.0`, 34 tool |
| Referensi API engine | `refs/creator-docs` | `git -C refs/creator-docs rev-parse --short HEAD` |
| Bahasa | Luau `--!strict` | Validasi sintaks lewat `execute_luau` di datamodel Edit |
| ProfileStore | commit `45c9847cbcf1` (MadStudioRoblox/ProfileStore, 2025-07-31) | `curl -s api.github.com/repos/MadStudioRoblox/ProfileStore/commits/main` |
| Dependensi runtime lain | tidak ada | `grep -r "require(" src/ \| grep -v src/` harus kosong selain ProfileStore |
| Alat analisis | Python 3.12 stdlib | `tools/` tanpa paket eksternal |

ProfileStore tidak dipublikasikan di Wally dan repo-nya tidak punya tag rilis, jadi dipin lewat **commit SHA**, bukan nomor versi. File masuk sebagai `src/packages/ProfileStore.luau` (hasil ekspor `.rbxm`), dan SHA-nya ditulis di komentar kepala file.

Alasan memakai ProfileStore padahal aturan umum "tanpa dependensi": DataStore mentah tidak punya penguncian sesi, dan dua server yang menulis profil yang sama menghasilkan duplikat atau kehilangan item. Menulis session lock sendiri untuk menghindari satu library berarti memperbaiki bug yang sudah diperbaiki orang lain (D9).

## 2. Topologi

```
VPS Linux (repo, sumber kebenaran)              Mac (Roblox Studio)
+---------------------------+                  +-----------------------------+
| src/**.luau               |  execute_luau    | ServerScriptService/PetRift |
| design/economy.json       | ---------------> | ReplicatedStorage/PetRift   |
| tools/gen_economy.py      |                  | StarterPlayer/...           |
|   -> src/shared/Economy   |                  |                             |
| tools/sim_rolls.py        | <--- capture ----| Playtest / Edit datamodel   |
+---------------------------+   screen_capture +-----------------------------+
```

Yang tidak terjadi: game tidak melakukan HTTP ke VPS, tidak ada secret di dalam game, tidak ada remote ke luar Roblox.

Kendali Studio dari VPS lewat MCP `roblox-studio` di `http://127.0.0.1:8790/mcp` melalui reverse tunnel Tailscale (`scripts/mac_roblox_mcp.sh` di Mac). Ini satu-satunya jalur tulis ke Studio, dan semua yang ditulis berasal dari file repo.

## 3. Struktur dalam game

```
ServerScriptService/PetRift/
  Bootstrap.server.luau          -- satu-satunya Script
  Services/
    ProfileService.luau          -- ProfileStore wrapper + autosave + BindToClose
    RollService.luau             -- otoritas roll, luck, pity, rate limit
    EconomyService.luau          -- grant, jual, upgrade, equip
    MonetizationService.luau     -- satu-satunya ProcessReceipt
    LeaderboardService.luau      -- papan skor per server (memori, bukan OrderedDataStore)
ReplicatedStorage/PetRift/
  Shared/
    Economy.luau                 -- HASIL GENERASI dari economy.json, jangan diedit tangan
    Types.luau
  Client/
    Main.client.luau
    UI/Factory.luau              -- pembuat instance dari deskripsi tabel
    UI/RollScreen.luau
    UI/IndexScreen.luau
    UI/UpgradeScreen.luau
    UI/OddsPanel.luau
    Reveal.luau                  -- animasi 3 fase
  Pets/
    Builder.luau                 -- fungsi build(spec) -> Model, dipakai server dan index
    Specs.luau                   -- 14 spec pet (telinga, ekor, proporsi, warna)
  Packages/
    ProfileStore.luau            -- vendored, pinned 45c9847cbcf1
```

Aturan keras:

- Tidak ada `Script` kedua di `ServerScriptService`. Semua modul di-require dari `Bootstrap`.
- `grep -c ProcessReceipt src/` harus **tepat 1**.
- `src/shared/Economy.luau` adalah file hasil generate. Kalau diedit tangan, gate G10 gagal karena angkanya menyimpang dari `economy.json`.

## 4. Algoritma inti

### 4.1 Tabel berbobot, integer, jumlah tetap

Bobot disimpan sebagai **integer per 10.000** supaya tidak ada galat pembulatan float yang menumpuk saat luck dikalikan:

| Tier | Bobot | Per 10.000 | Peluang | Label |
|---|---|---|---|---|
| Common | 45,00 | 4500 | 45,0000% | 1 in 2,22 |
| Uncommon | 30,00 | 3000 | 30,0000% | 1 in 3,33 |
| Rare | 15,00 | 1500 | 15,0000% | 1 in 6,67 |
| Epic | 7,50 | 750 | 7,5000% | 1 in 13,3 |
| Legendary | 2,00 | 200 | 2,0000% | 1 in 50 |
| Mythic | 0,45 | 45 | 0,4500% | 1 in 222 |
| Divine | 0,05 | 5 | 0,0500% | 1 in 2.000 |

### 4.2 Luck: kali bobot chase, lalu renormalisasi

```
function Economy.weightsWithLuck(luck):
  w = copy(BASE_WEIGHTS)                    -- integer per 10.000
  for tier in CHASE:                        -- Legendary, Mythic, Divine
     w[tier] = math.floor(w[tier] * luck + 0.5)
  total = sum(w)                            -- berubah, bukan 10.000 lagi
  return w, total
```

Efek pada luck 2,0 dan 3,0 (dihitung dari tabel di atas):

| Tier | luck 1,0 | luck 2,0 | luck 3,0 |
|---|---|---|---|
| Common | 45,0000% | 43,9024% | 42,8571% |
| Uncommon | 30,0000% | 29,2683% | 28,5714% |
| Rare | 15,0000% | 14,6341% | 14,2857% |
| Epic | 7,5000% | 7,3171% | 7,1429% |
| Legendary | 2,0000% | 3,9024% | 5,7143% |
| Mythic | 0,4500% | 0,8780% | 1,2857% |
| Divine | 0,0500% | 0,0976% | 0,1429% |
| Total bobot | 10.000 | 10.250 | 10.500 |

Semua tier chase naik, semua tier bawah turun sedikit. Itu memang yang dijual: kesempatan ke tier atas, bukan menghapus hasil jelek. Angka di tabel ini wajib sama dengan output `tools/sim_rolls.py`; kalau beda, yang salah adalah implementasi.

### 4.3 Roll (server)

```
function RollService.roll(player)
  profile = Profiles:get(player)                  -- gagal load = tolak
  if not rateLimit:allow(player, "roll") then return end
  if #profile.inventory >= CAP_500 then return {err="full"} end

  local w, total = Economy.weightsWithLuck(profile.luck)
  local roll = rng:NextInteger(1, total)           -- rng = Random.new(profile.seed), seed disimpan
  local acc, tier = 0, nil
  for _, t in ipairs(Economy.TIER_ORDER) do        -- urutan tetap, deterministik
    acc += w[t]
    if roll <= acc then tier = t; break end
  end

  profile.rollsSinceDivine += 1
  local pityFired = false
  if profile.rollsSinceDivine >= Economy.PITY_THRESHOLD then
    tier = "Divine"; pityFired = true
  end
  if tier == "Divine" then profile.rollsSinceDivine = 0 end

  local pet = Economy.pickPet(tier, rng)           -- seragam di dalam tier
  local variant = Economy.rollVariant(rng)         -- Normal 85 / Golden 12 / Dark 3
  local record, isNew = EconomyService:grant(profile, pet.id, variant)

  return { tier=tier, petId=pet.id, variant=variant, isNew=isNew,
           pityFired=pityFired, rollsSinceDivine=profile.rollsSinceDivine }
end
```

Yang mengikat:

- `Random.new(seed)` per pemain, seed disimpan di profil. Hasil bisa direproduksi untuk audit. `math.random` global tidak dipakai karena tidak bisa diputar ulang.
- Pity dicek **setelah** roll, dan hanya memberi Divine. Pity tidak boleh mengubah bobot apa pun; dia mengganti hasil, bukan menggeser tabel.
- Varian diundi terpisah dari tier, jadi Divine Dark = 0,05% x 3% = 0,0015% (1 in 66.667). Itu hasil yang sah dan memang paling langka di game.
- Roll tidak menyentuh DataStore langsung. `profile.dirty = true`, autosave yang menulis.

### 4.4 Label odds

| Tampilan | Aturan |
|---|---|
| Persen | 4 desimal kalau < 1% (`0,0500%`), 2 desimal kalau >= 1% (`45,00%`) |
| `1 in N` | `1/p`, 3 angka penting (`1 in 2.220`) |
| Total | wajib 100,0000%; kalau pembulatan menghasilkan 99,9999%, tampilkan catatan pembulatan |
| Saat luck naik | panel menghitung ulang dari `Economy.weightsWithLuck(luck)` dan menampilkan delta per tier |

Panel memanggil fungsi yang sama dengan server. Tidak ada persentase yang diketik di klien.

## 5. Rate limit

| Aksi | Batas | Saat dilanggar |
|---|---|---|
| `RequestRoll` | 45/menit (token bucket, burst 5) | Tolak diam-diam; 20 pelanggaran dalam 10 detik -> kunci roll 5 detik |
| `RequestEquip` | 4/detik | Tolak |
| `RequestSell` | 10/detik | Tolak |
| `RequestUpgrade` | 4/detik | Tolak |
| `RequestPrompt` | 2/detik | Tolak |

Rate limit dicek **sebelum** lookup profil, sesuai urutan: tipe -> rentang -> rate -> kepemilikan.

Batas 45/menit dipilih dari cooldown tercepat yang mungkin: 3,0 detik x 0,92^8 = 1,53 detik, dibagi 2 dengan Fast Roll = 0,77 detik -> 78 roll/menit secara teori. Bucket 45/menit dengan burst 5 mengizinkan burst tapi menahan flood; pemain paling cepat tetap bisa roll terus karena burst mengisi ulang sepanjang menit. Kalau data rilis menunjukkan banyak pemain kena limit, naikkan ke 60 — bukan hapus limit.

## 6. Kontrak remote

| Remote | Arah | Payload | Validasi server |
|---|---|---|---|
| `RequestRoll` | C->S | `{}` | tabel kosong; rate limit; profil siap; inventori < 500 |
| `RollResult` | S->C | `{tier, petId, variant, isNew, pityFired, rollsSinceDivine, shards}` | tidak ada data rahasia (tabel bobot tidak pernah dikirim) |
| `RequestState` | C->S | `{}` | rate limit |
| `StateSync` | S->C | `{shards, luck, cooldown, inventory[], indexBits, equipped[]}` | - |
| `RequestEquip` | C->S | `{key: string}` | key ada di inventori pemanggil, format `PetId|Variant`, <= 40 char |
| `RequestSell` | C->S | `{key: string}` atau `{dupesOnly: true}` | kepemilikan; tidak boleh menjual key yang ada di `equipped` |
| `RequestUpgrade` | C->S | `{track: "luck"\|"speed"}` | track di whitelist; shard cukup (dihitung server) |
| `RequestPrompt` | C->S | `{productKey: string}` | key ada di `Products`; prompt dipanggil server |

Aturan: tidak ada harga, jumlah, tier, atau saldo yang dibaca dari payload klien.

## 7. Data dan sesi

Detail skema di `05-BACKEND-SCHEMA.md`. Kontrak tingkat TRD:

- Satu key per pemain: `player_{userId}`. Tidak ada key pendukung per fitur.
- Penguncian sesi dari ProfileStore (lease + fencing). Setelah sesi hilang, semua tulis berhenti, bukan mencoba lagi.
- Autosave 60 detik; `BindToClose` menyimpan semua profil paralel dengan `pcall` + retry, dilewati di Studio.
- Muat gagal -> pemain ditahan di layar "gagal memuat data", tidak bisa roll. Tidak ada profil default yang menimpa data lama.
- Migration function di ProfileStore dipakai untuk perubahan skema versi (`Profile.Data.version`), bukan `if data.field == nil then` yang berserak.

## 8. Monetisasi

| Aturan | Alasan |
|---|---|
| Satu `ProcessReceipt` di `MonetizationService`, dispatch lewat tabel produk | Dua penetapan = hanya yang terakhir menang |
| Grant dan `PurchaseId` ditulis dalam satu update profil | Crash di antara dua tulis = item gratis atau item hilang |
| Return `PurchaseGranted` hanya setelah simpan sukses | Kalau tidak, item hilang saat crash |
| Prompt dipanggil dari server | Klien tidak bisa memilih harga |
| `ArePaidRandomItemsRestricted` dicek saat join, **fail-closed** | v1 tidak menjual RNG, tapi jalur v1.1 disiapkan sekarang |
| Harga di `Products` dicocokkan dengan developer product ID di dashboard | Harga di klien tidak dipakai untuk transaksi |

## 9. Performa (angka)

| Metrik | Target | Cara ukur |
|---|---|---|
| Boot sampai tombol roll aktif | < 6 detik (mobile kelas menengah) | `os.clock()` di `Main.client` -> atribut `bootMs`, dibaca lewat `execute_luau` |
| Respons roll | p95 < 120 ms | 200 roll, catat `tick()` sebelum kirim dan saat `RollResult` |
| Frame saat reveal | >= 55 fps | `RenderStepped` sampling 5 detik |
| Partikel bersamaan | <= 120 | hitung emitter aktif di `Reveal` |
| Memori klien | < 250 MB setelah 10 menit | `Stats():GetTotalMemoryUsageMb()` |
| Part per pet | <= 50 | `#model:GetDescendants()` saat build |
| Ukuran profil | < 8 KB JSON | `#HttpService:JSONEncode(profile)` |

Batas 50 part per pet datang dari angka nyata: Emberfox 44 part. Kalau satu pet mendekati 50, kurangi detail, jangan naikkan batas — 3 pet sekaligus di layar x 50 part masih di bawah anggaran 200 part dinamis.

## 10. Strategi pengujian

Tidak ada framework uji Luau di lingkungan ini, jadi:

1. **Uji murni di Studio lewat `execute_luau`.** Modul `Tests/Spec.luau` (tidak di-require produksi) berisi assert dan mengembalikan `{passed, failed, failures[]}`. Menguji normalisasi luck, batas pity, pemilihan pet di dalam tier, dan penolakan payload. Dijalankan satu panggilan, hasilnya dibaca dari output.
2. **Simulasi odds di Python (`tools/sim_rolls.py`)** yang hanya membaca `economy.json`, menghasilkan 100.000 undian per skenario luck, dan menulis CSV. Tujuannya memverifikasi **angka dokumen**, bukan menggantikan uji runtime; karena itu dia tidak boleh menyalin logika Luau.
3. **Uji sesi dengan adapter palsu.** `ProfileService` menerima adapter; adapter uji menyimpan di tabel memori dan bisa dipaksa gagal. Skenario: 50 kegagalan tulis, dua sesi berebut key, rejoin setelah crash.
4. **Uji abuse.** Klien palsu mengirim 1.000 payload cacat (string, nil, uid orang lain, spam 500/menit) -> inventori tidak berubah.
5. **Uji visual.** `start_stop_play` -> `user_mouse_input` -> `screen_capture` -> review vision. Setiap layar di `03-APP-FLOW.md` wajib punya capture di `captures/`.
6. **Bukti gate.** Tiap gate G1-G10 punya file bukti `captures/G{n}-*` di repo.

Yang tidak diuji otomatis: pembelian Robux nyata. Diverifikasi manual dengan akun pemilik dan dicatat sebagai bukti teks.

## 11. Risiko teknis

| Risiko | Kenyataan | Mitigasi |
|---|---|---|
| Studio menutup -> tunnel mati, kerja berhenti | Terjadi di sesi pertama (place ter-reload, id berubah) | Semua aset adalah kode di repo; pulih = jalankan ulang builder, bukan reka ulang manual |
| `execute_luau` menolak file besar | Belum diuji di atas ~400 baris | Maksimum satu modul ~300 baris; pecah per tanggung jawab |
| DataStore tidak bisa diuji di Studio tanpa API access | Benar | Adapter palsu + uji perilaku |
| Rate limit 45/menit terlalu ketat untuk Auto Roll | Mungkin, kalau cooldown turun ke 0,77 detik | Ukur di rilis pertama; naikkan ke 60, jangan hapus |
| Pet blocky tidak cukup menarik | Skor review 3-5/10 | Style test sebelum F4; rencana fallback mesh untuk tier atas |