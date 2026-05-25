import pytest
import pandas as pd
import numpy as np
from src.ml_layer.feature_engineering import AuditFeatureEngineer
from src.ml_layer.isolation_forest import AuditAnomalyDetector

@pytest.fixture
def synthetic_audit_population():
    """
    Menghasilkan populasi data tiruan kecil (50 baris).
    49 baris berupa profil normal (pendapatan menengah, pinjaman proporsional).
    1 baris (INDEX_ANOMALI) dirancang khusus sebagai 'Siluman Multidimensi':
    Secara parsial lulus RBAE (funded_amnt == loan_amnt, dll), namun memiliki 
    kombinasi dti raksasa, pendapatan super ekstrem tak terverifikasi, dan akun terbuka padat.
    """
    np.random.seed(42)
    n_records = 50
    
    data = {
        'loan_amnt':   np.random.normal(15000, 3000, n_records),
        'funded_amnt': np.random.normal(15000, 3000, n_records),
        'int_rate':    np.random.normal(12.0, 2.0, n_records),
        'installment': np.random.normal(350, 50, n_records),
        'annual_inc':  np.random.normal(65000, 10000, n_records),
        'dti':         np.random.normal(15.0, 3.0, n_records),
        'delinq_2yrs': np.zeros(n_records),
        'inq_last_6mths': np.random.randint(0, 3, n_records),
        'open_acc':    np.random.randint(5, 12, n_records),
        'pub_rec':     np.zeros(n_records),
        'revol_bal':   np.random.normal(10000, 2000, n_records),
        'revol_util':  np.random.normal(45.0, 10, n_records),
        'total_acc':   np.random.randint(15, 30, n_records),
        'total_pymnt': np.random.normal(5000, 1000, n_records),
        'out_prncp':   np.random.normal(10000, 2000, n_records),
        'grade':       ['B'] * n_records,
        'has_delinquency_history': [0] * n_records,
        'has_public_record': [0] * n_records
    }
    
    df = pd.DataFrame(data)
    
    # Suntikkan 1 data pencilan siluman pada indeks terakhir (Baris ke-49)
    df.loc[49, 'annual_inc'] = 4500000.0   # Pendapatan melompat drastis (outlier masif)
    df.loc[49, 'dti'] = 98.5               # Rasio beban utang hampir habis melampaui rata-rata
    df.loc[49, 'open_acc'] = 45            # Jumlah akun aktif terbuka berantakan secara masif
    df.loc[49, 'revol_bal'] = 890000.0     # Saldo revolving luar biasa besar
    
    return df

def test_ai_layer_isolates_multidimensional_anomaly(synthetic_audit_population):
    # 1. Jalankan komponen rekayasa fitur & RobustScaler
    engineer = AuditFeatureEngineer()
    X = engineer.fit_transform(synthetic_audit_population)
    
    assert X.shape == (50, 18), f"Ekspektasi dimensi matriks (50, 18), namun terbentuk {X.shape}"

    # 2. Jalankan deteksi model Isolation Forest (set contamination ke 0.02 agar fokus pada top 1 anomali)
    detector = AuditAnomalyDetector(contamination=0.02)
    flags, scores = detector.fit_predict(X)

    # 3. Verifikasi bendera deteksi
    # Baris ke-49 harus sukses terisolasi sebagai anomali (-1) oleh AI
    assert flags[49] == -1, "Model AI gagal mengisolasi data siluman multidimensi pada indeks 49"
    
    # Skor untuk data pencilan harus bernilai jauh lebih kecil (lebih negatif) dibanding skor data normal rata-rata
    assert scores[49] < np.mean(scores), "Skor anomali data pencilan tidak merepresentasikan tingkat kerawanan dimensi"