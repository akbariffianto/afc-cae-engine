import pandas as pd
import numpy as np
from typing import Dict, Any

class CreditRiskConsistencyModule:
    """
    Modul CRS — Konsistensi Sinyal Risiko Kredit AFC-CAE.
    Mengaudit sinkronisasi indikator tunggakan, batas akun biro, dan anomali nilai saldo keuangan.
    """
    def __init__(self):
        pass

    def execute(self, df: pd.DataFrame) -> Dict[str, Any]:
        results = {}
        total_records = len(df)

        if total_records == 0:
            return results

        # --- CRS-01: open_acc <= total_acc (Toleransi Nol) ---
        if 'open_acc' in df.columns and 'total_acc' in df.columns:
            crs_01_failures = df['open_acc'] > df['total_acc']
            results['CRS-01'] = self._format_result(
                check_id='CRS-01',
                failures=crs_01_failures,
                df=df,
                severity='P1_KRITIS'
            )

        # --- CRS-02: delinq_2yrs = 0 -> mths_since_last_delinq harus NULL atau > 24 ---
        if 'delinq_2yrs' in df.columns and 'mths_since_last_delinq' in df.columns:
            # Catatan: Jika data sudah lewat Null Governance Classifier, null asli bernilai 999
            delinq_zero_mask = df['delinq_2yrs'] == 0
            
            # Melanggar jika delinq_2yrs == 0 tapi histinya mencatat ada tunggakan dalam rentang 1-24 bulan terakhir
            crs_02_failures = delinq_zero_mask & (df['mths_since_last_delinq'] <= 24)
            results['CRS-02'] = self._format_result(
                check_id='CRS-02',
                failures=crs_02_failures,
                df=df,
                severity='P2_TINGGI'
            )

        # --- CRS-12: revol_bal >= 0 (Toleransi Nol) ---
        if 'revol_bal' in df.columns:
            crs_12_failures = df['revol_bal'] < 0
            results['CRS-12'] = self._format_result(
                check_id='CRS-12',
                failures=crs_12_failures,
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