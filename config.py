# -*- coding: utf-8 -*-
"""
config.py - Konfigurasi Aplikasi Water Quality AI
Berisi semua konstanta dan pengaturan global aplikasi.
"""

import os

# ==============================================================================
# KONFIGURASI DASAR FLASK
# ==============================================================================
SECRET_KEY = os.environ.get('SECRET_KEY', 'water-quality-ai-secret-2024')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# ==============================================================================
# PATH PENTING
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'model.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'models', 'scaler.pkl')
METADATA_PATH = os.path.join(BASE_DIR, 'models', 'training_metadata.json')
DATASET_PATH = os.path.join(BASE_DIR, 'dataset', 'water_potability.csv')

# ==============================================================================
# KONFIGURASI FITUR INPUT
# Urutan fitur HARUS sama persis dengan urutan saat training
# ==============================================================================
FEATURE_NAMES = [
    'ph',
    'Hardness',
    'Solids',
    'Chloramines',
    'Sulfate',
    'Conductivity',
    'Organic_carbon',
    'Trihalomethanes',
    'Turbidity'
]

# Rentang nilai valid untuk validasi input (berdasarkan standar WHO & data)
FEATURE_RANGES = {
    'ph': {
        'min': 0.0, 'max': 14.0,
        'label': 'pH',
        'unit': '',
        'safe_min': 6.5, 'safe_max': 8.5,
        'description': 'Tingkat keasaman/kebasaan air',
        'placeholder': '7.0',
        'step': '0.01'
    },
    'Hardness': {
        'min': 0.0, 'max': 400.0,
        'label': 'Hardness',
        'unit': 'mg/L',
        'safe_min': 60.0, 'safe_max': 300.0,
        'description': 'Konsentrasi kalsium dan magnesium terlarut',
        'placeholder': '196.37',
        'step': '0.01'
    },
    'Solids': {
        'min': 0.0, 'max': 60000.0,
        'label': 'Solids (TDS)',
        'unit': 'mg/L',
        'safe_min': 500.0, 'safe_max': 50000.0,
        'description': 'Total Dissolved Solids (padatan terlarut)',
        'placeholder': '22014.09',
        'step': '0.01'
    },
    'Chloramines': {
        'min': 0.0, 'max': 14.0,
        'label': 'Chloramines',
        'unit': 'ppm',
        'safe_min': 0.0, 'safe_max': 4.0,
        'description': 'Konsentrasi kloramin sebagai disinfektan',
        'placeholder': '7.12',
        'step': '0.01'
    },
    'Sulfate': {
        'min': 0.0, 'max': 600.0,
        'label': 'Sulfate',
        'unit': 'mg/L',
        'safe_min': 0.0, 'safe_max': 250.0,
        'description': 'Jumlah sulfat dalam air',
        'placeholder': '333.77',
        'step': '0.01'
    },
    'Conductivity': {
        'min': 0.0, 'max': 800.0,
        'label': 'Conductivity',
        'unit': 'μS/cm',
        'safe_min': 200.0, 'safe_max': 400.0,
        'description': 'Kemampuan air menghantarkan listrik',
        'placeholder': '421.08',
        'step': '0.01'
    },
    'Organic_carbon': {
        'min': 0.0, 'max': 30.0,
        'label': 'Organic Carbon',
        'unit': 'ppm',
        'safe_min': 0.0, 'safe_max': 10.0,
        'description': 'Total Organic Carbon (kandungan karbon organik)',
        'placeholder': '14.28',
        'step': '0.01'
    },
    'Trihalomethanes': {
        'min': 0.0, 'max': 130.0,
        'label': 'Trihalomethanes',
        'unit': 'μg/L',
        'safe_min': 0.0, 'safe_max': 80.0,
        'description': 'Senyawa THM hasil klorinasi air',
        'placeholder': '66.40',
        'step': '0.01'
    },
    'Turbidity': {
        'min': 0.0, 'max': 8.0,
        'label': 'Turbidity',
        'unit': 'NTU',
        'safe_min': 0.0, 'safe_max': 4.0,
        'description': 'Tingkat kekeruhan / kejernihan air',
        'placeholder': '3.97',
        'step': '0.001'
    }
}

# ==============================================================================
# KONFIGURASI LABEL PREDIKSI
# ==============================================================================
PREDICTION_LABELS = {
    0: {
        'label': 'Tidak Layak Minum',
        'label_en': 'Not Potable',
        'color': 'danger',
        'icon': 'bi-x-circle-fill',
        'emoji': 'X',
        'badge_class': 'badge-danger'
    },
    1: {
        'label': 'Layak Minum',
        'label_en': 'Potable',
        'color': 'success',
        'icon': 'bi-check-circle-fill',
        'emoji': 'OK',
        'badge_class': 'badge-success'
    }
}

# ==============================================================================
# REKOMENDASI TINDAKAN BERDASARKAN HASIL PREDIKSI
# ==============================================================================
RECOMMENDATIONS = {
    1: {  # Layak Minum
        'title': 'Air Aman untuk Dikonsumsi',
        'summary': 'Berdasarkan analisis parameter kualitas air, sampel ini memenuhi standar kelayakan konsumsi.',
        'actions': [
            'Pertahankan kondisi pengolahan air yang sudah baik',
            'Lakukan monitoring rutin setiap 3-6 bulan sekali',
            'Pastikan sistem distribusi air tetap bersih dan tertutup',
            'Simpan air dalam wadah bersih dan tertutup rapat'
        ],
        'color': 'success',
        'alert_class': 'alert-success'
    },
    0: {  # Tidak Layak
        'title': 'Air Tidak Aman untuk Dikonsumsi',
        'summary': 'Sampel air ini tidak memenuhi standar kelayakan. Diperlukan tindakan segera sebelum dikonsumsi.',
        'actions': [
            'JANGAN dikonsumsi langsung sebelum diolah lebih lanjut',
            'Lakukan filtrasi menggunakan filter membran atau activated carbon',
            'Pertimbangkan penggunaan sistem reverse osmosis (RO)',
            'Didihkan air hingga 100°C selama minimal 1 menit jika tidak ada filter',
            'Segera hubungi PDAM atau Dinas Kesehatan setempat untuk pemeriksaan lebih lanjut',
            'Gunakan air minum kemasan sebagai alternatif sementara'
        ],
        'color': 'danger',
        'alert_class': 'alert-danger'
    }
}
