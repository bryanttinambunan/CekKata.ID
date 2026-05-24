# 🇮🇩 Bahasa Baku Detector v2.0

Sistem deteksi dan analisis penggunaan bahasa Indonesia baku secara otomatis.
Mendukung input teks manual maupun upload dokumen (PDF, DOCX, TXT).

---

## ✨ Fitur Baru (v2.0)

| Fitur | v1.0 | v2.0 |
|---|---|---|
| Input teks manual | ✅ | ✅ |
| Upload PDF | ❌ | ✅ |
| Upload DOCX | ❌ | ✅ |
| Upload TXT | ❌ | ✅ |
| Highlight kata tidak baku | ❌ | ✅ |
| Tooltip saran perbaikan | ❌ | ✅ |
| Statistik frekuensi kata | ❌ | ✅ |
| Top 5 kata tidak baku | ❌ | ✅ |
| Toast notifikasi | ❌ | ✅ |
| Drag & drop upload | ❌ | ✅ |
| Persentase kata tidak baku | ❌ | ✅ |

---

## 📁 Struktur Folder

```
bahasa_baku_detector_v2/
├── app.py                  ← Backend Flask utama
├── requirements.txt        ← Dependensi Python
├── README.md               ← Dokumentasi ini
└── templates/
    └── index.html          ← Frontend (HTML + CSS + JS)
```

---

## 🚀 Cara Menjalankan

### 1. Pastikan Python 3.8+ terinstal
```bash
python --version
```

### 2. (Opsional) Buat virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependensi
```bash
pip install -r requirements.txt
```

### 4. Jalankan server Flask
```bash
python app.py
```

### 5. Buka di browser
```
http://127.0.0.1:5000
```

---

## 📦 Dependensi

| Library | Kegunaan |
|---|---|
| `flask` | Web framework backend |
| `werkzeug` | Utilitas Flask (upload file) |
| `PyMuPDF` | Ekstrak teks dari PDF |
| `python-docx` | Ekstrak teks dari DOCX |
| `pypdf` | Fallback parser PDF |

---

## 🔌 API Endpoints

### `POST /deteksi`
Analisis teks dari input manual.

**Request Body:**
```json
{ "teks": "gue udah ngerjain tugasnya kemaren banget" }
```

**Response:**
```json
{
  "status": "tidak_baku",
  "label": "BAHASA TIDAK BAKU",
  "skor_baku": 28.6,
  "total_kata": 7,
  "jumlah_tidak_baku": 5,
  "persentase_tidak_baku": 71.4,
  "kata_tidak_baku": ["gue", "udah", "kemaren", "banget"],
  "saran_perbaikan": {
    "gue": "saya",
    "udah": "sudah",
    "kemaren": "kemarin",
    "banget": "sekali"
  },
  "top_kata_tidak_baku": [...],
  "highlighted_text": "...<mark>gue</mark>...",
  "temuan_pola": [...]
}
```

### `POST /upload`
Upload dan analisis dokumen (PDF, DOCX, TXT).

**Request:** `multipart/form-data` dengan field `file`

**Response:** Sama seperti `/deteksi`, ditambah `nama_file` dan `ukuran_teks`.

---

## 🧠 Cara Kerja

```
Input (Teks / Dokumen)
        ↓
[Parsing Dokumen — PDF/DOCX/TXT]
        ↓
Preprocessing (lowercase + tokenisasi regex)
        ↓
Dictionary Lookup (kamus 150+ kata tidak baku)
        ↓
Regex Pattern Matching (alay, singkatan, tanda baca)
        ↓
Hitung Skor Kebakuan (0–100%)
        ↓
Build Highlighted HTML (mark kata tidak baku)
        ↓
Output JSON → Render di Frontend
```

---

## 📊 Kriteria Klasifikasi

| Skor Kebakuan | Status |
|---|---|
| ≥ 80% | ✅ BAHASA BAKU |
| 60–79% | ⚠️ CAMPURAN |
| < 60% | ❌ BAHASA TIDAK BAKU |

---

## 🛠️ Pengembangan Lebih Lanjut

- Integrasikan library **Sastrawi** untuk stemming bahasa Indonesia
- Gunakan model **Machine Learning** (Naive Bayes / SVM / BERT)
- Tambah export hasil ke PDF/DOCX
- Tambah fitur "Teks yang Sudah Diperbaiki" otomatis
- Integrasikan dataset KBBI yang lebih lengkap
- Tambah dukungan file XLSX dan ODT
