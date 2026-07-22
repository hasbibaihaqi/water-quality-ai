# services/who_validator.py
from config import FEATURE_RANGES

CRITICAL_PARAMS = ['ph', 'Chloramines', 'Sulfate', 'Organic_carbon', 'Trihalomethanes', 'Turbidity']

class WHOValidator:
    @staticmethod
    def validate(values_dict):
        status_list = []
        safe_count = 0
        out_of_bounds_count = 0
        critical_out_of_bounds = 0
        problematic_params = []

        for param, value in values_dict.items():
            config = FEATURE_RANGES.get(param)
            if not config:
                continue

            min_val = config['safe_min']
            max_val = config['safe_max']
            
            is_safe = min_val <= value <= max_val
            is_critical = param in CRITICAL_PARAMS

            if is_safe:
                safe_count += 1
                status = 'normal'
            else:
                out_of_bounds_count += 1
                problematic_params.append({
                    'name': config['label'],
                    'value': value,
                    'unit': config['unit'],
                    'reason': 'Terlalu Rendah' if value < min_val else 'Terlalu Tinggi',
                    'is_critical': is_critical
                })
                if is_critical:
                    critical_out_of_bounds += 1
                status = 'low' if value < min_val else 'high'
            
            status_list.append({
                'id': param,
                'label': config['label'],
                'value': value,
                'status': status,
                'is_critical': is_critical,
                'reason': 'Aman' if status == 'normal' else ('Rendah' if status == 'low' else 'Tinggi'),
                'safe_min': min_val,
                'safe_max': max_val,
                'unit': config['unit']
            })

        return {
            'status_list': status_list,
            'safe_count': safe_count,
            'out_of_bounds_count': out_of_bounds_count,
            'critical_out_of_bounds': critical_out_of_bounds,
            'problematic_params': problematic_params
        }
