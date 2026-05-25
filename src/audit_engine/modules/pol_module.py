import pandas as pd
import numpy as np
from typing import Dict, Any

class PolicyComplianceModule:
    """
    Modul POL — Kepatuhan Kebijakan & Siklus Hidup Pinjaman AFC-CAE.
    Mengaudit integritas alur kerja, validasi sub-grade, dan konsistensi logis mesin penetapan harga.
    """
    def __init__(self):
        pass

    def execute(self, df: pd.DataFrame) -> Dict[str, Any]:
        results = {}
        total_records = len(df)

        if total_records == 0:
            return results

        # --- POL-02: Validasi Kosakata & Hierarki Sub-Grade (Toleransi Nol) ---
        if 'grade' in df.columns and 'sub_grade' in df.columns:
            # Mengambil huruf pertama dari sub_grade untuk dicocokkan dengan grade induk
            sub_grade_prefix = df['sub_grade'].astype(str).str.get(0)
            grade_clean = df['grade'].astype(str)
            
            pol_02_failures = (df['grade'].notna() & df['sub_grade'].notna()) & (sub_grade_prefix != grade_clean)
            results['POL-02'] = self._format_result(
                check_id='POL-02',
                failures=pol_02_failures,
                df=df,
                severity='P1_KRITIS'
            )

        # --- POL-04: pymnt_plan = 'y' HANYA untuk Tunggakan/Kesulitan ---
        if 'pymnt_plan' in df.columns and 'loan_status' in df.columns:
            invalid_statuses = ['Current', 'Fully Paid', 'In Grace Period']
            plan_active_mask = df['pymnt_plan'].astype(str) == 'y'
            status_normal_mask = df['loan_status'].astype(str).isin(invalid_statuses)
            
            pol_04_failures = plan_active_mask & status_normal_mask
            results['POL-04'] = self._format_result(
                check_id='POL-04',
                failures=pol_04_failures,
                df=df,
                severity='P1_KRITIS'
            )

        # --- POL-10: Invers Tingkat Median Suku Bunga per Grade (Kontrol Pricing SR 11-7) ---
        if 'grade' in df.columns and 'int_rate' in df.columns:
            # Hitung median int_rate per grade
            grade_medians = df.groupby('grade', observed=False)['int_rate'].median().sort_index()
            
            # Deteksi jika ada grade yang lebih buruk tetapi memiliki median bunga lebih rendah dari grade sebelumnya
            # Contoh: Median Grade C lebih kecil dibanding Median Grade B (Inversi)
            inversed_grades = []
            for i in range(1, len(grade_medians)):
                if grade_medians.iloc[i] <= grade_medians.iloc[i-1]:
                    inversed_grades.append(grade_medians.index[i])
            
            pol_10_failures = df['grade'].isin(inversed_grades)
            results['POL-10'] = self._format_result(
                check_id='POL-10',
                failures=pol_10_failures,
                df=df,
                severity='P2_TINGGI'
            )
            # Tambahkan metadata spesifik untuk membantu peninjauan forensik auditor
            results['POL-10']['metadata'] = {
                "calculated_medians": grade_medians.to_dict(),
                "inversed_segments": inversed_grades
            }

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