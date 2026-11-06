# 05 — BACKEND SCHEMA

Sumber: ProfileStore (pinned `45c9847cbcf1`). Satu key per pemain, satu tabel, satu migration function.

## 1. Kenapa inventori disimpan sebagai hitungan, bukan daftar item

Keputusan yang membentuk seluruh dokumen ini: **pet bersifat fungible per (petId, variant)**. Dua `Mochi Normal` identik dan tidak punya identitas sendiri. Karena itu inventori disimpan sebagai:

```
inventory["Mochi|Normal"] = 3
```

bukan sebagai array 500 record. Konsekuensinya:

| Aspek | Hasil |
|---|---|
| Ukuran profil | <= 2 KB walau inventori penuh (maks 42 key, bukan 500 record) |
| Duplikat | tidak mungkin ada dua record yang menyimpang (mis. satu Golden satu Normal dengan key sama) |
| Jual duplikat | satu operasi aritmetika, tidak bisa menghapus pet terakhir yang di-equip |
| Nama pet | disimpan per key (`names[key]`), jadi mengganti nama tidak membuat item baru |
| Trading (v2) | butuh identitas unik per item; itu migration v2, bukan alasan mengubah v1 sekarang |

Yang dikorbankan: pemain tidak bisa punya dua `Mochi Normal` dengan nama berbeda. Itu diterima (D7).

## 2. Template profil

```lua
local TEMPLATE = {
    version = 1,

    shards = 0,                      -- integer, 0 .. 9_999_999
    luckLevel = 0,                   -- 0 .. 10   (upgrade shard)
    speedLevel = 0,                  -- 0 .. 8    (upgrade shard)
    rollsSinceDivine = 0,            -- 0 .. 8000 (pity)
    totalRolls = 0,                  -- statistik, tidak dipakai logika

    inventory = {},                  -- ["PetId|Variant"] = count (1..99)
    names = {},                      -- ["PetId|Variant"] = string (<= 16 char, sudah difilter)
    equipped = {},                   -- array of key, maks 3 (1 gratis, 3 dengan VIP)

    seed = 0,                        -- integer, dibuat sekali saat profil baru
    ownedPasses = {},                -- ["FastRoll"] = true, ditulis dari ProcessReceipt
    ownedProducts = {},              -- ["PurchaseId"] = true, idempotensi receipt
    tutorialDone = false,
    restrictions = { paidRandomAllowed = false },  -- hasil PolicyService saat join, tidak dipakai v1
    lastSavedAt = 0,                 -- os.time() saat simpan sukses
}
```

Tipe yang dipaksakan saat load (bukan saat tulis): semua field numerik di-`math.floor`, semua string dipotong, `inventory` dibersihkan dari key yang tidak ada di `Economy.PETS`, `equipped` dipotong ke batas slot. Kalau ada field yang hilang, migration yang menambal; kode fitur tidak boleh menambal sendiri.

## 3. Key dan batas

| Key DataStore | Isi | Batas |
|---|---|---|
| `player_{userId}` | satu template di atas | < 4 MB (batas engine); target < 2 KB |

Tidak ada key kedua. Papan skor per server disimpan di memori server (tabel Lua), bukan `OrderedDataStore`; itu menghindari satu request DataStore per roll dan cukup untuk kebutuhan v1 ("top 10 di server ini").

## 4. Operasi dan invariannya

| Operasi | Perubahan | Invarian yang dijaga |
|---|---|---|
| Roll | `inventory[key] += 1`, `rollsSinceDivine`, `totalRolls` | total item <= 500; count <= 99; tidak menyentuh `shards` |
| Jual satu | `inventory[key] -= 1`, `shards += nilai` | tidak boleh menjual key yang ada di `equipped`; count >= 1 sebelum dikurangi |
| Jual duplikat | untuk tiap key: sisakan 1, sisanya diuangkan | minimal 1 salinan tiap key yang dimiliki tetap ada |
| Equip | `equipped` diisi key yang ada di inventori | panjang `equipped` <= slot (1 + 2 kalau VIP) |
| Upgrade | `shards -= cost`, `luckLevel` atau `speedLevel` +1 | `shards >= cost` dihitung server; level <= maksimum |
| Nama | `names[key] = filtered` | hanya key yang dimiliki; <= 16 karakter setelah filter |
| Receipt | `ownedPasses[key] = true`, `ownedProducts[id] = true` | satu update dengan grant; `PurchaseId` tidak pernah diproses dua kali |

Nilai jual dihitung dari `Economy.TIERS[tier].shard * VARIANTS[variant].shard_mult`, dibulatkan ke bawah. Harga upgrade dari `Economy.upgradeCost(track, level)`. Keduanya fungsi murni, tidak menyimpan tabel harga di profil.

## 5. Alur load dan simpan

```
PlayerAdded
  rateLimit reset
  profile = ProfileStore:StartSessionAsync("player_"..userId, { Cancel = function() return player.Parent == nil end })
  if not profile then  -> tampilkan layar GAGAL MUAT, jangan buat profil baru
  profile:AddUserId(userId)          -- GDPR: DataStore bisa menghapus data saat akun dihapus
  profile:Reconcile()                -- isi field yang hilang dari TEMPLATE
  profile.OnSessionEnd = ...         -- pemain keluar di server lain / sesi dicabut

  state = buildState(profile)        -- dikirim ke klien lewat StateSync
  profile.OnAfterSave = function() profile.Data.lastSavedAt = os.time() end

PlayerRemoving -> profile:EndSession()
BindToClose   -> simpan semua sesi paralel (pcall + retry), tunggu selesai, dilewati di Studio
```

Aturan yang tidak boleh dilanggar:

- **Tidak ada fallback ke profil default** saat load gagal. Profil default di atas data lama = penghapusan data pemain.
- Autosave tidak dipanggil manual per aksi. ProfileStore punya `AutoSaveProfiles` (30 detik default); aksi hanya set `dirty` untuk UI, bukan memicu tulis.
- `profile.Data` tidak pernah dikirim mentah ke klien. `buildState()` memilih field yang aman (tanpa `seed`, tanpa `ownedProducts`).

## 6. Migration

`version` = 1 sekarang. Migration function dipakai untuk perubahan skema:

```lua
local function migrate(data, oldVersion)
    if oldVersion < 1 then
        data.inventory = data.inventory or {}
        data.equipped = data.equipped or {}
    end
    -- tambahan versi berikutnya di sini, satu blok per versi
    data.version = 1
    return data
end
```

Alasan tidak memakai `if data.x == nil then` di kode fitur: penambalan tersebar tidak bisa diaudit, dan tidak ada satu tempat untuk tahu skema mana yang sedang berjalan.

## 7. Estimasi volume (untuk kapasitas, bukan tebakan)

| Skenario | Profil | Pemain | Total |
|---|---|---|---|
| Rata-rata | 1,2 KB | 1.000 DAU | 1,2 MB |
| Berat (inventori penuh, 42 key) | 2,0 KB | 10.000 DAU | 20 MB |

DataStore gratis Roblox memberi kuota penyimpanan yang jauh di atas ini. Yang jadi batas bukan ukuran, tapi **frekuensi tulis**: 1 tulis per 30 detik per server per pemain. Dengan 30 pemain per server, itu 60 tulis/menit/server, di bawah batas 60 + 10 x pemain per menit. Aman.

## 8. Titik rawan dan penanganannya

| Titik | Kenyataan | Penanganan |
|---|---|---|
| Dua server memuat pemain sama | Bisa terjadi saat teleport/rejoin cepat | ProfileStore mengunci sesi; sesi kedua menunggu atau menolak. Kode tidak menulis tanpa sesi aktif |
| Server mati di tengah roll | Data roll belum tersimpan | Roll adalah perubahan state yang sah untuk hilang (pemain bisa roll sekali lagi); yang tidak boleh hilang adalah **item yang sudah terlihat di layar**. Karena itu `RollResult` dikirim setelah `grant` di memori, dan autosave menulis <= 30 s. Kompromi diterima: crash = 1 roll hilang, bukan item hantu |
| Server mati setelah receipt dibayar | Paling mahal | `PurchaseId` + grant dalam satu update; `PurchaseGranted` dikirim setelah simpan sukses |
| `DataStore` rate limited | Bisa saat 30 pemain keluar bersamaan | Satu sesi per pemain, retry bawaan ProfileStore, `BindToClose` paralel dengan timeout total 25 detik |
| Pemain hapus akun (GDPR) | Roblox menandai, bukan menghapus | `AddUserId` wajib; tanpa itu data tetap ada setelah akun dihapus |

## 9. Data yang tidak disimpan

Tidak disimpan di DataStore: posisi karakter, state UI, hasil roll terakhir, isi papan skor, waktu cooldown. Semuanya bisa direkonstruksi atau memang seharusnya hilang saat rejoin.