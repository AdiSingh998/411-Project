# tests/test_full_smoketest.py

import pytest
from unittest.mock import patch
from weather.models.user_model import Users
from weather.models.weatherdata_model import WeatherData
from weather.models.weatherlocation_model import FavoriteLocation
from weather import db


MOCK_WEATHER = {
    'city': 'MockCity',
    'country': 'MC',
    'temp_celsius': 21.0,
    'humidity_percent': 55,
    'description': 'Partly cloudy',
    'wind_speed_mps': 4.5,
    'cloud_cover_percent': 20
}


@pytest.fixture(scope="module")
def user_credentials():
    username = "full_smoke_user"
    password = "full_smoke_pass"
    try:
        Users.delete_user(username)
    except ValueError:
        pass

    Users.create_user(username, password)
    yield username, password
    try:
        Users.delete_user(username)
    except Exception:
        pass


@patch('weather.utils.api_utils.getweather')
def test_all_functions(mock_getweather, user_credentials):
    username, password = user_credentials
    user_id = Users.get_id_by_username(username)

    # USER FUNCTIONS
    assert Users.check_password(username, password)
    Users.update_password(username, "new_pass")
    assert Users.check_password(username, "new_pass")

    # WEATHERDATA + FAVORITELOCATION
    mock_getweather.return_value = MOCK_WEATHER
    wd = WeatherData(user_id)

    # add_location (-> FavoriteLocation.add_favorite)
    wd.add_location("MockCity")

    # list_all_favorites_for_user
    favorites = FavoriteLocation.list_all_favorites_for_user(user_id)
    assert any(fav.city == "MockCity" for fav in favorites)

    # update_weather_data
    updated_data = MOCK_WEATHER.copy()
    updated_data["temp_celsius"] = 30.0
    assert FavoriteLocation.update_weather_data(user_id, "MockCity", updated_data)

    # get_all_locations
    all_data = wd.get_all_locations()
    assert all_data[0]["temperature"] == 30.0

    # delete_favorite
    assert FavoriteLocation.delete_favorite(user_id, "MockCity")

    # re-add for testing clear_locations
    wd.add_location("MockCity")
    wd.clear_locations()
    assert not wd.get_all_locations()

