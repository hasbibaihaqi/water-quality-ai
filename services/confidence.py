# services/confidence.py

class ConfidenceAnalyzer:
    @staticmethod
    def analyze(normalized_prob_safe, prediction):
        confidence_value = normalized_prob_safe if prediction == 1 else (100.0 - normalized_prob_safe)
        
        if confidence_value >= 80:
            level = "High Confidence"
            color = "var(--success)"
            badge_class = "bg-success"
        elif confidence_value >= 65:
            level = "Medium Confidence"
            color = "var(--warning)"
            badge_class = "bg-warning text-dark"
        else:
            level = "Low Confidence"
            color = "var(--danger)"
            badge_class = "bg-danger"
            
        return {
            'value': round(confidence_value, 2),
            'level': level,
            'color': color,
            'badge_class': badge_class
        }
