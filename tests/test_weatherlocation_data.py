import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from weather.models.weatherlocation_model import FavoriteLocation
from sqlalchemy.exc import IntegrityError
from weather.db import db
from app import create_app
from config import TestConfig

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def session(app):
    """Creates a new database session for a test."""
    with app.app_context():
        yield db.session

@pytest.fixture
def sample_weather_data():
    return {
        "city": "London",
        "country": "GB",
        "temp_celsius": 15.0,
        "humidity_percent": 70,
        "description": "Cloudy",
        "wind_speed_mps": 3.5,
        "cloud_cover_percent": 80
    }

@pytest.fixture
def mock_favorite():
    return MagicMock(
        id=1,
        user_id=1,
        city="London",
        country="GB",
        temp_celsius=15.0,
        humidity_percent=70,
        description="Cloudy",
        wind_speed_mps=3.5,
        cloud_cover_percent=80,
        last_updated=datetime(2025, 4, 29, 12, 0, 0)
    )

# --- add_favorite ---

def test_add_favorite_success(app, sample_weather_data):
    """Test successfully adding a favorite location."""
    with app.app_context():
        FavoriteLocation.add_favorite(1, sample_weather_data)
        # Verify the location was added
        favorite = FavoriteLocation.query.filter_by(user_id=1, city="London").first()
        assert favorite is not None
        assert favorite.city == "London"

def test_add_favorite_integrity_error(app, sample_weather_data):
    """Test adding a duplicate favorite location."""
    with app.app_context():
        # Add the first location
        FavoriteLocation.add_favorite(1, sample_weather_data)
        
        # Try to add it again
        with pytest.raises(ValueError, match="Failed to add favorite location - possible duplicate"):
            FavoriteLocation.add_favorite(1, sample_weather_data)

# --- list_all_favorites_for_user ---

def test_list_all_favorites_for_user(app, sample_weather_data):
    """Test listing favorites for a user."""
    with app.app_context():
        # Add a favorite
        FavoriteLocation.add_favorite(1, sample_weather_data)
        
        # Get the list
        favorites = FavoriteLocation.list_all_favorites_for_user(1)
        assert len(favorites) == 1
        assert favorites[0].city == "London"

def test_list_all_favorites_empty(app):
    """Test listing favorites when user has none."""
    with app.app_context():
        favorites = FavoriteLocation.list_all_favorites_for_user(1)
        assert favorites == []

# --- delete_favorite ---

def test_delete_favorite_success(app, sample_weather_data):
    """Test successfully deleting a favorite."""
    with app.app_context():
        # Add a favorite
        FavoriteLocation.add_favorite(1, sample_weather_data)
        
        # Delete it
        result = FavoriteLocation.delete_favorite(1, "London")
        assert result is True
        
        # Verify it's gone
        favorite = FavoriteLocation.query.filter_by(user_id=1, city="London").first()
        assert favorite is None

def test_delete_favorite_not_found(app):
    """Test deleting a non-existent favorite."""
    with app.app_context():
        result = FavoriteLocation.delete_favorite(1, "Paris")
        assert result is False

# --- update_weather_data ---

def test_update_weather_data_success(app, sample_weather_data):
    """Test successfully updating weather data."""
    with app.app_context():
        # Add a favorite
        FavoriteLocation.add_favorite(1, sample_weather_data)
        
        # Update it
        updated_data = {**sample_weather_data, "temp_celsius": 18.0}
        result = FavoriteLocation.update_weather_data(1, "London", updated_data)
        assert result is True
        
        # Verify the update
        favorite = FavoriteLocation.query.filter_by(user_id=1, city="London").first()
        assert favorite.temp_celsius == 18.0

def test_update_weather_data_not_found(app, sample_weather_data):
    """Test updating a non-existent favorite."""
    with app.app_context():
        result = FavoriteLocation.update_weather_data(1, "Paris", sample_weather_data)
        assert result is False