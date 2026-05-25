import pandas as pd
import numpy as np
from typing import Dict, Any

class BorrowerProfileModule:
    """
    Modul PRF — Integritas Profil Peminjam AFC-CAE.
    Memeriksa konsistensi identitas, temporalitas kredit, dan anomali aplikasi.
    """
    def __init__(self):
        pass

    def execute(self, df: pd.DataFrame) -> Dict[str, Any]:
        results = {}
        total_records = len(df)

        if total_records == 0:
            return results

        # --- PRF-01: Keunikan member_id (Toleransi Nol) ---
        if 'member_id' in df.columns:
            # Tandai semua baris yang memiliki member_id duplikat
            prf_01_failures = df.duplicated(subset=['member_id'], keep=False)
            results['PRF-01'] = self._format_result(
                check_id='PRF-01',
                failures=prf_01_failures,
                df=df,
                severity='P1_KRITIS'
            )

        # --- PRF-04: Vektor Kecurangan Aplikasi / AFV-1 (Batas IQR + Not Verified) ---
        if 'annual_inc' in df.columns and 'verification_status' in df.columns:
            annual_inc_clean = df['annual_inc'].dropna()
            if len(annual_inc_clean) > 0:
                q1 = annual_inc_clean.quantile(0.25)
                q3 = annual_inc_clean.quantile(0.75)
                iqr = q3 - q1
                upper_limit = q3 + (3 * iqr) # 3x IQR sesuai PRD untuk outlier ekstrem
                
                extreme_income_mask = df['annual_inc'] > upper_limit
                not_verified_mask = df['verification_status'].astype(str) == 'Not Verified'
                
                prf_04_failures = extreme_income_mask & not_verified_mask
                results['PRF-04'] = self._format_result(
                    check_id='PRF-04',
                    failures=prf_04_failures,
                    df=df,
                    severity='P2_TINGGI'
                )

        # --- PRF-07: earliest_cr_line <= issue_d (Kemustahilan Temporal) ---
        if 'earliest_cr_line' in df.columns and 'issue_d' in df.columns:
            # Asumsikan kolom sudah melewati DType Consistency Gate (sudah bertipe datetime64)
            cr_line_dt = pd.to_datetime(df['earliest_cr_line'], errors='coerce')
            issue_dt = pd.to_datetime(df['issue_d'], errors='coerce')
            
            # Gagal jika garis kredit pertama kali dibuka SEBELUM tanggal penerbitan (kemustahilan)
            prf_07_failures = cr_line_dt > issue_dt
            results['PRF-07'] = self._format_result(
                check_id='PRF-07',
                failures=pd.Series(prf_07_failures, index=df.index),
                df=df,
                severity='P1_KRITIS'
            )

        return results

    def _format_result(self, check_id: str, failures: pd.Series, df: pd.DataFrame, severity: str) -> Dict[str, Any]:
        failure_count = int(failures.sum())
        total_records = len(df)
        sample_failing_ids = df[failures].index[:10].tolist()

        return {
            "check_id": check_id,
            "records_tested": total_records,
            "failure_count": failure_count,
            "failure_rate_pct": round((failure_count / total_records) * 100, 4),
            "severity": severity,
            "status": "GAGAL" if failure_count > 0 else "LULUS",
            "sample_failing_ids": sample_failing_ids
        }