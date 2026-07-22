# services/ml_predictor.py
import os
import joblib
import numpy as np
import json
from config import MODEL_PATH, SCALER_PATH, METADATA_PATH

class MLPredictor:
    def __init__(self):
        try:
            self.model = joblib.load(MODEL_PATH)
            self.scaler = joblib.load(SCALER_PATH)
            with open(METADATA_PATH, 'r') as f:
                self.metadata = json.load(f)
            self.is_ready = True
        except Exception as e:
            self.is_ready = False
            self.model = None
            self.scaler = None
            self.metadata = {}
            
    def predict(self, input_array):
        if not self.is_ready:
            raise ValueError("Model belum dilatih atau tidak ditemukan.")
            
        # Clip to avoid extreme outliers
        input_scaled = self.scaler.transform(input_array)
        input_scaled = np.clip(input_scaled, -3.0, 3.0)
        
        probabilities = self.model.predict_proba(input_scaled)[0]
        prob_unsafe = float(probabilities[0])
        prob_safe = float(probabilities[1])
        
        threshold = self.metadata.get('optimal_threshold', 0.5)
        
        # Normalize probabilities around the tuned threshold for UI display
        if prob_safe >= threshold:
            prediction = 1
            norm_safe = 0.5 + 0.5 * ((prob_safe - threshold) / (1.0 - threshold))
        else:
            prediction = 0
            norm_safe = 0.5 * (prob_safe / threshold)
            
        norm_unsafe = 1.0 - norm_safe
        
        return {
            'prediction': prediction,
            'raw_prob_safe': prob_safe,
            'raw_prob_unsafe': prob_unsafe,
            'norm_prob_safe': norm_safe * 100,
            'norm_prob_unsafe': norm_unsafe * 100,
            'threshold': threshold
        }
