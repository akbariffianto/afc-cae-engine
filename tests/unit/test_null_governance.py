import pytest
import pandas as pd
import numpy as np
from src.audit_engine.null_governance import NullGovernanceClassifier

@pytest.fixture
def synthetic_null_dataset():
    """
    Menghasilkan dataset sintetis dengan kombinasi anomali null
    yang dirancang khusus untuk memicu setiap kondisi di NullGovernanceClassifier.
    """
    data = {
        'application_type': ['Individual', 'Individual', 'Individual', 'Joint App', 'Individual'],
        'annual_inc_joint': [np.nan, np.nan, np.nan, 150000.0, np.nan],
        'open_acc_6m': [np.nan, 2.0, np.nan, np.nan, np.nan], # Baris ke-2 memicu pelanggaran FEN
        'mths_since_last_delinq': [34.0, np.nan, 12.0, np.nan, np.nan], # Baris 2, 4, 5 memicu sentinel 999
        'emp_title': ['Engineer', np.nan, np.nan, 'Manager', 'Teacher'],
        'emp_length': ['10+ years', '2 years', np.nan, '5 years', '1 year'], # Baris ke-3 memicu UCG Dual Null
        'annual_inc': [60000.0, 45000.0, 80000.0, np.nan, 55000.0], # Baris ke-4 memicu UCG Critical P1
        'desc': ['Great loan', np.nan, np.nan, 'Consolidation', np.nan]
    }
    return pd.DataFrame(data)

def test_null_taxonomy_classification(synthetic_null_dataset):
    """
    Memvalidasi bahwa mesin secara akurat membedakan antara null yang sah 
    dan null anomali sesuai taksonomi PRD.
    """
    classifier = NullGovernanceClassifier()
    df_processed, audit_log = classifier.process(synthetic_null_dataset)
    
    # --- 1. Validasi FEN (Feature Epoch Null) ---
    assert len(audit_log["FEN_violations"]) == 1
    assert audit_log["FEN_violations"][0]["column"] == "open_acc_6m"
    assert audit_log["FEN_violations"][0]["violation_count"] == 1
    assert "open_acc_6m" not in df_processed.columns, "Kolom FEN gagal di-drop dari dataset proses"

    # --- 2. Validasi IM (Informative Missingness) ---
    # Memeriksa pembuatan indikator biner
    assert 'has_delinquency_history' in df_processed.columns
    assert 'has_desc_narrative' in df_processed.columns
    
    # Memeriksa imputasi sentinel 999 pada field temporal
    assert df_processed['mths_since_last_delinq'].iloc[1] == 999.0
    assert df_processed['mths_since_last_delinq'].iloc[3] == 999.0
    
    # Memeriksa kebenaran bendera biner
    assert df_processed['has_delinquency_history'].iloc[0] == 1  # Tidak null (ada riwayat)
    assert df_processed['has_delinquency_history'].iloc[1] == 0  # Null (tidak ada riwayat)

    # --- 3. Validasi UCG (Underwriting Completeness Gap) ---
    ucg_findings = [f['finding'] for f in audit_log["UCG_findings"]]
    
    # P2: Dual Employment Null
    assert "UCG-DUAL-EMPLOYMENT-NULL" in ucg_findings
    dual_null_log = next(f for f in audit_log["UCG_findings"] if f["finding"] == "UCG-DUAL-EMPLOYMENT-NULL")
    assert dual_null_log["count"] == 1
    
    # P1: Critical Null
    assert "UCG-CRITICAL-NULL-ANNUAL_INC" in ucg_findings
    critical_null_log = next(f for f in audit_log["UCG_findings"] if f["finding"] == "UCG-CRITICAL-NULL-ANNUAL_INC")
    assert critical_null_log["count"] == 1

    # --- 4. Validasi PDAN ---
    pdan_assertions = [f['column'] for f in audit_log["PDAN_assertions"]]
    assert "annual_inc_joint" in pdan_assertions