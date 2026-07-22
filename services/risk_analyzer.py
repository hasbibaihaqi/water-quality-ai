# services/risk_analyzer.py

class RiskAnalyzer:
    @staticmethod
    def analyze(final_status_code):
        # 1: Layak (Aman), 2: Peringatan, 3: Tidak Direkomendasikan, 4: Tidak Layak
        if final_status_code == 1:
            return {'level': 'Rendah', 'color': 'success', 'badge': 'bg-success', 'icon': 'bi-shield-check'}
        elif final_status_code == 2:
            return {'level': 'Sedang', 'color': 'warning', 'badge': 'bg-warning text-dark', 'icon': 'bi-exclamation-triangle'}
        else:
            return {'level': 'Tinggi', 'color': 'danger', 'badge': 'bg-danger', 'icon': 'bi-shield-x'}
