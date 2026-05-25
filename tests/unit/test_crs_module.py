import pytest
import pandas as pd
from src.audit_engine.modules.crs_module import CreditRiskConsistencyModule

@pytest.fixture
def synthetic_credit_dataset():
    """
    Menghasilkan data risiko kredit tiruan.
    - ACC_01: Valid (open_acc <= total_acc, delinq selaras, revol_bal positif).
    - ACC_02: Gagal CRS-01 (open_acc 15 > total_acc 10 -> Kemustahilan struktural biro).
    - ACC_03: Gagal CRS-02 (delinq_2yrs tercatat 0, tapi mths_since_last_delinq mencatat baru 6 bulan lalu).
    - ACC_04: Gagal CRS-12 (revol_bal bernilai minus -$450.00).
    """
    data = {
        'open_acc':               [5,   15,  8,   6],
        'total_acc':              [12,  10,  20,  10],
        'delinq_2yrs':            [0,   1,   0,   0],
        'mths_since_last_delinq': [999, 14,  6,   999], # 999 adalah representasi NULL dari Null Classifier kita
        'revol_bal':              [5000.0, 12000.0, 3400.0, -450.0]
    }
    return pd.DataFrame(data, index=['ACC_01', 'ACC_02', 'ACC_03', 'ACC_04'])

def test_credit_risk_consistency_assertions(synthetic_credit_dataset):
    module = CreditRiskConsistencyModule()
    results = module.execute(synthetic_credit_dataset)

    # --- Verifikasi CRS-01 (Batas Akun Aktif) ---
    assert results['CRS-01']['status'] == 'GAGAL'
    assert results['CRS-01']['failure_count'] == 1
    assert 'ACC_02' in results['CRS-01']['sample_failing_ids']

    # --- Verifikasi CRS-02 (Inkonsistensi Histori Tunggakan) ---
    assert results['CRS-02']['status'] == 'GAGAL'
    assert results['CRS-02']['failure_count'] == 1
    assert 'ACC_03' in results['CRS-02']['sample_failing_ids']

    # --- Verifikasi CRS-12 (Saldo Revolving Negatif) ---
    assert results['CRS-12']['status'] == 'GAGAL'
    assert results['CRS-12']['failure_count'] == 1
    assert 'ACC_04' in results['CRS-12']['sample_failing_ids']

    # Pastikan data ACC_01 yang valid tidak masuk perangkap fraud
    for check_id in ['CRS-01', 'CRS-02', 'CRS-12']:
        assert 'ACC_01' not in results[check_id]['sample_failing_ids']