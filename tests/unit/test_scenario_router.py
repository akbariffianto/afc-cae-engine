import pytest
from src.ml_layer.scenario_router import AuditScenarioRouter

def test_scenario_router_decision_matrix():
    router = AuditScenarioRouter(threshold_b=0.5, threshold_c=5.0)
    total_population = 1000  # Total 1000 data sampel

    # --- Kasus 1: Skenario A (Hanya 3 data anomali = 0.3% < 0.5%) ---
    rbae_fail_1 = ["LN_01", "LN_02"]
    ai_fail_1 = ["LN_02", "LN_03"] # LN_02 beririsan (union harus mengonsolidasikannya jadi 3 data unik)
    
    res_a = router.route(total_population, rbae_fail_1, ai_fail_1)
    assert res_a['scenario'] == 'A'
    assert res_a['action'] == 'ANNOTATE_AND_PROCEED'
    assert res_a['detected_anomalies_count'] == 3
    assert len(res_a['quarantine_list']) == 0 # Skenario A tidak perlu melakukan karantina fisik

    # --- Kasus 2: Skenario B (20 data anomali = 2.0% -> Rentang 0.5% - 5%) ---
    rbae_fail_2 = [f"LN_{i}" for i in range(15)] # 0 sampai 14 (15 data)
    ai_fail_2 = [f"LN_{i}" for i in range(10, 20)] # 10 sampai 19 (10 data)
    
    res_b = router.route(total_population, rbae_fail_2, ai_fail_2)
    assert res_b['scenario'] == 'B'
    assert res_b['action'] == 'QUARANTINE_AND_INVESTIGATE'
    assert res_b['detected_anomalies_count'] == 20 # 0 sampai 19 unik
    assert len(res_b['quarantine_list']) == 20

    # --- Kasus 3: Skenario C (60 data anomali = 6.0% > 5%) ---
    rbae_fail_3 = [f"LN_{i}" for i in range(60)]
    ai_fail_3 = []
    
    res_c = router.route(total_population, rbae_fail_3, ai_fail_3)
    assert res_c['scenario'] == 'C'
    assert res_c['action'] == 'EMERGENCY_HALT'
    assert res_c['composite_anomaly_rate_pct'] == 6.0