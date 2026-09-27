"""Unit and integration tests for dataset ingestion, profiling, and insights."""
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.ingestion.service import ingestion_service
from app.profiling.service import profiling_service
from app.analysis.insights import insights_service


client = TestClient(app)


SAMPLE_CSV_CONTENT = b"""date,revenue,cost,profit,category,region
2025-01-01,10000,6000,4000,Electronics,North
2025-01-01,5000,3000,2000,Clothing,South
2025-02-01,12000,7000,5000,Electronics,North
2025-02-01,5500,3200,2300,Clothing,South
2025-03-01,15000,8000,7000,Electronics,North
2025-03-01,6000,3500,2500,Clothing,South
2025-04-01,8000,6000,2000,Electronics,North
2025-04-01,4000,3000,1000,Clothing,South
"""


def test_upload_dataset_csv():
    """Test uploading a CSV file through the API."""
    files = {
        "file": ("test_sales.csv", io.BytesIO(SAMPLE_CSV_CONTENT), "text/csv")
    }
    response = client.post("/api/v1/datasets/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "dataset" in data
    dataset = data["dataset"]
    assert dataset["row_count"] == 8
    assert dataset["column_count"] == 6
    assert len(dataset["columns"]) == 6


def test_get_dataset_and_list():
    """Test retrieving dataset by ID and listing all datasets."""
    # First upload
    files = {
        "file": ("test_sales_list.csv", io.BytesIO(SAMPLE_CSV_CONTENT), "text/csv")
    }
    upload_res = client.post("/api/v1/datasets/upload", files=files)
    dataset_id = upload_res.json()["dataset"]["id"]

    # Retrieve single
    get_res = client.get(f"/api/v1/datasets/{dataset_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == dataset_id

    # List all
    list_res = client.get("/api/v1/datasets")
    assert list_res.status_code == 200
    ids = [d["id"] for d in list_res.json()]
    assert dataset_id in ids


def test_dataset_profiling():
    """Test automated dataset profiling endpoint."""
    files = {
        "file": ("test_profile.csv", io.BytesIO(SAMPLE_CSV_CONTENT), "text/csv")
    }
    upload_res = client.post("/api/v1/datasets/upload", files=files)
    dataset_id = upload_res.json()["dataset"]["id"]

    profile_res = client.get(f"/api/v1/profile/{dataset_id}")
    assert profile_res.status_code == 200
    profile = profile_res.json()

    assert profile["total_rows"] == 8
    assert profile["total_columns"] == 6
    assert profile["quality_score"] == 100.0
    assert profile["primary_date_column"] == "date"
    assert "revenue" in profile["key_metrics"]
    assert "category" in profile["key_dimensions"]


def test_auto_insights_generation():
    """Test automated business insights discovery."""
    files = {
        "file": ("test_insights.csv", io.BytesIO(SAMPLE_CSV_CONTENT), "text/csv")
    }
    upload_res = client.post("/api/v1/datasets/upload", files=files)
    dataset_id = upload_res.json()["dataset"]["id"]

    insights_res = client.get(f"/api/v1/insights/{dataset_id}")
    assert insights_res.status_code == 200
    insights = insights_res.json()
    assert isinstance(insights, list)
    assert len(insights) > 0

    # Verify insights structure
    for insight in insights:
        assert "id" in insight
        assert "type" in insight
        assert "title" in insight
        assert "description" in insight
        assert "suggested_question" in insight
