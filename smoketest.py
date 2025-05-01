import requests
import pytest
import os

# Define the base URL of your application. Adjust if needed.
BASE_URL = "http://localhost:5000/api"

def test_health_endpoint():
    """Check if the health endpoint is available and returns success."""
    health_url = f"{BASE_URL}/health"
    try:
        response = requests.get(health_url)
        assert response.status_code == 200
        assert response.json().get("status") == "success"
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Connection error: Could not connect to {health_url}")
    except Exception as e:
        pytest.fail(f"Error during health check: {e}")

def test_create_user():
    """Test the creation of a new user."""
    create_user_url = f"{BASE_URL}/create-user"
    username = "testuser_smoke"
    password = "password123_smoke"
    data = {"username": username, "password": password}

    try:
        response = requests.put(create_user_url, json=data)
        assert response.status_code == 201
        assert response.json().get("status") == "success"
        assert response.json().get("message") == f"User '{username}' created successfully"
        return username, password  # Return credentials for later tests
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Connection error: Could not connect to {create_user_url}")
    except Exception as e:
        pytest.fail(f"Error during user creation: {e}")
    return None, None

def test_add_weather(logged_in_session):
    """Test adding weather data for a city."""
    if not logged_in_session:
        pytest.skip("Login failed, skipping add weather test.")

    add_weather_url = f"{BASE_URL}/weather"
    city_name = "London"
    data = {"city_name": city_name}
    try:
        response = logged_in_session.post(add_weather_url, json=data)
        assert response.status_code == 201
        assert response.json().get("status") == "success"
        assert response.json().get("message") == f"Weather data added for {city_name}"
        return city_name
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Connection error: Could not connect to {add_weather_url}")
    except Exception as e:
        pytest.fail(f"Error during add weather: {e}")
    return None

def test_get_weather_by_city(logged_in_session, added_city):
    """Test retrieving weather data for a specific city."""
    if not logged_in_session or not added_city:
        pytest.skip("Login or adding weather failed, skipping get weather test.")

    get_weather_url = f"{BASE_URL}/weather/{added_city}"
    try:
        response = logged_in_session.get(get_weather_url)
        assert response.status_code == 200
        assert response.json().get("status") == "success"
        assert response.json().get("data").get("city_name").lower() == added_city.lower()
        assert "temperature" in response.json().get("data")
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Connection error: Could not connect to {get_weather_url}")
    except Exception as e:
        pytest.fail(f"Error during get weather: {e}")

def test_delete_weather_by_city(logged_in_session, added_city):
    """Test deleting weather data for a specific city."""
    if not logged_in_session or not added_city:
        pytest.skip("Login or adding weather failed, skipping delete weather test.")

    delete_weather_url = f"{BASE_URL}/weather/{added_city}"
    try:
        response = logged_in_session.delete(delete_weather_url)
        assert response.status_code == 200
        assert response.json().get("status") == "success"
        assert response.json().get("message") == f"Weather data for {added_city} deleted"
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Connection error: Could not connect to {delete_weather_url}")
    except Exception as e:
        pytest.fail(f"Error during delete weather: {e}")

def test_reset_users():
    """Test the reset users endpoint."""
    reset_users_url = f"{BASE_URL}/reset-users"
    try:
        response = requests.delete(reset_users_url)
        assert response.status_code == 200
        assert response.json().get("status") == "success"
        assert response.json().get("message") == "Users table recreated successfully"
        # Optionally, try to create a user again after reset
        test_create_user()
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Connection error: Could not connect to {reset_users_url}")
    except Exception as e:
        pytest.fail(f"Error during reset users: {e}")

# Pytest fixtures to manage test dependencies
@pytest.fixture
def created_user():
    """Fixture to create a user for testing and return their credentials."""
    return test_create_user()

@pytest.fixture
def logged_in_session(created_user):
    """Fixture to create and log in a user, returning a logged-in requests session."""
    if created_user:
        username, password = created_user
        session = requests.Session()
        login_url = f"{BASE_URL}/login"
        data = {"username": username, "password": password}
        try:
            response = session.post(login_url, json=data)
            if response.status_code == 200 and response.json().get("status") == "success":
                return session
        except Exception as e:
            pytest.fail(f"Error during login fixture: {e}")
    return None

@pytest.fixture
def updated_user_credentials(logged_in_session):
    """Fixture to update the user's password and return the new credentials."""
    if logged_in_session:
        return test_change_password(logged_in_session)
    return None

@pytest.fixture
def added_city(logged_in_session):
    """Fixture to add a weather record and return the city name."""
    if logged_in_session:
        return test_add_weather(logged_in_session)
    return None

if __name__ == "__main__":
    pytest.main()
