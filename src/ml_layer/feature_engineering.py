import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler, OrdinalEncoder

class AuditFeatureEngineer:
    """
    Komponen Rekayasa Fitur AFC-CAE v1.1.
    Mempersiapkan data keuangan pinjaman ke dalam bentuk matriks numerik yang siap diserap oleh AI,
    menggunakan RobustScaler untuk mengamankan data dari sebaran heavy-tail.
    """
    def __init__(self):
        self.scaler = RobustScaler()
        self.encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
        
        # 18 Fitur Utama sesuai spesifikasi PRD
        self.continuous_features = [
            'loan_amnt', 'funded_amnt', 'int_rate', 'installment', 
            'annual_inc', 'dti', 'delinq_2yrs', 'inq_last_6mths', 
            'open_acc', 'pub_rec', 'revol_bal', 'revol_util', 
            'total_acc', 'total_pymnt', 'out_prncp'
        ]
        self.im_indicators = [
            'has_delinquency_history', 'has_public_record'
        ]
        self.categorical_features = ['grade_encoded']

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        """Mentransformasikan DataFrame input menjadi matriks numerik siap-pakai untuk ML."""
        df_feats = df.copy()

        # 1. Transformasi Logaritma untuk Fitur Ekor Kanan Berat (heavy-tail)
        for col in ['annual_inc', 'revol_bal']:
            if col in df_feats.columns:
                # Menggunakan log1p untuk mengantisipasi nilai nol secara aman
                df_feats[col] = np.log1p(df_feats[col].astype(float))

        # 2. Penskalaan Fitur Kontinu menggunakan RobustScaler (Median/IQR)
        if all(col in df_feats.columns for col in self.continuous_features):
            df_feats[self.continuous_features] = self.scaler.fit_transform(
                df_feats[self.continuous_features].astype(float)
            )
        
        # 3. Encoding Ordinal untuk Tingkat Risiko Kredit (Grade)
        if 'grade' in df_feats.columns:
            # Mengubah urutan grade A=0 ... G=6 secara berurutan
            df_feats['grade_encoded'] = self.encoder.fit_transform(df_feats[['grade']].astype(str))
        else:
            df_feats['grade_encoded'] = 0

        # Pastikan kolom indikator IM siap (jika belum diproses di Null Governance, default ke 0)
        for col in self.im_indicators:
            if col not in df_feats.columns:
                df_feats[col] = 0

        # Konsolidasikan seluruh 18 kolom fitur secara urut
        all_features = self.continuous_features + self.im_indicators + self.categorical_features
        return df_feats[all_features].fillna(0).to_numpy()