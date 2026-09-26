# Menfess Control System

## Struktur
```
menfess-system/
  core/
    keywords.py     -> 9 kategori + kata kunci
    topics.py        -> auto-match nama topic WTB! ke topic_id
    db.py             -> model database (log, wording, keywords, on/off)
    monitor.py       -> Amela: pantau base, filter, forward ke WTB!
    commands.py     -> Berline: dengar reply + command r1-r4
    executor.py       -> kirim wording via 4 akun, paralel + delay + retry floodwait
  dashboard/
    api.py             -> FastAPI, endpoint buat dashboard
    static/dashboard.html
  accounts/
    generate_session.py
  main.py             -> jalanin semua akun bareng
  requirements.txt
  Procfile
  .env.example
```

## 1. Ambil API ID & API Hash (1x aja, pakai akun Amela)
1. Buka https://my.telegram.org, login pakai nomor HP **Amela**.
2. API Development Tools -> buat App baru (nama bebas).
3. Catat `api_id` dan `api_hash`.

## 2. Generate session tiap akun (one-time, di laptop kamu)
Buat ke-6 akun (Amela, Berline, Geya, Shazald, Bear, Abillo):
```bash
pip install telethon
python accounts/generate_session.py
```
Masukin api_id/api_hash yang sama tiap kali (punya Amela), lalu login pakai
nomor HP akun yang lagi digenerate + kode OTP yang masuk ke akun itu. Copy
session string yang muncul ke `.env` sesuai nama (`SESSION_AMELA`,
`SESSION_BERLINE`, dst). **Jangan share session string ke siapa pun** — itu
setara password akun.

## 3. Isi `.env`
Copy `.env.example` -> `.env`, isi:
- `API_ID`, `API_HASH`
- 6 `SESSION_*`
- `WTB_GROUP` (username/ID grup WTB!)
- `SOURCE_BASES` (8 base yang mau dipantau, tanpa @, pisah koma)
- `JOCKEY_BASE`, `MONEY_BASE`
- `DATABASE_URL` (isi otomatis kalau attach plugin Postgres di Railway)

## 4. Pastikan topic WTB! namanya cocok
Kode nyari topic_id dengan cocokin **nama** topic (mengandung nama kategori,
case-insensitive) — jadi topic yang udah kamu buat ("Joki Tugas Umum ♡",
"Karya Tulis Ilmiah", dst) otomatis kedetect, nggak perlu di-hardcode.

## 5. Deploy ke Railway (cuma butuh 1 project, 2 service: Postgres + app)
Push folder ini ke repo GitHub (jangan ikutkan file `.env`), lalu di Railway:
1. **Buka 1 project yang sama** (jangan bikin project baru lagi kalau Postgres kamu udah ada di situ).
2. Kalau Postgres belum ada di project ini: klik **"+ New" -> Database -> Add PostgreSQL**.
3. Klik **"+ New" -> Deploy from GitHub repo**, pilih repo ini. Ini jadi service ke-2, isinya bot + dashboard jadi satu (nggak perlu bikin service ke-3).
4. Klik service dari GitHub itu -> tab **Settings** -> **Custom Start Command**, isi:
   ```
   uvicorn dashboard.api:app --host 0.0.0.0 --port $PORT
   ```
5. Masih di Settings -> **Networking** -> klik **Generate Domain** (ini link dashboard kamu).
6. Tab **Variables** -> **Raw Editor** -> paste semua isi `.env` kamu -> Save.
7. Tambah 1 variable lagi: **+ New Variable -> Add Reference -> pilih service Postgres -> pilih `DATABASE_URL`**.
8. Tunggu deploy selesai, buka link dashboard-nya.

Bot Telegram (Amela, Berline, 4 eksekutor) jalan otomatis di **background** di dalam
service yang sama begitu dashboard nyala — nggak perlu service terpisah.

## Alur singkat
- **Amela** pantau 8 base -> cocokin keyword -> forward ke topic yang sesuai
  di WTB! (Jockey Fess masuk semua, Moneyfess cuma yang match keyword).
- **Berline** reply menfess yang masuk di WTB!, ketik `r1`/`r2`/`r3`/`r4`.
  - r1-r3 -> Geya, Shazald, Bear, Abillo kirim paralel (delay random 0.5-2s,
    auto-retry kalau kena FloodWait).
  - r4 -> cuma Berline sendiri yang kirim.
- Pesan command Berline otomatis ke-edit jadi status ("MENFESS TERKIRIM OLEH
  SEMUA AKUN" + rincian per akun).
- Dashboard: nyalain/matiin tiap akun atau seluruh sistem, edit wording 1-5 &
  daftar keyword tanpa sentuh kode, lihat log real-time.

## Yang perlu kamu tes manual dulu
- Pastikan 4 eksekutor beneran bisa `send_message` ke comment section base
  (base biasanya linked discussion group terpisah dari channel utamanya) —
  kalau belum ke-invite/join di situ, reply-nya bakal gagal.
- Command matcher (`commands.py`) baca `fwd_from.channel_post` dari pesan
  yang di-reply — ini cuma keisi kalau menfess di-**forward** (bukan **copy**)
  dari base asli, jadi `monitor.py` sengaja pakai `forward_messages` bukan
  `send_message` supaya metadata ini kebawa.
