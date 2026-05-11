# 📈 TPID Dashboard — Kab. Pekalongan

Dashboard monitoring harga komoditas dan inflasi daerah berbasis **Streamlit + Supabase**.

## 🚀 Fitur
- **Beranda** — Ringkasan inflasi (Kota Tegal / Jawa Tengah / Nasional) & kartu harga komoditas terkini
- **Analisis HBK** — Pola harga sekitar Idulfitri, Natal, Tahun Baru (multi-tahun)
- **Detail Harga** — Pivot tabel harian + IPH mingguan per komoditas
- **Manajemen Data** — CRUD harga harian, inflasi, komoditas, pasar via Supabase
- **Laporan** — Ekspor CSV ringkasan bulanan + rekomendasi otomatis

## 🗄️ Skema Database (Supabase)

```sql
-- Tabel komoditas
CREATE TABLE komoditas (
  id_komoditas SERIAL PRIMARY KEY,
  nama_komoditas VARCHAR NOT NULL,
  satuan VARCHAR NOT NULL
);

-- Tabel pasar
CREATE TABLE pasar (
  id_pasar SERIAL PRIMARY KEY,
  nama_pasar VARCHAR NOT NULL,
  kabupaten VARCHAR,
  kecamatan VARCHAR
);

-- Tabel harga harian
CREATE TABLE harga_harian (
  tanggal DATE NOT NULL,
  id_komoditas INT4 REFERENCES komoditas(id_komoditas),
  id_pasar INT4 REFERENCES pasar(id_pasar),
  harga INT4 NOT NULL,
  PRIMARY KEY (tanggal, id_komoditas, id_pasar)
);

-- Tabel inflasi
CREATE TABLE inflasi (
  id_inflasi SERIAL PRIMARY KEY,
  tahun INT4 NOT NULL,
  bulan INT4 NOT NULL,
  level_wilayah VARCHAR NOT NULL,
  nama_wilayah VARCHAR NOT NULL,
  inflasi_mtm NUMERIC,
  inflasi_ytd NUMERIC,
  inflasi_yoy NUMERIC,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## ⚙️ Cara Jalankan Lokal

```bash
# 1. Clone repositori
git clone https://github.com/USERNAME/tpid-dashboard.git
cd tpid-dashboard

# 2. Install dependensi
pip install -r requirements.txt

# 3. Jalankan aplikasi
streamlit run app.py
```

## ☁️ Deploy ke Streamlit Cloud (Manual)

Lihat bagian **Langkah Deploy** di bawah.

---

## 📦 Struktur File

```
tpid_dashboard/
├── app.py              # Aplikasi utama Streamlit
├── database.py         # Client Supabase (CRUD semua tabel)
├── utils.py            # CSS, konstanta, helper chart
├── requirements.txt    # Dependensi Python
├── .streamlit/
│   └── config.toml     # Konfigurasi tema dark
└── README.md
```
