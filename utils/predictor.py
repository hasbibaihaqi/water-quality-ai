# -*- coding: utf-8 -*-
"""
utils/predictor.py
Modul inti untuk melakukan prediksi kelayakan air minum.
Mengelola loading model, scaling input, dan menghasilkan output prediksi.
"""

import os
import json
import joblib
import numpy as np

from config import (
    MODEL_PATH, SCALER_PATH, METADATA_PATH,
    PREDICTION_LABELS, RECOMMENDATIONS
)
from utils.preprocessing import prepare_input_array, get_parameter_status


class WaterQualityPredictor:
    """
    Kelas utama untuk prediksi kelayakan air minum.

    Attributes:
        model: Model ML yang sudah dilatih (loaded dari .pkl)
        scaler: StandardScaler yang sudah di-fit (loaded dari .pkl)
        metadata: Metadata training model (dari JSON)
        is_ready (bool): Status apakah model siap digunakan
    """

    def __init__(self):
        """Inisialisasi predictor dan load model dari disk."""
        self.model = None
        self.scaler = None
        self.metadata = None
        self.is_ready = False
        self._load_model()

    def _load_model(self):
        """
        Load model, scaler, dan metadata dari file.
        Dipanggil saat inisialisasi kelas.
        """
        try:
            # Load model yang sudah dilatih
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(
                    f"Model tidak ditemukan: {MODEL_PATH}\n"
                    "Jalankan notebooks/training.py terlebih dahulu."
                )
            self.model = joblib.load(MODEL_PATH)

            # Load scaler yang sudah di-fit pada data training
            if not os.path.exists(SCALER_PATH):
                raise FileNotFoundError(
                    f"Scaler tidak ditemukan: {SCALER_PATH}\n"
                    "Jalankan notebooks/training.py terlebih dahulu."
                )
            self.scaler = joblib.load(SCALER_PATH)

            # Load metadata training (opsional, tidak fatal jika tidak ada)
            if os.path.exists(METADATA_PATH):
                with open(METADATA_PATH, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {}

            self.is_ready = True
            print("[Predictor] Model berhasil dimuat.")
            if self.metadata:
                print(f"[Predictor] Model: {self.metadata.get('model_name', 'Unknown')}")
                eval_data = self.metadata.get('evaluation', {})
                print(f"[Predictor] F1 Score: {eval_data.get('f1_score', 'N/A')}")

        except FileNotFoundError as e:
            print(f"[Predictor] ERROR: {e}")
            self.is_ready = False
        except Exception as e:
            print(f"[Predictor] ERROR saat load model: {str(e)}")
            self.is_ready = False

    def predict(self, values_dict):
        """
        Melakukan prediksi kelayakan air dari input pengguna.

        Pipeline prediksi:
        1. Konversi dict ke numpy array (urutan fitur sesuai training)
        2. Normalisasi menggunakan StandardScaler yang sama dengan training
        3. Prediksi kelas (0/1) dan probabilitas
        4. Generate hasil lengkap dengan rekomendasi

        Parameters:
            values_dict (dict): {feature_name: float_value} dari preprocessing

        Returns:
            dict: Hasil prediksi lengkap berisi:
                - prediction (int): 0 atau 1
                - label (str): "Layak Minum" / "Tidak Layak Minum"
                - probability_safe (float): Probabilitas layak (0-100%)
                - probability_unsafe (float): Probabilitas tidak layak (0-100%)
                - confidence (float): Tingkat keyakinan model (0-100%)
                - parameter_status (list): Status tiap parameter vs standar WHO
                - recommendation (dict): Rekomendasi tindakan
                - label_config (dict): Konfigurasi label (warna, icon, dll)

        Raises:
            RuntimeError: Jika model belum siap / tidak berhasil dimuat
        """
        if not self.is_ready:
            raise RuntimeError(
                "Model belum siap. Pastikan training.py sudah dijalankan "
                "dan file model.pkl serta scaler.pkl tersedia di folder models/."
            )

        # Step 1: Buat array numpy dari input
        input_array = prepare_input_array(values_dict)

        # Step 2: Scaling menggunakan scaler yang sama dengan training
        # PENTING: Hanya transform (bukan fit_transform) karena scaler sudah di-fit
        input_scaled = self.scaler.transform(input_array)

        # PERBAIKAN BUG: Capping nilai scaled ke rentang [-3.0, 3.0] 
        # Mencegah Vanishing Kernel SVM akibat input outlier yang sangat ekstrem
        input_scaled = np.clip(input_scaled, -3.0, 3.0)

        # Step 3: Prediksi probabilitas
        # predict_proba mengembalikan [P(class=0), P(class=1)]
        probabilities = self.model.predict_proba(input_scaled)[0]
        prob_unsafe = float(probabilities[0])  # P(Tidak Layak)
        prob_safe = float(probabilities[1])    # P(Layak)

        # Step 4: Prediksi kelas menggunakan threshold optimal
        threshold = self.metadata.get('optimal_threshold', 0.5) if self.metadata else 0.5
        prediction = 1 if prob_safe >= threshold else 0

        # Normalisasi probabilitas agar intuitif di UI (Kelas yang diprediksi selalu > 50%)
        if prob_safe >= threshold:
            # Jika Layak, petakan prob_safe dari [threshold, 1.0] ke [0.5, 1.0]
            normalized_prob_safe = 0.5 + 0.5 * ((prob_safe - threshold) / (1.0 - threshold))
        else:
            # Jika Tidak Layak, petakan prob_safe dari [0.0, threshold] ke [0.0, 0.499]
            normalized_prob_safe = 0.5 * (prob_safe / threshold)
            
        normalized_prob_unsafe = 1.0 - normalized_prob_safe

        # Tingkat keyakinan = probabilitas kelas yang diprediksi (dari probabilitas yang sudah dinormalisasi)
        confidence = normalized_prob_safe if prediction == 1 else normalized_prob_unsafe

        # Step 5: Analisis status parameter vs standar WHO
        parameter_status = get_parameter_status(values_dict)
        abnormal_params = [p for p in parameter_status if p['status'] != 'normal']
        abnormal_count = len(abnormal_params)

        # =====================================================================
        # HYBRID AI LOGIC: ML + WHO RULE-BASED
        # =====================================================================
        hybrid_status = "normal"  # "normal", "warning", "override"
        hybrid_message = ""

        if prediction == 1:
            if abnormal_count > 3:
                prediction = 0
                hybrid_status = "override"
                hybrid_message = f"Sistem pakar menolak hasil prediksi awal karena {abnormal_count} parameter kritis berada di luar batas standar aman WHO."
            elif abnormal_count >= 1:
                hybrid_status = "warning"
                hybrid_message = "Model memprediksi air layak diminum berdasarkan pola, namun beberapa parameter berada di luar batas aman WHO. Sangat disarankan melakukan pengujian laboratorium tambahan."

        # Update probabilitas secara statis jika di-override agar UI tidak bingung
        if hybrid_status == "override":
            normalized_prob_safe = 0.0
            normalized_prob_unsafe = 1.0
            confidence = 1.0

        # Step 6: Ambil konfigurasi label dan rekomendasi
        label_config = PREDICTION_LABELS[prediction]
        recommendation = RECOMMENDATIONS[prediction]

        return {
            'prediction': prediction,
            'label': label_config['label'],
            'label_en': label_config['label_en'],
            'color': label_config['color'],
            'icon': label_config['icon'],
            'probability_safe': round(normalized_prob_safe * 100, 2),
            'probability_unsafe': round(normalized_prob_unsafe * 100, 2),
            'confidence': round(confidence * 100, 2),
            'parameter_status': parameter_status,
            'recommendation': recommendation,
            'label_config': label_config,
            'abnormal_count': len(abnormal_params),
            'abnormal_params': [p['label'] for p in abnormal_params],
            'input_values': values_dict,
            'hybrid_status': hybrid_status,
            'hybrid_message': hybrid_message
        }

    def get_model_info(self):
        """
        Mengembalikan informasi tentang model yang sedang digunakan.

        Returns:
            dict: Informasi model (nama, metrik evaluasi, dll)
        """
        if not self.metadata:
            return {
                'model_name': 'Unknown',
                'is_ready': self.is_ready,
                'evaluation': {}
            }

        return {
            'model_name': self.metadata.get('model_name', 'Unknown'),
            'is_ready': self.is_ready,
            'used_tuning': self.metadata.get('used_tuning', False),
            'features': self.metadata.get('features', []),
            'dataset_size': self.metadata.get('dataset_size', 0),
            'train_size': self.metadata.get('train_size', 0),
            'test_size': self.metadata.get('test_size', 0),
            'train_size_after_smote': self.metadata.get('train_size_after_smote', 0),
            'class_distribution': self.metadata.get('class_distribution_original', {}),
            'evaluation': self.metadata.get('evaluation', {}),
            'preprocessing': self.metadata.get('preprocessing', {}),
            'all_models_comparison': self.metadata.get('all_models_comparison', []),
            'training_date': self.metadata.get('training_date', 'N/A')
        }


# Singleton predictor instance - dibuat sekali saat aplikasi start
# Ini menghindari load model berulang kali di setiap request
predictor_instance = None


def get_predictor():
    """
    Mengembalikan singleton instance dari WaterQualityPredictor.
    Model hanya di-load satu kali saat aplikasi pertama kali diakses.

    Returns:
        WaterQualityPredictor: Instance predictor yang siap digunakan
    """
    global predictor_instance
    if predictor_instance is None:
        predictor_instance = WaterQualityPredictor()
    return predictor_instance