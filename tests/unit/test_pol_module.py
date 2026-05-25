import pytest
import pandas as pd
from src.audit_engine.modules.pol_module import PolicyComplianceModule

@pytest.fixture
def synthetic_policy_dataset():
    """
    Menghasilkan data kebijakan tiruan untuk pengujian.
    - TX_01: Valid (Grade A, Sub A1, Suku bunga rendah, Status normal).
    - TX_02: Gagal POL-02 (Grade B tapi Sub-grade C2 -> Misklasifikasi sistem).
    - TX_03: Gagal POL-04 (Pymnt_plan aktif 'y' pada pinjaman yang berstatus 'Fully Paid').
    - Segmen: Ditambahkan data massal untuk memicu inversi pricing POL-10 (Grade B sengaja diset bunga tinggi).
    """
    data = {
        'grade':             ['A', 'B', 'A', 'A', 'B', 'B', 'C', 'C'],
        'sub_grade':         ['A1', 'C2', 'A3', 'A2', 'B1', 'B4', 'C1', 'C5'],
        'pymnt_plan':        ['n', 'n', 'y', 'n', 'n', 'n', 'n', 'n'],
        'loan_status':       ['Current', 'Current', 'Fully Paid', 'Current', 'Current', 'Current', 'Current', 'Current'],
        'int_rate':          [5.0, 18.0, 5.5, 6.0, 18.5, 19.0, 12.0, 12.5] 
        # Perhatikan: Median Grade B (~18.5%) sengaja dibuat melonjak melampaui Median Grade C (~12.25%)
    }
    return pd.DataFrame(data, index=['TX_01', 'TX_02', 'TX_03', 'TX_04', 'TX_05', 'TX_06', 'TX_07', 'TX_08'])

def test_policy_compliance_assertions(synthetic_policy_dataset):
    module = PolicyComplianceModule()
    results = module.execute(synthetic_policy_dataset)

    # --- Verifikasi POL-02 (Hierarki Grade) ---
    assert results['POL-02']['status'] == 'GAGAL'
    assert results['POL-02']['failure_count'] == 1
    assert 'TX_02' in results['POL-02']['sample_failing_ids']

    # --- Verifikasi POL-04 (Mesin Status Rencana Pembayaran Kesulitan) ---
    assert results['POL-04']['status'] == 'GAGAL'
    assert results['POL-04']['failure_count'] == 1
    assert 'TX_03' in results['POL-04']['sample_failing_ids']

    # --- Verifikasi POL-10 (Inversi Algoritmik Suku Bunga / Kontrol Model SR 11-7) ---
    assert results['POL-10']['status'] == 'GAGAL'
    # Seluruh data dengan Grade C harus ditandai sebagai anomali karena aturan penetapan harga platform berbalik
    assert 'TX_07' in results['POL-10']['sample_failing_ids']
    assert 'TX_08' in results['POL-10']['sample_failing_ids']
    assert 'C' in results['POL-10']['metadata']['inversed_segments']