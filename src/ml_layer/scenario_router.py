import numpy as np
import pandas as pd
from typing import Dict, Any, List, Set

class AuditScenarioRouter:
    """
    Komponen Pengarah Kebijakan Risiko Otomatis AFC-CAE v1.1.
    Menghitung tingkat komitment anomali agregat dan mengarahkan takdir alur eksekusi
    data ke Skenario A, B, atau C berdasarkan ambang batas PRD.
    """
    def __init__(self, threshold_b: float = 0.5, threshold_c: float = 5.0):
        self.threshold_b = threshold_b
        self.threshold_c = threshold_c

    def route(self, total_records: int, rbae_failing_indices: List[Any], ai_flagged_indices: List[Any]) -> Dict[str, Any]:
        """
        Menghitung persentase anomali gabungan (RBAE U AI) dan menentukan
        skenario eskalasi beserta rekomendasi tindakan sistem.
        """
        if total_records == 0:
            return {"scenario": "A", "anomaly_rate_pct": 0.0, "action": "PROCEED"}

        # Menggunakan operasi Set Union (U) untuk memastikan rekaman yang gagal di RBAE 
        # sekaligus ditandai AI tidak dihitung dua kali (double counting) sesuai rumus PRD
        combined_anomalies: Set[Any] = set(rbae_failing_indices).union(set(ai_flagged_indices))
        total_anomalies = len(combined_anomalies)
        
        # Tingkat Anomali Komposit
        anomaly_rate_pct = (total_anomalies / total_records) * 100

        # Penentuan Skenario Berdasarkan Ambang Batas
        if anomaly_rate_pct > self.threshold_c:
            scenario = "C"
            action = "EMERGENCY_HALT"
            description = "Kegagalan Kontrol Sistemik Kontaminasi Masif (> 5%). Segera bekukan seluruh pipeline hilir."
        elif anomaly_rate_pct >= self.threshold_b:
            scenario = "B"
            action = "QUARANTINE_AND_INVESTIGATE"
            description = "Zona Pantau Terdeteksi (0.5% - 5%). Isolasi data yang rusak ke staging review."
        else:
            scenario = "A"
            action = "ANNOTATE_AND_PROCEED"
            description = "Varians Kesalahan Operasional Normal (< 0.5%). Lanjutkan alur kerja dengan anotasi log."

        return {
            "scenario": scenario,
            "composite_anomaly_rate_pct": round(anomaly_rate_pct, 4),
            "total_records_evaluated": total_records,
            "detected_anomalies_count": total_anomalies,
            "action": action,
            "description": description,
            "quarantine_list": list(combined_anomalies) if scenario in ["B", "C"] else []
        }