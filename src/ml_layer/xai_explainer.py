import pandas as pd
import numpy as np
from typing import Dict, Any, List

class AuditXAIExplainer:
    """
    Komponen Explainable AI (XAI) AFC-CAE v1.1.
    Mengimplementasikan Metode XAI-1 untuk memecah faktor pendorong anomali
    berdasarkan deviasi relatif terhadap median segmen operasional (Grade x Term).
    """
    def __init__(self, feature_cols: List[str]):
        self.feature_cols = feature_cols
        self.segment_medians = None

    def fit_baseline(self, df: pd.DataFrame):
        """Menghitung dan mengunci nilai median untuk setiap segmen kombinasi Grade dan Term."""
        # Pastikan tidak ada kegagalan fungsi jika kolom bertipe kategori dengan observed=False
        self.segment_medians = df.groupby(['grade', 'term'], observed=False)[self.feature_cols].median()

    def explain_record(self, record: pd.Series) -> Dict[str, Any]:
        """
        Menghasilkan laporan XAI untuk satu rekaman yang ditandai sebagai anomali.
        Mengurutkan 3 fitur pendorong utama (Top 3 Anomaly Drivers).
        """
        if self.segment_medians is None:
            raise ValueError("Baseline median segmen belum dihitung. Jalankan fit_baseline() terlebih dahulu.")

        grade = record['grade']
        term = record['term']
        
        # Ambil median khusus untuk segmen milik rekaman ini
        try:
            idx = (grade, term) if isinstance(self.segment_medians.index, pd.MultiIndex) else grade
            segment_med = self.segment_medians.loc[idx]
        except KeyError:
            # Antisipasi jika ada kombinasi segmen baru yang tidak terekam di baseline
            return {"error": f"Segmen ({grade}, {term}) tidak ditemukan dalam baseline data."}

        deviations = {}
        record_index = record.index
        for col in self.feature_cols:
            if col in record_index:
                rec_val = float(record[col])
                med_val = float(segment_med[col])
                
                # Hitung persentase deviasi relatif terhadap median kelompoknya
                if med_val != 0:
                    pct_deviation = ((rec_val - med_val) / abs(med_val)) * 100
                else:
                    pct_deviation = "INF" if rec_val != 0 else 0.0

                deviations[col] = {
                    "record_value": round(rec_val, 2),
                    "segment_median": round(med_val, 2),
                    "pct_deviation": pct_deviation
                }

        # Urutkan berdasarkan nilai absolut deviasi terbesar (faktor pendorong paling ekstrem)
        def _sort_key(item):
            v = item[1]['pct_deviation']
            return float('inf') if isinstance(v, str) else abs(v)

        sorted_drivers = sorted(
            deviations.items(), 
            key=_sort_key, 
            reverse=True
        )

        top_3_drivers = [item[0] for item in sorted_drivers[:3]]
        
        return {
            "method": "segment_median_deviation",
            "segment_context": {"grade": str(grade), "term": str(term)},
            "top_3_anomaly_drivers": top_3_drivers,
            "deviation_profile": dict(sorted_drivers)
        }