import os
import pytest
import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")


def test_health_endpoint():
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "healthy"
    assert "model_version" in data


def test_predict_returns_label_and_confidence():
    payload = {"text": "The food was absolutely delicious and the chef clearly has exceptional skill"}
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("label") in ["POSITIVE", "NEGATIVE"]
    assert 0 <= data.get("confidence") <= 1
    assert "model_version" in data


def test_predict_negative_text():
    payload = {"text": "This was terrible and I hated every moment of it"}
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    assert resp.status_code == 200


def test_health_returns_model_version_unstable():
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("model_version") == "unstable-v1"