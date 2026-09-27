"""Integration tests for business analysis, period comparisons, and simulations."""
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

SAMPLE_SAAS_CSV = b"""date,mrr,churn_rate,cac,region,segment
2025-01-01,100000,2.1,300,North America,Enterprise
2025-01-01,50000,3.5,180,EMEA,Pro
2025-02-01,110000,2.0,290,North America,Enterprise
2025-02-01,55000,3.2,175,EMEA,Pro
2025-03-01,120000,1.9,280,North America,Enterprise
2025-03-01,60000,3.0,170,EMEA,Pro
2025-04-01,80000,5.8,450,North America,Enterprise
2025-04-01,42000,4.9,260,EMEA,Pro
"""


@pytest.fixture
def uploaded_dataset_id():
    files = {"file": ("saas_test.csv", io.BytesIO(SAMPLE_SAAS_CSV), "text/csv")}
    res = client.post("/api/v1/datasets/upload", files=files)
    assert res.status_code == 200
    return res.json()["dataset"]["id"]


def test_period_comparison(uploaded_dataset_id):
    """Test period-over-period calculation."""
    payload = {
        "dataset_id": uploaded_dataset_id,
        "date_column": "date",
        "metric_column": "mrr",
        "period_type": "month",
    }
    res = client.post("/api/v1/analysis/compare-periods", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["metric"] == "mrr"
    assert len(data["periods"]) == 4
    assert data["largest_drop_period"] == "2025-04"


def test_contribution_analysis(uploaded_dataset_id):
    """Test segment contribution breakdown."""
    res = client.get(
        f"/api/v1/analysis/contribution?dataset_id={uploaded_dataset_id}&metric=mrr&dimension=region"
    )
    assert res.status_code == 200
    data = res.json()
    assert data["metric"] == "mrr"
    assert len(data["items"]) == 2
    assert data["items"][0]["percentage_share"] > 50.0


def test_safe_sql_query(uploaded_dataset_id):
    """Test safe read-only SQL execution and injection protection."""
    # Valid SELECT
    payload = {
        "dataset_id": uploaded_dataset_id,
        "query": "SELECT region, SUM(mrr) AS total_mrr FROM saas_test GROUP BY region",
    }
    # Using the registered table
    get_res = client.get(f"/api/v1/datasets/{uploaded_dataset_id}")
    table_name = get_res.json()["table_name"]
    payload["query"] = f'SELECT region, SUM(mrr) AS total_mrr FROM "{table_name}" GROUP BY region'

    res = client.post("/api/v1/analysis/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["rows"]) == 2

    # Forbidden DDL/DML attempt
    bad_payload = {
        "dataset_id": uploaded_dataset_id,
        "query": f'DROP TABLE "{table_name}"',
    }
    bad_res = client.post("/api/v1/analysis/query", json=bad_payload)
    assert bad_res.json()["success"] is False


def test_ai_investigation_and_evidence(uploaded_dataset_id):
    """Test full AI investigation with verifiable evidence items."""
    payload = {
        "dataset_id": uploaded_dataset_id,
        "question": "Why did MRR drop in April 2025?",
        "focus_metric": "mrr",
    }
    res = client.post("/api/v1/investigation/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["target_metric"] == "mrr"
    assert len(data["hypotheses_tested"]) > 0
    assert len(data["evidence_package"]) > 0
    assert len(data["recommendations"]) > 0

    # Verify that evidence has verifiable proof
    first_ev = data["evidence_package"][0]
    assert "sql_query" in first_ev
    assert "proof" in first_ev
    assert first_ev["proof"]["confidence_pct"] >= 80.0


def test_decision_graph_generation(uploaded_dataset_id):
    """Test Decision Graph node and edge construction."""
    payload = {
        "dataset_id": uploaded_dataset_id,
        "question": "Why did MRR drop in April 2025?",
        "focus_metric": "mrr",
    }
    res = client.post("/api/v1/graph/build", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["nodes"]) >= 4
    assert len(data["edges"]) >= 3

    # Check node types
    node_types = {n["type"] for n in data["nodes"]}
    assert "question" in node_types
    assert "hypothesis" in node_types
    assert "action" in node_types
    assert "simulation" in node_types


def test_what_if_simulation(uploaded_dataset_id):
    """Test grounded what-if parameter simulation."""
    payload = {
        "dataset_id": uploaded_dataset_id,
        "target_metric": "mrr",
        "price_change_pct": 10.0,
        "churn_reduction_pct": 15.0,
        "conversion_boost_pct": 5.0,
    }
    res = client.post("/api/v1/simulation/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["target_metric"] == "mrr"
    assert data["projected_value"] > data["baseline_value"]
    assert len(data["scenarios"]) == 3
    assert len(data["timeline_curve"]) == 6
