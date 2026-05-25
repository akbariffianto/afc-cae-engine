import pandas as pd
import numpy as np
from typing import Dict, Any

class FinancialReconciliationModule:
    """
    Modul FIN — Integritas Rekonsiliasi Keuangan AFC-CAE.
    Mengeksekusi pemeriksaan deterministik berbasis aturan menggunakan operasi vektorisasi.
    """
    def __init__(self, amnt_tolerance: float = 1.00):
        self.amnt_tolerance = amnt_tolerance

    def execute(self, df: pd.DataFrame) -> Dict[str, Any]:
        results = {}
        total_records = len(df)

        if total_records == 0:
            return results

        # --- FIN-01: funded_amnt <= loan_amnt (Toleransi Nol) ---
        # Menggunakan operasi boolean array NumPy (vektorisasi) untuk efisiensi memori
        fin_01_failures = df['funded_amnt'] > df['loan_amnt']
        results['FIN-01'] = self._format_result(
            check_id='FIN-01',
            failures=fin_01_failures,
            df=df,
            severity='P1_KRITIS'
        )

        # --- FIN-03: Amortisasi Angsuran (Toleransi ±$1.00) ---
        # Rumus PMT: P * [r(1+r)^n] / [(1+r)^n - 1]
        # Pastikan kolom term sudah dibersihkan menjadi integer (misal: ' 36 months' -> 36)
        if 'term' in df.columns and 'int_rate' in df.columns:
            # Konversi jangka waktu ke numerik jika masih berupa string/kategori
            term_months = df['term'].astype(str).str.extract(r'(\d+)').astype(float)[0]
            p = df['loan_amnt'].astype(float)
            r = (df['int_rate'].astype(float) / 100.0) / 12.0 # Tarif bulanan
            n = term_months

            # Hindari pembagian dengan nol jika r = 0
            pmt_calc = np.where(
                r > 0,
                p * (r * (1 + r)**n) / ((1 + r)**n - 1),
                p / n
            )
            
            fin_03_failures = np.abs(df['installment'].astype(float) - pmt_calc) > self.amnt_tolerance
            results['FIN-03'] = self._format_result(
                check_id='FIN-03',
                failures=pd.Series(fin_03_failures, index=df.index),
                df=df,
                severity='P1_KRITIS'
            )

        # --- FIN-10: loan_status = 'Fully Paid' -> out_prncp == 0 (Toleransi Nol) ---
        if 'loan_status' in df.columns and 'out_prncp' in df.columns:
            fully_paid_mask = df['loan_status'].astype(str) == 'Fully Paid'
            fin_10_failures = fully_paid_mask & (df['out_prncp'].astype(float) > 0)
            results['FIN-10'] = self._format_result(
                check_id='FIN-10',
                failures=fin_10_failures,
                df=df,
                severity='P1_KRITIS'
            )

        return results

    def _format_result(self, check_id: str, failures: pd.Series, df: pd.DataFrame, severity: str) -> Dict[str, Any]:
        """Helper untuk menstandardisasi manifest output per pemeriksaan sesuai spesifikasi JSON."""
        failure_count = int(failures.sum())
        total_records = len(df)
        
        # Ambil maksimal 10 sampel ID yang gagal untuk jejak forensik audit
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