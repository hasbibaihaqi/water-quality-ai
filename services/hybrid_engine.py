# services/hybrid_engine.py
from services.ml_predictor import MLPredictor
from services.who_validator import WHOValidator
from services.confidence import ConfidenceAnalyzer
from services.feature_importance import FeatureImportanceAnalyzer
from services.risk_analyzer import RiskAnalyzer
from services.recommendation import RecommendationEngine
from utils.preprocessing import prepare_input_array

class HybridWaterQualitySystem:
    def __init__(self):
        self.ml_predictor = MLPredictor()
        self.feature_analyzer = FeatureImportanceAnalyzer()

    def process(self, values_dict):
        # 1. WHO Validation
        who_result = WHOValidator.validate(values_dict)
        
        # 2. ML Prediction
        input_array = prepare_input_array(values_dict)
        ml_result = self.ml_predictor.predict(input_array)
        
        # 3. Confidence Analysis
        confidence_result = ConfidenceAnalyzer.analyze(ml_result['norm_prob_safe'], ml_result['prediction'])
        
        # 4. Feature Importance
        top_features = self.feature_analyzer.get_top_features(limit=4)
        
        # 5. Hybrid Logic Engine (Final Status)
        ml_is_safe = ml_result['prediction'] == 1
        critical_violations = who_result['critical_out_of_bounds']
        total_violations = who_result['out_of_bounds_count']
        
        final_status_code = 0
        final_status_text = ""
        final_status_color = ""
        final_status_desc = ""
        
        if ml_is_safe:
            if total_violations == 0:
                final_status_code = 1
                final_status_text = "Layak Minum"
                final_status_color = "success"
                final_status_desc = "Kualitas air terpantau sangat baik dan memenuhi standar."
            elif critical_violations <= 3:
                final_status_code = 2
                final_status_text = "Layak dengan Peringatan"
                final_status_color = "warning"
                final_status_desc = "Model ML memprediksi air layak diminum. Namun terdapat beberapa parameter yang berada di luar batas aman WHO. Disarankan pengolahan."
            else:
                final_status_code = 3
                final_status_text = "Tidak Direkomendasikan"
                final_status_color = "danger"
                final_status_desc = "Walaupun model ML memprediksi layak, terdapat >3 parameter kritis yang melanggar standar WHO secara signifikan."
        else:
            final_status_code = 4
            final_status_text = "Tidak Layak Minum"
            final_status_color = "danger"
            final_status_desc = "Pola kimia air sangat beracun atau tidak layak konsumsi."
            
        # 6. Risk Analysis & Recommendations
        risk_result = RiskAnalyzer.analyze(final_status_code)
        recommendations = RecommendationEngine.get_recommendation(risk_result['level'])
        
        return {
            'input_values': values_dict,
            'ml_prediction_text': "Layak Minum" if ml_is_safe else "Tidak Layak",
            'ml_is_safe': ml_is_safe,
            'ml_prob_safe': round(ml_result['norm_prob_safe'], 2),
            'ml_prob_unsafe': round(ml_result['norm_prob_unsafe'], 2),
            'confidence': confidence_result,
            'who_validation': who_result,
            'final_status': {
                'code': final_status_code,
                'text': final_status_text,
                'color': final_status_color,
                'desc': final_status_desc
            },
            'risk': risk_result,
            'recommendations': recommendations,
            'feature_importance': top_features
        }

    def get_model_info(self):
        return self.ml_predictor.metadata

# Singleton
_hybrid_instance = None
def get_hybrid_system():
    global _hybrid_instance
    if _hybrid_instance is None:
        _hybrid_instance = HybridWaterQualitySystem()
    return _hybrid_instance
