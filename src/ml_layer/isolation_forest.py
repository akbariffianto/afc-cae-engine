import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from typing import Tuple

class AuditAnomalyDetector:
    """
    Lapisan Unsupervised ML AFC-CAE v1.1.
    Menggunakan algoritma Isolation Forest tunggal untuk mendeteksi pencilan multidimensi
    yang lolos dari saringan aturan bisnis (RBAE).
    """
    def __init__(self, contamination: float = 0.05, n_estimators: int = 200):
        # Konfigurasi parameter sesuai amanat PRD demi integritas audit bit-by-bit
        self.model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            max_features=1.0,
            bootstrap=False,
            n_jobs=-1,          # Optimalisasi komputasi pada core CPU lokal yang tersedia
            random_state=42,    # Wajib konstan demi aspek reproduktibilitas pengujian regulasi
            warm_start=False
        )

    def fit_predict(self, feature_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Melatih model dan menghasilkan skor anomali.
        Mengembalikan tuple: (anomaly_flags, anomaly_scores)
        - anomaly_flags: -1 untuk pencilan/anomali, 1 untuk rekaman normal.
        - anomaly_scores: Rentang berkelanjutan, semakin negatif artinya semakin anomali.
        """
        # Fit model dan prediksi bendera anomali
        flags = self.model.fit_predict(feature_matrix)
        
        # score_samples mengembalikan nilai negatif berkelanjutan (skor mentah iforest)
        scores = self.model.score_samples(feature_matrix)
        
        return flags, scores