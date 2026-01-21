"""LangChain tools for the TaskTimer API."""

import json

import requests
from langchain_core.tools import tool

# Configurable base URL for the API
BASE_URL: str = "http://localhost:8000"


def set_base_url(url: str) -> None:
    """Set the base URL for the TaskTimer API.

    Args:
        url: The base URL (e.g., "http://localhost:8000" or "https://api.example.com")
    """
    global BASE_URL
    BASE_URL = url.rstrip("/")


def get_base_url() -> str:
    """Get the current base URL for the TaskTimer API."""
    return BASE_URL


@tool
def track_task(user_id: int, description: str) -> str:
    """Start tracking a new task for a user.

    Args:
        user_id: The ID of the user starting the task.
        description: A description of the task being tracked.

    Returns:
        A JSON string containing the task ID and user ID of the newly created task,
        or an error message if the request failed.
    """
    try:
        response = requests.post(
            f"{BASE_URL}/track",
            json={"user_id": user_id, "description": description},
        )
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"


@tool
def stop_task(task_id: int, user_id: int) -> str:
    """Stop tracking an active task.

    Args:
        task_id: The ID of the task to stop.
        user_id: The ID of the user who owns the task.

    Returns:
        A JSON string containing the task ID and user ID of the stopped task,
        or an error message if the request failed (e.g., task not found).
    """
    try:
        response = requests.post(
            f"{BASE_URL}/stop",
            json={"id": task_id, "user_id": user_id},
        )
        if response.status_code == 404:
            return f"Error: Task with id={task_id} and user_id={user_id} not found."
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"


@tool
def get_times(user_id: int, date: str) -> str:
    """Get all tasks and time spent for a user on a specific date.

    Args:
        user_id: The ID of the user to get tasks for.
        date: The date to query in YYYY-MM-DD format (e.g., "2024-01-15").

    Returns:
        A JSON string containing a list of dicts with task details. Each dict has:
        - id: The task ID
        - description: The task description
        - time_spent: Time spent on the task in seconds (float)
        Returns an error message if the request failed.
    """
    try:
        response = requests.get(
            f"{BASE_URL}/times",
            params={"user_id": user_id, "date": date},
        )
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"


# List of all available tools for easy import
tools = [track_task, stop_task, get_times]
