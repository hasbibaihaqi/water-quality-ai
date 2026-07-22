# services/recommendation.py

class RecommendationEngine:
    @staticmethod
    def get_recommendation(risk_level):
        if risk_level == 'Rendah':
            return [
                "Air dapat dikonsumsi dengan aman.",
                "Tetap lakukan pemeriksaan kebersihan wadah secara berkala.",
                "Pastikan sumber air terlindungi dari kontaminasi eksternal."
            ]
        elif risk_level == 'Sedang':
            return [
                "Sebaiknya dilakukan proses filtrasi (penyaringan) tambahan.",
                "Sangat disarankan untuk merebus air sebelum dikonsumsi.",
                "Hindari konsumsi langsung dari sumber tanpa pengolahan."
            ]
        else:
            return [
                "JANGAN dikonsumsi secara langsung.",
                "Lakukan proses pengolahan air tingkat lanjut (Reverse Osmosis / Distilasi).",
                "Segera hubungi pihak berwenang atau laboratorium untuk uji sampel menyeluruh."
            ]
