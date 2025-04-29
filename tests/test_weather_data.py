import pytest
from unittest.mock import patch, MagicMock
from weather.models.weatherlocation_model import FavoriteLocation
from weather.models.weatherdata_model import WeatherData  

@pytest.fixture
def weather_data():
    """Fixture to provide WeatherData instance for user with ID 1."""
    return WeatherData(user_id=1)

@pytest.fixture
def sample_weather_response():
    return {
        "city": "London",
        "country": "GB",
        "temp_celsius": 15.0,
        "humidity_percent": 70,
        "description": "Cloudy",
        "wind_speed_mps": 3.5,
        "cloud_cover_percent": 80,
        "last_updated": MagicMock(isoformat=lambda: "2025-04-29T12:00:00Z")
    }

# --- add_location ---

@patch("weather.models.weatherdata_model.getweather")
@patch("weather.models.weatherdata_model.FavoriteLocation.add_favorite")
def test_add_location_success(mock_add_favorite, mock_getweather, weather_data, sample_weather_response):
    mock_getweather.return_value = sample_weather_response
    weather_data.add_location("London")
    mock_add_favorite.assert_called_once_with(1, sample_weather_response)

@patch("weather.models.weatherdata_model.getweather", return_value=None)
def test_add_location_no_data(mock_getweather, weather_data):
    with pytest.raises(ValueError, match="No weather data found for city: London"):
        weather_data.add_location("London")

@patch("weather.models.weatherdata_model.getweather", side_effect=Exception("API failure"))
def test_add_location_failure(mock_getweather, weather_data):
    with pytest.raises(Exception, match="API failure"):
        weather_data.add_location("London")

# --- get_all_locations ---

@patch("weather.models.weatherdata_model.FavoriteLocation.list_all_favorites_for_user")
def test_get_all_locations(mock_list, weather_data, sample_weather_response):
    mock_fav = MagicMock(**sample_weather_response)
    mock_list.return_value = [mock_fav]
    result = weather_data.get_all_locations()

    assert isinstance(result, list)
    assert result[0]["city_name"] == "London"
    assert result[0]["last_updated"] == "2025-04-29T12:00:00Z"

@patch("weather.models.weatherdata_model.FavoriteLocation.list_all_favorites_for_user", return_value=[])
def test_get_all_locations_empty(mock_list, weather_data):
    assert weather_data.get_all_locations() == []

# --- clear_locations ---

@patch("weather.models.weatherdata_model.db")
@patch("weather.models.weatherdata_model.FavoriteLocation.list_all_favorites_for_user", return_value=[])
def test_clear_locations_empty(mock_list, mock_db, weather_data, caplog):
    with caplog.at_level("WARNING"):
        weather_data.clear_locations()
    assert "No favorites to clear." in caplog.text

@patch("weather.models.weatherdata_model.db")
@patch("weather.models.weatherdata_model.FavoriteLocation.list_all_favorites_for_user")
def test_clear_locations_success(mock_list, mock_db, weather_data, sample_weather_response):
    mock_fav = MagicMock()
    mock_list.return_value = [mock_fav]
    weather_data.clear_locations()
    mock_db.session.delete.assert_called_once_with(mock_fav)
    mock_db.session.commit.assert_called_once()

@patch("weather.models.weatherdata_model.db")
@patch("weather.models.weatherdata_model.FavoriteLocation.list_all_favorites_for_user")
def test_clear_locations_failure(mock_list, mock_db, weather_data):
    mock_fav = MagicMock()
    mock_list.return_value = [mock_fav]
    mock_db.session.delete.side_effect = Exception("DB failure")

    with pytest.raises(Exception, match="DB failure"):
        weather_data.clear_locations()
    mock_db.session.rollback.assert_called_once()