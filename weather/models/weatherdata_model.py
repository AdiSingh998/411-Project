import logging
import os
import time
from typing import List

from weather.models.weatherlocation_model import FavoriteLocation
from weather.utils.api_utils import getweather
from weather.utils.logger import configure_logger
from weather.utils import db

logger = logging.getLogger(__name__)
configure_logger(logger)


import logging
from typing import List, Dict
from weather.utils.api_utils import getweather
from weather.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

class WeatherData:
    """Database-backed model to manage current weather locations."""

    def __init__(self, user_id: int):
        """Initialize with a specific user context."""
        self.user_id = user_id

    def add_location(self, city_name: str) -> None:
        """Fetch weather for a city and add it to the database.

        Args:
            city_name (str): The name of the city to fetch weather for.
        """
        logger.info(f"Adding weather data for city: {city_name} for user {self.user_id}")
        try:
            data = getweather(city_name)
            if not data:
                raise ValueError(f"No weather data found for city: {city_name}")

            FavoriteLocation.add_favorite(self.user_id, data)
            logger.info(f"Weather data added for {city_name}")

        except Exception as e:
            logger.error(f"Failed to add weather data for {city_name}: {e}")
            raise

    def get_all_locations(self) -> List[Dict]:
        """Return all stored weather records for the user."""
        logger.info(f"Retrieving all weather data for user {self.user_id}.")
        favorites = FavoriteLocation.list_all_favorites_for_user(self.user_id)

        return [
            {
                "city_name": fav.city,
                "country": fav.country,
                "temperature": fav.temp_celsius,
                "humidity": fav.humidity_percent,
                "description": fav.description,
                "wind_speed": fav.wind_speed_mps,
                "cloudiness": fav.cloud_cover_percent,
                "last_updated": fav.last_updated.isoformat()
            }
            for fav in favorites
        ]

    def clear_locations(self) -> None:
        """Delete all weather records for the user."""
        logger.info(f"Clearing all stored weather data for user {self.user_id}.")
        favorites = FavoriteLocation.list_all_favorites_for_user(self.user_id)

        if not favorites:
            logger.warning("No favorites to clear.")
            return

        try:
            for favorite in favorites:
                db.session.delete(favorite)
            db.session.commit()
            logger.info(f"All favorites cleared for user {self.user_id}.")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to clear favorites: {e}")
            raise