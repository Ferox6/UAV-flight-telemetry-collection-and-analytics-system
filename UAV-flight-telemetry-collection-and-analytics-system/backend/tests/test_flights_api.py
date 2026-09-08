import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.models.flight import FlightModel
from datetime import datetime

client = TestClient(app)


@patch("app.api.flights.SessionLocal")
def test_get_flights_empty(mock_session_local):
    mock_db = MagicMock()
    mock_db.query().all.return_value = []
    mock_session_local.return_value = mock_db

    response = client.get("/api/flights")

    assert response.status_code == 200
    assert response.json() == []


@patch("app.api.flights.SessionLocal")
def test_get_flights_with_data(mock_session_local):
    mock_db = MagicMock()

    fake_flight = FlightModel(
        id=1,
        filename="LOG0001.BFL",
        duration=120.5,
        created_at=datetime(2026, 5, 28, 12, 0, 0)
    )
    mock_db.query().all.return_value = [fake_flight]
    mock_session_local.return_value = mock_db

    response = client.get("/api/flights")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 1
    assert data[0]["filename"] == "LOG0001.BFL"


@patch("app.api.flights.SessionLocal")
def test_get_flight_not_found(mock_session_local):
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None
    mock_session_local.return_value = mock_db

    response = client.get("/api/flights/999")

    assert response.status_code == 200
    assert response.json() == {"error": "Not found"}


@patch("app.api.flights.SessionLocal")
def test_clear_flights(mock_session_local):
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db

    response = client.delete("/api/flights")

    assert response.status_code == 200
    assert response.json() == {"status": "cleared"}
    mock_db.commit.assert_called_once()