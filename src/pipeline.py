import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any

from src.ingestion.schema_validator import SchemaValidator
from src.ingestion.dtype_gate import DTypeConsistencyGate
from src.audit_engine.null_governance import NullGovernanceClassifier
from src.audit_engine.modules.assertion_runner import AssertionRunner
from src.ml_layer.feature_engineering import AuditFeatureEngineer
from src.ml_layer.isolation_forest import AuditAnomalyDetector
from src.ml_layer.xai_explainer import AuditXAIExplainer
from src.ml_layer.scenario_router import AuditScenarioRouter

def run_full_audit_pipeline(file_path: str, config_path: str) -> Dict[str, Any]:
    """
    Eksekusi penuh pipeline AFC-CAE v1.1 dari penyerapan hingga routing keputusan.
    Menyatukan metode deterministik aturan bisnis dan probabilitas kecerdasan buatan.
    """
    f_path = Path(file_path)
    c_path = Path(config_path)

    # 1. Validasi Sidik Jari Skema
    validator = SchemaValidator(c_path)
    schema_res = validator.validate_schema(f_path)
    if schema_res["status"] == "SCHEMA-DRIFT-ALERT":
        return {"status": "FAILED", "step": "SCHEMA_VALIDATION", "details": schema_res}

    # 2. Gerbang Konsistensi Tipe Data (DType Gate)
    gate = DTypeConsistencyGate(c_path)
    df_raw = gate.load_and_coerce(f_path)

    # 3. Klasifikasi Taksonomi Arsitektur Null
    null_classifier = NullGovernanceClassifier()
    df_clean, null_log = null_classifier.process(df_raw)

    # 4. Mesin Pernyataan Berbasis Aturan (RBAE)
    rbae_runner = AssertionRunner()
    rbae_manifest = rbae_runner.run_all(df_clean)

    # Ekstrak indeks yang gagal dari RBAE untuk diserahkan ke router
    rbae_fail_idx = rbae_manifest["rbae_summary"]["unique_failing_records_count"]
    # Untuk simulasi index mapping riwayatkan id mentah
    rbae_failing_list = list(df_clean.index[df_clean.index.isin(rbae_manifest["FIN"].get("sample_failing_ids", []))])

    # 5. Rekayasa Fitur & Deteksi Anomali AI (Isolation Forest)
    engineer = AuditFeatureEngineer()
    X = engineer.fit_transform(df_clean)
    
    detector = AuditAnomalyDetector(contamination=0.01) # Set ambang batas deteksi AI 1%
    flags, scores = detector.fit_predict(X)
    
    # Ambil indeks data yang ditandai sebagai anomali (-1) oleh AI
    ai_flagged_indices = np.where(flags == -1)[0]
    ai_failing_list = df_clean.index[ai_flagged_indices].tolist()

    # 6. Eksplikabilitas AI (XAI) untuk Data Terpilih
    explainer = AuditXAIExplainer(feature_cols=engineer.continuous_features)
    explainer.fit_baseline(df_clean)
    
    xai_explanations = {}
    # Hasilkan penjelasan XAI hanya untuk top 5 sampel data yang ditandai AI demi menghemat komputasi
    for idx in ai_failing_list[:5]:
        record = df_clean.loc[idx]
        if isinstance(record, pd.DataFrame): # Antisipasi jika ada duplikasi index
            record = record.iloc[0]
        xai_explanations[str(idx)] = explainer.explain_record(record)

    # 7. Router Kebijakan Skenario Risiko (A / B / C)
    router = AuditScenarioRouter()
    routing_manifest = router.route(len(df_clean), rbae_failing_list, ai_failing_list)

    # Konsolidasikan Manifes Hasil Akhir Bermutu Audit
    return {
        "status": "SUCCESS",
        "dataset_name": f_path.name,
        "null_governance_logs": null_log,
        "rbae_assertions": rbae_manifest["rbae_summary"],
        "ai_anomaly_metrics": {
            "ai_flagged_count": len(ai_failing_list),
            "sample_xai_explanations": xai_explanations
        },
        "risk_decision_routing": routing_manifest
    }