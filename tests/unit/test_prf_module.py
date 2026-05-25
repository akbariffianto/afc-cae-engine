import pytest
import pandas as pd
from src.audit_engine.modules.prf_module import BorrowerProfileModule

@pytest.fixture
def synthetic_borrower_dataset():
    """
    Menghasilkan data profil peminjam tiruan untuk pengujian.
    - CUST_01: Valid.
    - CUST_02 & CUST_03: Duplikat member_id (Memicu PRF-01)
    - CUST_04: Pendapatan ekstrem tak terverifikasi (Memicu PRF-04)
    - CUST_05: earliest_cr_line melompati issue_d (Memicu PRF-07)
    """
    data = {
        'member_id':           ['MEM_99', 'MEM_02', 'MEM_02', 'MEM_04', 'MEM_05'],
        'annual_inc':          [60000.0,  50000.0,  55000.0,  999000.0, 70000.0], # IQR normal di kisaran 50k-70k, 999k adalah ekstrem
        'verification_status': ['Verified', 'Source Verified', 'Verified', 'Not Verified', 'Verified'],
        'earliest_cr_line':    ['Jan-2010', 'Feb-2012', 'Mar-2015', 'Jan-2011', 'Dec-2025'],
        'issue_d':             ['Jan-2020', 'Jan-2020', 'Jan-2020', 'Jan-2020', 'Jan-2024'] # CUST_05 memiliki riwayat kredit di masa depan (2025 > 2024)
    }
    return pd.DataFrame(data, index=['CUST_01', 'CUST_02', 'CUST_03', 'CUST_04', 'CUST_05'])

def test_borrower_profile_assertions(synthetic_borrower_dataset):
    module = BorrowerProfileModule()
    results = module.execute(synthetic_borrower_dataset)

    # --- Verifikasi PRF-01 (Duplikasi ID) ---
    assert results['PRF-01']['status'] == 'GAGAL'
    assert results['PRF-01']['failure_count'] == 2 # CUST_02 & CUST_03 keduanya terhitung gagal karena duplikat
    assert 'CUST_02' in results['PRF-01']['sample_failing_ids']
    assert 'CUST_03' in results['PRF-01']['sample_failing_ids']

    # --- Verifikasi PRF-04 (Potensi Fraud Aplikasi AFV-1) ---
    assert results['PRF-04']['status'] == 'GAGAL'
    assert results['PRF-04']['failure_count'] == 1
    assert 'CUST_04' in results['PRF-04']['sample_failing_ids']

    # --- Verifikasi PRF-07 (Anomali Kronologis Temporal) ---
    assert results['PRF-07']['status'] == 'GAGAL'
    assert results['PRF-07']['failure_count'] == 1
    assert 'CUST_05' in results['PRF-07']['sample_failing_ids']
    
    # Pastikan CUST_01 tetap bersih
    for check_id in ['PRF-01', 'PRF-04', 'PRF-07']:
        assert 'CUST_01' not in results[check_id]['sample_failing_ids']