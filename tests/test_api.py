import pytest
import os
import sys
from fastapi.testclient import TestClient

# Add root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.database import init_db
from ml_model.predictor import predict_disease

# Initialize database before tests
init_db()

client = TestClient(app)

def test_predict_disease_function():
    # Directly test the ML logic
    result = predict_disease("I have a very high fever and dry cough", top_k=2)
    assert len(result) > 0
    assert "disease" in result[0]
    assert "probability" in result[0]

def get_auth_token():
    # Try to register, ignore if already exists
    client.post("/api/register", json={"username": "testuser", "password": "testpassword123"})
    # Login to get token
    response = client.post("/api/login", data={"username": "testuser", "password": "testpassword123"})
    return response.json()["access_token"]

def test_chat_endpoint_unauthorized():
    response = client.post("/api/chat", json={"symptoms": "severe headache and nausea"})
    assert response.status_code == 401

def test_chat_endpoint_valid():
    token = get_auth_token()
    response = client.post(
        "/api/chat", 
        json={"symptoms": "severe headache and nausea"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "bot_response" in data
    assert "predictions" in data
    assert isinstance(data["predictions"], list)

def test_chat_endpoint_invalid():
    token = get_auth_token()
    response = client.post(
        "/api/chat", 
        json={"symptoms": "12"},
         headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200 
    assert "didn't quite catch that" in response.json()["bot_response"]

def test_history_endpoint():
    token = get_auth_token()
    response = client.get(
        "/api/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "history" in data
    assert isinstance(data["history"], list)
