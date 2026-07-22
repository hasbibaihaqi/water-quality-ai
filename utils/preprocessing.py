# -*- coding: utf-8 -*-
"""
utils/preprocessing.py
Modul untuk preprocessing input pengguna sebelum prediksi.
Bertanggung jawab untuk validasi, konversi, dan penanganan nilai input.
"""

import numpy as np
from config import FEATURE_NAMES, FEATURE_RANGES


def validate_and_parse_input(form_data):
    """
    Validasi dan parsing input dari form HTML.

    Proses:
    1. Memeriksa apakah semua field ada
    2. Mengkonversi string ke float
    3. Validasi rentang nilai tiap fitur

    Parameters:
        form_data (dict): Data dari request.form Flask

    Returns:
        tuple: (values_dict, errors_list)
            - values_dict: dict berisi nilai float yang valid, atau None jika ada error
            - errors_list: list pesan error, kosong jika tidak ada error
    """
    errors = []
    parsed_values = {}

    for feature in FEATURE_NAMES:
        raw_value = form_data.get(feature, '').strip()

        # Cek apakah field kosong
        if raw_value == '' or raw_value is None:
            label = FEATURE_RANGES[feature]['label']
            errors.append(f"Field '{label}' tidak boleh kosong.")
            continue

        # Konversi ke float
        try:
            value = float(raw_value)
        except ValueError:
            label = FEATURE_RANGES[feature]['label']
            errors.append(f"Nilai '{label}' harus berupa angka (desimal).")
            continue

        # Validasi rentang nilai
        f_min = FEATURE_RANGES[feature]['min']
        f_max = FEATURE_RANGES[feature]['max']
        label = FEATURE_RANGES[feature]['label']
        unit = FEATURE_RANGES[feature]['unit']

        if value < f_min or value > f_max:
            errors.append(
                f"Nilai '{label}' harus antara {f_min} dan {f_max} {unit}."
            )
            continue

        parsed_values[feature] = value

    if errors:
        return None, errors

    return parsed_values, []


def prepare_input_array(values_dict):
    """
    Mengubah dictionary nilai input menjadi numpy array 2D
    dengan urutan fitur yang benar sesuai saat training.

    Parameters:
        values_dict (dict): Dictionary {feature_name: float_value}

    Returns:
        numpy.ndarray: Array shape (1, 9) siap untuk di-scale dan diprediksi
    """
    # Susun nilai sesuai urutan FEATURE_NAMES (urutan saat training)
    ordered_values = [values_dict[feature] for feature in FEATURE_NAMES]

    # Reshape menjadi (1, n_features) untuk prediksi satu sampel
    input_array = np.array(ordered_values).reshape(1, -1)

    return input_array


def get_parameter_status(values_dict):
    """
    Menganalisis status setiap parameter berdasarkan rentang aman WHO.

    Parameters:
        values_dict (dict): Dictionary {feature_name: float_value}

    Returns:
        list: List of dict berisi info status tiap parameter
    """
    status_list = []

    for feature in FEATURE_NAMES:
        value = values_dict[feature]
        config = FEATURE_RANGES[feature]

        safe_min = config.get('safe_min', config['min'])
        safe_max = config.get('safe_max', config['max'])

        if safe_min <= value <= safe_max:
            status = 'normal'
            status_label = 'Normal'
            status_color = 'success'
            status_icon = 'bi-check-circle'
        elif value < safe_min:
            status = 'low'
            status_label = 'Terlalu Rendah'
            status_color = 'warning'
            status_icon = 'bi-arrow-down-circle'
        else:
            status = 'high'
            status_label = 'Terlalu Tinggi'
            status_color = 'danger'
            status_icon = 'bi-arrow-up-circle'

        # Hitung persentase posisi dalam skala total (untuk progress bar)
        total_range = config['max'] - config['min']
        if total_range > 0:
            percentage = min(100, max(0, (value - config['min']) / total_range * 100))
        else:
            percentage = 0

        status_list.append({
            'feature': feature,
            'label': config['label'],
            'value': round(value, 4),
            'unit': config['unit'],
            'description': config['description'],
            'status': status,
            'status_label': status_label,
            'status_color': status_color,
            'status_icon': status_icon,
            'safe_min': safe_min,
            'safe_max': safe_max,
            'percentage': round(percentage, 1)
        })

    return status_list
