import os
import sys
import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime

# Set DATABASE_URL before importing app modules
os.environ["DATABASE_URL"] = "sqlite:///test.db"

# Mock the database module before importing app
mock_database = MagicMock()
mock_database.connect = AsyncMock()
mock_database.disconnect = AsyncMock()
mock_database.execute = AsyncMock()
mock_database.fetch_one = AsyncMock()
mock_database.fetch_all = AsyncMock()

# Patch the database module
with patch.dict("sys.modules", {"tasktimer.database": MagicMock()}):
    pass

from fastapi.testclient import TestClient
from tasktimer.main import app


class TestTrackEndpoint(unittest.TestCase):
    """Tests for POST /track endpoint"""

    def setUp(self):
        self.client = TestClient(app)

    @patch("tasktimer.main.database")
    def test_track_creates_task(self, mock_database):
        mock_database.execute = AsyncMock(return_value=1)
        mock_database.connect = AsyncMock()
        mock_database.disconnect = AsyncMock()

        response = self.client.post(
            "/track",
            json={"user_id": 123, "description": "Test task"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["user_id"], 123)
        mock_database.execute.assert_called_once()

    @patch("tasktimer.main.database")
    def test_track_missing_fields(self, mock_database):
        mock_database.connect = AsyncMock()
        mock_database.disconnect = AsyncMock()

        response = self.client.post("/track", json={})

        self.assertEqual(response.status_code, 422)


class TestStopEndpoint(unittest.TestCase):
    """Tests for POST /stop endpoint"""

    def setUp(self):
        self.client = TestClient(app)

    @patch("tasktimer.main.database")
    def test_stop_existing_task(self, mock_database):
        mock_database.connect = AsyncMock()
        mock_database.disconnect = AsyncMock()
        mock_database.fetch_one = AsyncMock(return_value={
            "id": 1,
            "user_id": 123,
            "description": "Test task",
            "start_time": datetime.now(),
            "end_time": None
        })
        mock_database.execute = AsyncMock()

        response = self.client.post(
            "/stop",
            json={"id": 1, "user_id": 123}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["user_id"], 123)

    @patch("tasktimer.main.database")
    def test_stop_nonexistent_task(self, mock_database):
        mock_database.connect = AsyncMock()
        mock_database.disconnect = AsyncMock()
        mock_database.fetch_one = AsyncMock(return_value=None)

        response = self.client.post(
            "/stop",
            json={"id": 999, "user_id": 123}
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Task not found")


class TestTimesEndpoint(unittest.TestCase):
    """Tests for GET /times endpoint"""

    def setUp(self):
        self.client = TestClient(app)

    @patch("tasktimer.main.database")
    def test_get_times_returns_tasks(self, mock_database):
        mock_database.connect = AsyncMock()
        mock_database.disconnect = AsyncMock()

        start = datetime(2024, 1, 15, 9, 0, 0)
        end = datetime(2024, 1, 15, 10, 30, 0)
        mock_database.fetch_all = AsyncMock(return_value=[
            {
                "id": 1,
                "user_id": 123,
                "description": "Task 1",
                "start_time": start,
                "end_time": end
            }
        ])

        response = self.client.get("/times?user_id=123&date=2024-01-15")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], 1)
        self.assertEqual(data[0]["description"], "Task 1")
        self.assertEqual(data[0]["time_spent"], 5400.0)  # 1.5 hours in seconds

    @patch("tasktimer.main.database")
    def test_get_times_empty_list(self, mock_database):
        mock_database.connect = AsyncMock()
        mock_database.disconnect = AsyncMock()
        mock_database.fetch_all = AsyncMock(return_value=[])

        response = self.client.get("/times?user_id=123&date=2024-01-15")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    @patch("tasktimer.main.database")
    def test_get_times_ongoing_task(self, mock_database):
        """Test that ongoing tasks (no end_time) use current time for calculation"""
        mock_database.connect = AsyncMock()
        mock_database.disconnect = AsyncMock()

        start = datetime(2024, 1, 15, 9, 0, 0)
        mock_database.fetch_all = AsyncMock(return_value=[
            {
                "id": 1,
                "user_id": 123,
                "description": "Ongoing task",
                "start_time": start,
                "end_time": None
            }
        ])

        response = self.client.get("/times?user_id=123&date=2024-01-15")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertGreater(data[0]["time_spent"], 0)

    @patch("tasktimer.main.database")
    def test_get_times_missing_params(self, mock_database):
        mock_database.connect = AsyncMock()
        mock_database.disconnect = AsyncMock()

        response = self.client.get("/times")

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
