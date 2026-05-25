import pandas as pd
from typing import Dict, Any, List
from src.audit_engine.modules.fin_module import FinancialReconciliationModule
from src.audit_engine.modules.prf_module import BorrowerProfileModule
from src.audit_engine.modules.pol_module import PolicyComplianceModule
from src.audit_engine.modules.crs_module import CreditRiskConsistencyModule

class AssertionRunner:
    """
    Orkestrator RBAE AFC-CAE.
    Menjalankan seluruh modul audit berbasis aturan secara sekuensial dan
    mengompilasi metrik kegagalan agregat untuk penentuan eskalasi risiko.
    """
    def __init__(self):
        self.modules = {
            "FIN": FinancialReconciliationModule(),
            "PRF": BorrowerProfileModule(),
            "POL": PolicyComplianceModule(),
            "CRS": CreditRiskConsistencyModule()
        }

    def run_all(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Mengeksekusi seluruh modul RBAE pada dataset."""
        manifest = {}
        total_failures = 0
        all_failing_indices = set()

        for module_name, module_instance in self.modules.items():
            module_results = module_instance.execute(df)
            manifest[module_name] = module_results
            
            # Hitung total kegagalan unik lintas kolom untuk kalkulasi tingkat anomali komposit
            for check_id, check_data in module_results.items():
                total_failures += check_data["failure_count"]
                if check_data["failure_count"] > 0:
                    all_failing_indices.update(check_data["sample_failing_ids"])

        # Menghitung summary metrik agregat tingkat RBAE
        total_records = len(df)
        manifest["rbae_summary"] = {
            "total_checks_executed": sum(len(res) for res in manifest.values()),
            "aggregate_rule_failures": total_failures,
            "unique_failing_records_count": len(all_failing_indices),
            "rbae_anomaly_rate_pct": round((len(all_failing_indices) / total_records) * 100, 4) if total_records > 0 else 0.0
        }

        return manifest