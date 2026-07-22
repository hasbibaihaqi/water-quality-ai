# Water Quality AI 💧

Aplikasi prediksi kelayakan air minum berbasis Machine Learning (Support Vector Machine - RBF Kernel) yang dikembangkan sebagai proyek Ujian Akhir Semester (UAS) mata kuliah Kecerdasan Buatan.

## 🚀 Fitur Utama

- **Prediksi Akurat**: Menggunakan 9 parameter kualitas air standar WHO.
- **Machine Learning Engine**: Dibangun dengan Scikit-Learn menggunakan Support Vector Machine (SVM) dengan RBF Kernel.
- **Robust Preprocessing**: 
  - Penanganan missing values menggunakan Median Imputation.
  - Penanganan outlier dengan IQR Capping.
  - Penanganan ketidakseimbangan kelas menggunakan SMOTE (Synthetic Minority Over-sampling Technique).
  - Feature Scaling menggunakan StandardScaler.
- **Glassmorphism UI**: Antarmuka modern, interaktif, dan responsif dengan tema dark mode.
- **Analisis & Rekomendasi**: Tidak hanya memberikan hasil "Layak" atau "Tidak Layak", tetapi juga memberikan tingkat keyakinan (confidence), status tiap parameter terhadap batas aman WHO, dan rekomendasi tindakan.

## 🛠️ Teknologi yang Digunakan

### Backend & Machine Learning
- **Python 3.11**
- **Flask 3.0** (Web Framework)
- **Scikit-Learn 1.9** (Model Training & Evaluation)
- **Imbalanced-Learn** (SMOTE)
- **Pandas & NumPy** (Data Manipulation)
- **Joblib** (Model Serialization)

### Frontend
- **HTML5 & CSS3** (Custom Glassmorphism Design)
- **JavaScript (ES6)** (Interactivity, Particles, Form Validation)
- **Bootstrap 5.3** (Grid System & Utility)
- **Bootstrap Icons** (UI Icons)

## 📁 Struktur Direktori

```text
water-quality-ai/
│
├── app.py                      # File utama Flask backend
├── config.py                   # Konfigurasi global & definisi fitur/label
├── requirements.txt            # Daftar dependensi Python
├── README.md                   # Dokumentasi proyek
│
├── dataset/
│   └── water_potability.csv    # Dataset Kaggle
│
├── models/                     # Tempat model disimpan setelah training
│   ├── model.pkl               # Model ML yang sudah dilatih (SVM)
│   ├── scaler.pkl              # StandardScaler untuk normalisasi
│   └── training_metadata.json  # Metadata & evaluasi model
│
├── notebooks/
│   └── training.py             # Script otomatisasi pipeline ML (EDA, Preprocessing, Training, Evaluasi)
│
├── utils/
│   ├── __init__.py
│   ├── predictor.py            # Logic load model dan melakukan prediksi
│   └── preprocessing.py        # Logic validasi dan parsing input form
│
├── static/
│   ├── css/
│   │   └── style.css           # Custom styling (Glassmorphism)
│   ├── js/
│   │   └── script.js           # Frontend logic & animations
│   └── images/                 # Hasil visualisasi dari script training
│
└── templates/
    ├── base.html               # Layout utama HTML
    ├── index.html              # Halaman Beranda
    ├── predict.html            # Halaman Form Prediksi
    ├── result.html             # Halaman Hasil & Rekomendasi
    ├── about.html              # Halaman Tentang & Metrik ML
    ├── 404.html                # Error Page 404
    └── 500.html                # Error Page 500
```

## 🔧 Panduan Instalasi & Menjalankan Aplikasi

1. **Pastikan Python 3.11 terinstall** di sistem Anda.
2. **Buka Terminal/Command Prompt** dan arahkan ke direktori proyek:
   ```bash
   cd water-quality-ai
   ```
3. **Install dependensi**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Jalankan script training (WAJIB)** untuk menghasilkan model ML:
   ```bash
   python notebooks/training.py
   ```
   *(Tunggu hingga proses selesai dan memastikan `model.pkl` dan `scaler.pkl` terbuat di folder `models/`)*
5. **Jalankan aplikasi web Flask**:
   ```bash
   python app.py
   ```
6. Buka browser dan akses: `http://127.0.0.1:5000`

## 📊 Dataset

Dataset yang digunakan bersumber dari Kaggle: [Water Potability Dataset](https://www.kaggle.com/datasets/adityakadiwal/water-potability). 
Terdiri dari 3276 observasi dengan 9 variabel independen (parameter air) dan 1 variabel dependen (Potability - 0: Tidak Layak, 1: Layak).

## 👨‍💻 Pengembang

Dikembangkan sebagai pemenuhan Tugas Akhir / UAS mata kuliah Kecerdasan Buatan (Artificial Intelligence).
