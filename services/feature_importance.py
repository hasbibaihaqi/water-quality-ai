# services/feature_importance.py
import json
from config import METADATA_PATH

class FeatureImportanceAnalyzer:
    def __init__(self):
        try:
            with open(METADATA_PATH, 'r') as f:
                self.metadata = json.load(f)
        except Exception:
            self.metadata = {}

    def get_top_features(self, limit=5):
        importances = self.metadata.get('feature_importances', {})
        if not importances:
            return []
        
        # Sort by value descending
        sorted_features = sorted(importances.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate percentage
        total = sum(val for key, val in sorted_features)
        
        result = []
        for key, val in sorted_features[:limit]:
            result.append({
                'name': key,
                'percentage': round((val / total) * 100, 1)
            })
        return result
