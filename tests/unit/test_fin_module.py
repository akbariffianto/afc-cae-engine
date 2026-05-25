import pytest
import pandas as pd
from src.audit_engine.modules.fin_module import FinancialReconciliationModule

@pytest.fixture
def synthetic_financial_dataset():
    """
    Menghasilkan data keuangan tiruan.
    Baris 0: Lulus semua pemeriksaan.
    Baris 1: Gagal FIN-01 (funded_amnt > loan_amnt)
    Baris 2: Gagal FIN-03 (installment tidak cocok dengan perhitungan rumus PMT)
    Baris 3: Gagal FIN-10 (Status Fully Paid tapi out_prncp masih tersisa)
    """
    data = {
        'loan_amnt':   [10000.0, 5000.0, 15000.0, 10000.0],
        'funded_amnt': [10000.0, 6000.0, 15000.0, 10000.0],
        'int_rate':    [12.0,    10.0,    10.0,    12.0],
        'term':        [' 36 months', ' 36 months', ' 36 months', ' 36 months'],
        'installment': [332.14,  161.34,  900.00,  332.14], # Baris 2 dimanipulasi jadi $900 (seharusnya ~$484)
        'loan_status': ['Current', 'Current', 'Current', 'Fully Paid'],
        'out_prncp':   [5000.0,   3000.0,   12000.0,  150.0]  # Baris 3 dimanipulasi ada sisa $150
    }
    # Set index khusus sebagai representasi Primary Key / Loan ID
    return pd.DataFrame(data, index=['LOAN_01', 'LOAN_02', 'LOAN_03', 'LOAN_04'])

def test_financial_reconciliation_assertions(synthetic_financial_dataset):
    module = FinancialReconciliationModule(amnt_tolerance=1.00)
    results = module.execute(synthetic_financial_dataset)

    # --- Verifikasi FIN-01 ---
    assert results['FIN-01']['status'] == 'GAGAL'
    assert results['FIN-01']['failure_count'] == 1
    assert 'LOAN_02' in results['FIN-01']['sample_failing_ids']

    # --- Verifikasi FIN-03 ---
    assert results['FIN-03']['status'] == 'GAGAL'
    assert results['FIN-03']['failure_count'] == 1
    assert 'LOAN_03' in results['FIN-03']['sample_failing_ids']

    # --- Verifikasi FIN-10 ---
    assert results['FIN-10']['status'] == 'GAGAL'
    assert results['FIN-10']['failure_count'] == 1
    assert 'LOAN_04' in results['FIN-10']['sample_failing_ids']

    # Pastikan LOAN_01 tidak masuk ke daftar kegagalan mana pun
    for check_id in ['FIN-01', 'FIN-03', 'FIN-10']:
        assert 'LOAN_01' not in results[check_id]['sample_failing_ids']