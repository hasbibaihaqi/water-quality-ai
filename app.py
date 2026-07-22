# -*- coding: utf-8 -*-
"""
app.py - Flask Application untuk Water Quality AI
Aplikasi prediksi kelayakan air minum berbasis web.

Routes:
    GET  /           -> Halaman utama (index)
    GET  /predict    -> Halaman form prediksi
    POST /predict    -> Proses prediksi dan tampilkan hasil
    GET  /about      -> Halaman tentang aplikasi & model
    GET  /api/info   -> API endpoint informasi model (JSON)
"""

from flask import (
    Flask, render_template, request,
    redirect, url_for, jsonify, flash, session
)
import os
import sys

from config import SECRET_KEY, DEBUG
from services.hybrid_engine import get_hybrid_system
from utils.preprocessing import FEATURE_NAMES, FEATURE_RANGES, validate_and_parse_input

# ==============================================================================
# INISIALISASI FLASK APP
# ==============================================================================
app = Flask(__name__)
app.secret_key = SECRET_KEY

# ==============================================================================
# ROUTE: HALAMAN UTAMA
# ==============================================================================
@app.route('/')
def index():
    """
    Halaman landing page.
    Menampilkan hero section, statistik, dan fitur aplikasi.
    """
    hybrid = get_hybrid_system()
    model_info = hybrid.get_model_info()

    # Data statistik untuk hero section
    stats = {
        'dataset_size': model_info.get('dataset_size', 3276),
        'feature_count': model_info.get('features', FEATURE_NAMES).__len__(),
        'model_name': model_info.get('model_name', 'Random Forest'),
        'accuracy': model_info.get('evaluation', {}).get('test_accuracy', 0),
        'f1_score': model_info.get('evaluation', {}).get('f1_score', 0),
        'roc_auc': model_info.get('evaluation', {}).get('roc_auc', 0),
    }

    return render_template('index.html', stats=stats, model_info=model_info)


# ==============================================================================
# ROUTE: HALAMAN PREDIKSI
# ==============================================================================
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """
    GET  -> Tampilkan form input parameter kualitas air
    POST -> Proses input, validasi, prediksi, tampilkan hasil
    """
    hybrid = get_hybrid_system()

    # Cek apakah model siap
    if not hybrid.ml_predictor.is_ready:
        flash(
            'Model belum tersedia. Jalankan notebooks/training.py terlebih dahulu.',
            'danger'
        )
        return redirect(url_for('index'))

    if request.method == 'GET':
        # Tampilkan form kosong dengan konfigurasi fitur
        return render_template(
            'predict.html',
            features=FEATURE_RANGES,
            feature_names=FEATURE_NAMES,
            form_data={},
            model_info=hybrid.get_model_info()
        )

    # ---- POST: Proses Prediksi ----
    # Step 1: Ambil dan validasi input
    form_data = request.form.to_dict()
    values_dict, errors = validate_and_parse_input(form_data)

    if errors:
        # Kembalikan form dengan pesan error dan nilai yang sudah diinput
        return render_template(
            'predict.html',
            features=FEATURE_RANGES,
            feature_names=FEATURE_NAMES,
            form_data=form_data,
            errors=errors,
            model_info=hybrid.get_model_info()
        )

    # Step 2: Lakukan prediksi (Hybrid AI)
    try:
        result = hybrid.process(values_dict)
        return render_template('result.html', result=result)
    except RuntimeError as e:
        flash(str(e), 'danger')
        return redirect(url_for('predict'))
    except Exception as e:
        flash(f'Terjadi kesalahan saat prediksi: {str(e)}', 'danger')
        return redirect(url_for('predict'))

    return render_template('result.html', result=result)


# ==============================================================================
# ROUTE: HALAMAN TENTANG
# ==============================================================================
@app.route('/about')
def about():
    """
    Halaman informasi tentang aplikasi, dataset, algoritma, dan evaluasi model.
    """
    hybrid = get_hybrid_system()
    model_info = hybrid.get_model_info()
    return render_template('about.html', model_info=model_info)


# ==============================================================================
# ROUTE: API ENDPOINT (JSON)
# ==============================================================================
@app.route('/api/info')
def api_info():
    """
    API endpoint untuk mendapatkan informasi model dalam format JSON.
    Berguna untuk debugging dan integrasi eksternal.
    """
    hybrid = get_hybrid_system()
    model_info = hybrid.get_model_info()
    return jsonify({
        'status': 'ready' if hybrid.ml_predictor.is_ready else 'not_ready',
        'model_info': model_info
    })


@app.route('/api/predict', methods=['POST'])
def api_predict():
    """
    API endpoint untuk prediksi via JSON (untuk integrasi program lain).

    Request body (JSON):
        {
            "ph": 7.0,
            "Hardness": 200.0,
            "Solids": 20000.0,
            "Chloramines": 7.0,
            "Sulfate": 350.0,
            "Conductivity": 400.0,
            "Organic_carbon": 14.0,
            "Trihalomethanes": 70.0,
            "Turbidity": 4.0
        }

    Response (JSON):
        {
            "prediction": 1,
            "label": "Layak Minum",
            "probability_safe": 78.5,
            "probability_unsafe": 21.5,
            "confidence": 78.5
        }
    """
    hybrid = get_hybrid_system()

    if not hybrid.ml_predictor.is_ready:
        return jsonify({'error': 'Model tidak tersedia'}), 503

    if not request.is_json:
        return jsonify({'error': 'Content-Type harus application/json'}), 400

    data = request.get_json()

    # Validasi input JSON
    values_dict, errors = validate_and_parse_input(data)
    if errors:
        return jsonify({'error': 'Validasi gagal', 'details': errors}), 422

    try:
        result = hybrid.process(values_dict)
        return jsonify({
            'prediction': result['final_status']['code'],
            'label': result['final_status']['text'],
            'probability_safe': result['ml_prob_safe'],
            'probability_unsafe': result['ml_prob_unsafe'],
            'confidence': result['confidence']['value'],
            'abnormal_count': result['who_validation']['out_of_bounds_count'],
            'abnormal_params': [p['name'] for p in result['who_validation']['problematic_params']]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==============================================================================
# ERROR HANDLERS
# ==============================================================================
@app.errorhandler(404)
def page_not_found(e):
    """Handler untuk halaman 404."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Handler untuk error 500."""
    return render_template('500.html'), 500


# ==============================================================================
# TEMPLATE FILTERS (JINJA2)
# ==============================================================================
@app.template_filter('percentage')
def percentage_filter(value):
    """Filter Jinja2 untuk format persen."""
    return f"{float(value):.1f}%"


@app.template_filter('round2')
def round2_filter(value):
    """Filter Jinja2 untuk 2 desimal."""
    return f"{float(value):.2f}"


@app.template_filter('round4')
def round4_filter(value):
    """Filter Jinja2 untuk 4 desimal."""
    return f"{float(value):.4f}"


# ==============================================================================
# MAIN
# ==============================================================================
if __name__ == '__main__':
    print("=" * 60)
    print("  Water Quality AI - Flask App")
    print("  http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=DEBUG, host='0.0.0.0', port=5000)
