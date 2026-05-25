import pytest
import pandas as pd
from src.ml_layer.xai_explainer import AuditXAIExplainer

@pytest.fixture
def sample_audit_history():
    """Menghasilkan baseline populasi untuk perhitungan median kelompok."""
    data = {
        'grade':      ['A', 'A', 'A', 'B', 'B'],
        'term':       [' 36 months', ' 36 months', ' 36 months', ' 36 months', ' 36 months'],
        'annual_inc': [50000.0, 60000.0, 55000.0, 80000.0, 90000.0], # Median Grade A = 55,000
        'loan_amnt':  [10000.0, 12000.0, 11000.0, 15000.0, 16000.0]  # Median Grade A = 11,000
    }
    return pd.DataFrame(data)

def test_xai_explainer_calculates_correct_drivers(sample_audit_history):
    features = ['annual_inc', 'loan_amnt']
    explainer = AuditXAIExplainer(feature_cols=features)
    explainer.fit_baseline(sample_audit_history)
    
    # Simulasikan satu kasus pencilan (Grade A) dengan lonjakan pendapatan raksasa
    anomaly_record = pd.Series({
        'grade': 'A',
        'term': ' 36 months',
        'annual_inc': 550000.0,  # 10x lipat dari median asli ($55,000) -> Deviasi +900%
        'loan_amnt': 11000.0     # Tepat di angka median ($11,000) -> Deviasi 0%
    })
    
    explanation = explainer.explain_record(anomaly_record)
    
    # --- ASSERTIONS ---
    assert explanation['method'] == "segment_median_deviation"
    assert explanation['segment_context']['grade'] == 'A'
    
    # annual_inc harus menjadi pendorong nomor satu karena deviasinya yang masif
    assert explanation['top_3_anomaly_drivers'][0] == 'annual_inc'
    assert explanation['deviation_profile']['annual_inc']['pct_deviation'] == 900.0
    assert explanation['deviation_profile']['loan_amnt']['pct_deviation'] == 0.0