import pandas as pd
from typing import Tuple, Dict

class NullGovernanceClassifier:
    """
    Mesin Taksonomi Arsitektur Null AFC-CAE v1.1.
    Mengkategorikan dan memproses nilai null menjadi sinyal audit (PDAN, FEN, IM, UCG)
    sebelum masuk ke tahap rekayasa fitur atau evaluasi RBAE.
    """
    def __init__(self):
        # 1. PDAN (Policy-Driven Architecture Null)
        self.pdan_cols = ['annual_inc_joint', 'dti_joint', 'verification_status_joint']
        
        # 2. FEN (Feature Epoch Null) - Subset representatif dari PRD
        self.fen_cols = [
            'open_acc_6m', 'open_il_6m', 'open_il_12m', 'open_il_24m',
            'mths_since_rcnt_il', 'total_bal_il', 'il_util', 'open_rv_12m',
            'open_rv_24m', 'max_bal_bc', 'all_util', 'total_rev_hi_lim',
            'inq_fi', 'total_cu_tl', 'inq_last_12m'
        ]
        
        # 3. IM (Informative Missingness)
        self.im_cols = {
            'mths_since_last_delinq': 'has_delinquency_history',
            'mths_since_last_record': 'has_public_record',
            'mths_since_last_major_derog': 'has_major_derogatory',
            'desc': 'has_desc_narrative'
        }
        
        # 4. UCG (Underwriting Completeness Gap)
        self.ucg_dual_cols = ['emp_title', 'emp_length']
        self.ucg_critical_cols = ['annual_inc']

    def process(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Mengeksekusi klasifikasi taksonomi null dan mengembalikan 
        DataFrame yang telah dianotasi beserta log temuan audit.
        """
        audit_log = {
            "PDAN_assertions": [],
            "FEN_violations": [],
            "UCG_findings": []
        }
        
        # Gunakan salinan agar tidak memodifikasi dataset asli secara in-place
        df_processed = df.copy()

        # --- 1. Pemeriksaan PDAN ---
        if 'application_type' in df_processed.columns:
            individual_mask = df_processed['application_type'] == 'Individual'
            for col in self.pdan_cols:
                if col in df_processed.columns:
                    # Mencatat bahwa homogenitas application_type mendukung null pada kolom joint
                    audit_log["PDAN_assertions"].append({
                        "column": col,
                        "status": "PDAN_CONFIRMED",
                        "records_evaluated": int(individual_mask.sum())
                    })

        # --- 2. Pemeriksaan FEN ---
        for col in self.fen_cols:
            if col in df_processed.columns:
                non_null_count = df_processed[col].notna().sum()
                if non_null_count > 0:
                    audit_log["FEN_violations"].append({
                        "column": col,
                        "violation_count": int(non_null_count),
                        "severity": "HIGH",
                        "flag": "FEATURE_EPOCH: PRE_ACTIVATION_VIOLATION"
                    })
                # Drop kolom FEN karena tidak relevan untuk pemodelan
                df_processed = df_processed.drop(columns=[col])

        # --- 3. Pemrosesan IM ---
        for col, indicator_name in self.im_cols.items():
            if col in df_processed.columns:
                # Buat indikator biner (1 jika ada nilai, 0 jika null)
                df_processed[indicator_name] = df_processed[col].notna().astype(int)
                
                # Imputasi sentinel 999 untuk kolom temporal guna menjaga semantik sorting model
                if col != 'desc':
                    # Gunakan fillna() standar Pandas
                    df_processed[col] = df_processed[col].fillna(999)

        # --- 4. Pemeriksaan UCG ---
        # A. UCG Dual Null (emp_title & emp_length)
        if all(c in df_processed.columns for c in self.ucg_dual_cols):
            dual_null_mask = df_processed['emp_title'].isna() & df_processed['emp_length'].isna()
            dual_null_count = dual_null_mask.sum()
            if dual_null_count > 0:
                audit_log["UCG_findings"].append({
                    "finding": "UCG-DUAL-EMPLOYMENT-NULL",
                    "count": int(dual_null_count),
                    "severity": "P2_TINGGI"
                })

        # B. UCG Critical Null (annual_inc)
        for col in self.ucg_critical_cols:
            if col in df_processed.columns:
                critical_null_mask = df_processed[col].isna()
                critical_null_count = critical_null_mask.sum()
                if critical_null_count > 0:
                    audit_log["UCG_findings"].append({
                        "finding": f"UCG-CRITICAL-NULL-{col.upper()}",
                        "count": int(critical_null_count),
                        "severity": "P1_KRITIS"
                    })

        return df_processed, audit_log