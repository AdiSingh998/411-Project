import logging
from datetime import datetime
from typing import List, Dict, Optional

from sqlalchemy.exc import IntegrityError

from weather import db
from weather.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class FavoriteLocation(db.Model):
    """Database model for storing user's favorite weather locations."""
    __tablename__ = 'favorite_locations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(2), nullable=False) 
    temp_celsius = db.Column(db.Float, nullable=False)
    humidity_percent = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    wind_speed_mps = db.Column(db.Float, nullable=False)
    cloud_cover_percent = db.Column(db.Integer, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'city', name='_user_city_uc'),
    )

    @classmethod
    def add_favorite(cls, user_id: int, weather_data: Dict) -> None:
        """Add a new favorite location for a user.
        
        Args:
            user_id: ID of the user adding the favorite
            weather_data: Dictionary containing weather data for the location
                         Expected keys: city, country, temp_celsius, humidity_percent,
                                       description, wind_speed_mps, cloud_cover_percent
        """
        try:
            favorite = cls(
                user_id=user_id,
                city=weather_data['city'],
                country=weather_data['country'],
                temp_celsius=weather_data['temp_celsius'],
                humidity_percent=weather_data['humidity_percent'],
                description=weather_data['description'],
                wind_speed_mps=weather_data['wind_speed_mps'],
                cloud_cover_percent=weather_data['cloud_cover_percent']
            )
            db.session.add(favorite)
            db.session.commit()
            logger.info(f"Added favorite location {weather_data['city']} for user {user_id}")
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Database integrity error adding favorite: {str(e)}")
            raise ValueError("Failed to add favorite location - possible duplicate")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding favorite location: {str(e)}")
            raise

    @classmethod
    def list_all_favorites_for_user(cls, user_id: int) -> List['FavoriteLocation']:
        """Get all favorite locations for a specific user.
        
        Args:
            user_id: ID of the user to get favorites for
            
        Returns:
            List of FavoriteLocation objects
        """
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def delete_favorite(cls, user_id: int, city: str) -> bool:
        """Delete a favorite location for a user.
        
        Args:
            user_id: ID of the user
            city: Name of the city to remove from favorites
            
        Returns:
            bool: True if deleted, False if not found
        """
        favorite = cls.query.filter_by(user_id=user_id, city=city).first()
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            logger.info(f"Deleted favorite location {city} for user {user_id}")
            return True
        logger.info(f"No favorite location {city} found for user {user_id}")
        return False

    @classmethod
    def update_weather_data(cls, user_id: int, city: str, weather_data: Dict) -> bool:
        """Update weather data for an existing favorite location.
        
        Args:
            user_id: ID of the user
            city: Name of the city to update
            weather_data: Dictionary containing updated weather data
            
        Returns:
            bool: True if updated, False if not found
        """
        favorite = cls.query.filter_by(user_id=user_id, city=city).first()
        if favorite:
            favorite.temp_celsius = weather_data['temp_celsius']
            favorite.humidity_percent = weather_data['humidity_percent']
            favorite.description = weather_data['description']
            favorite.wind_speed_mps = weather_data['wind_speed_mps']
            favorite.cloud_cover_percent = weather_data['cloud_cover_percent']
            favorite.last_updated = datetime.utcnow()
            db.session.commit()
            logger.info(f"Updated weather data for {city} for user {user_id}")
            return True
        logger.info(f"No favorite location {city} found for user {user_id} to update")
        return False