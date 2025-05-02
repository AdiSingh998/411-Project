import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, request
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)

from weather.config import ProductionConfig
from weather.db import db
from weather.models.user_model import Users
from weather.models.weatherlocation_model import FavoriteLocation
from weather.models.weatherdata_model import WeatherData
from weather.utils.logger import configure_logger

load_dotenv()

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    configure_logger(app.logger)
    app.config.from_object(config_class)

    # Set up the database
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.filter_by(username=user_id).first()

    @login_manager.unauthorized_handler
    def unauthorized():
        return make_response(jsonify({
            "status": "error", 
            "message": "Authentication required"
        }), 401)

    @app.route('/api/health', methods=['GET'])
    def healthcheck():
        """Health check endpoint"""
        app.logger.info("Health check endpoint hit")
        return jsonify({
            'status': 'success',
            'message': 'Weather service is running'
        }), 200

    # User Management Endpoints
    @app.route('/api/create-user', methods=['PUT'])
    def create_user():
        """Register a new user account"""
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({
                "status": "error",
                "message": "Username and password are required"
            }), 400

        try:
            Users.create_user(username, password)
            return jsonify({
                "status": "success",
                "message": f"User '{username}' created successfully"
            }), 201
        except ValueError as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400
        except Exception as e:
            app.logger.error(f"User creation failed: {e}")
            return jsonify({
                "status": "error",
                "message": "An internal error occurred while creating user"
            }), 500

    @app.route('/api/login', methods=['POST'])
    def login():
        """Authenticate a user and log them in"""
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({
                "status": "error",
                "message": "Username and password are required"
            }), 400

        try:
            if Users.check_password(username, password):
                user = Users.query.filter_by(username=username).first()
                login_user(user)
                return jsonify({
                    "status": "success",
                    "message": f"User '{username}' logged in successfully"
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "Invalid username or password"
                }), 401
        except ValueError as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 401
        except Exception as e:
            app.logger.error(f"Login failed: {e}")
            return jsonify({
                "status": "error",
                "message": "An internal error occurred during login"
            }), 500

    @app.route('/api/logout', methods=['POST'])
    @login_required
    def logout():
        """Log out the current user"""
        logout_user()
        return jsonify({
            "status": "success",
            "message": "User logged out successfully"
        }), 200

    @app.route('/api/change-password', methods=['POST'])
    @login_required
    def change_password():
        """Change the password for the current user"""
        data = request.get_json()
        new_password = data.get("new_password")

        if not new_password:
            return jsonify({
                "status": "error",
                "message": "New password is required"
            }), 400

        try:
            username = current_user.username
            Users.update_password(username, new_password)
            return jsonify({
                "status": "success",
                "message": "Password changed successfully"
            }), 200
        except ValueError as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400
        except Exception as e:
            app.logger.error(f"Password change failed: {e}")
            return jsonify({
                "status": "error",
                "message": "An internal error occurred while changing password"
            }), 500

    # Weather Data Endpoints
    @app.route('/api/weather', methods=['POST'])
    @login_required
    def add_weather_location():
        """Add a weather location to user's favorites"""
        data = request.get_json()
        city_name = data.get("city_name")

        if not city_name:
            return jsonify({
                "status": "error",
                "message": "City name is required"
            }), 400

        try:
            user_id = Users.get_id_by_username(current_user.username)
            weather_data = WeatherData(user_id)
            weather_data.add_location(city_name)
            return jsonify({
                "status": "success",
                "message": f"Weather data for {city_name} added successfully"
            }), 201
        except ValueError as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400
        except Exception as e:
            app.logger.error(f"Failed to add location: {e}")
            return jsonify({
                "status": "error",
                "message": "An internal error occurred while adding location"
            }), 500

    @app.route('/api/weather', methods=['GET'])
    @login_required
    def get_weather_locations():
        """Get all weather locations for the current user"""
        try:
            user_id = Users.get_id_by_username(current_user.username)
            weather_data = WeatherData(user_id)
            locations = weather_data.get_all_locations()
            return jsonify({
                "status": "success",
                "locations": locations
            }), 200
        except Exception as e:
            app.logger.error(f"Failed to get locations: {e}")
            return jsonify({
                "status": "error",
                "message": "An internal error occurred while getting locations"
            }), 500

    @app.route('/api/weather/<city_name>', methods=['GET'])
    @login_required
    def get_weather_by_city(city_name):
        """Get weather data for a specific city"""
        try:
            user_id = Users.get_id_by_username(current_user.username)
            favorites = FavoriteLocation.list_all_favorites_for_user(user_id)
            
            city_data = None
            for fav in favorites:
                if fav.city.lower() == city_name.lower():
                    city_data = {
                        "city_name": fav.city,
                        "country": fav.country,
                        "temperature": fav.temp_celsius,
                        "humidity": fav.humidity_percent,
                        "description": fav.description,
                        "wind_speed": fav.wind_speed_mps,
                        "cloudiness": fav.cloud_cover_percent,
                        "last_updated": fav.last_updated.isoformat()
                    }
                    break

            if city_data:
                return jsonify({
                    "status": "success",
                    "weather": city_data
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": f"Weather data for {city_name} not found"
                }), 404
        except Exception as e:
            app.logger.error(f"Failed to get weather for {city_name}: {e}")
            return jsonify({
                "status": "error",
                "message": f"An error occurred while getting weather for {city_name}"
            }), 500

    @app.route('/api/weather', methods=['DELETE'])
    @login_required
    def clear_weather_locations():
        """Clear all weather locations for the current user"""
        try:
            user_id = Users.get_id_by_username(current_user.username)
            weather_data = WeatherData(user_id)
            weather_data.clear_locations()
            return jsonify({
                "status": "success",
                "message": "All locations cleared successfully"
            }), 200
        except Exception as e:
            app.logger.error(f"Failed to clear locations: {e}")
            return jsonify({
                "status": "error",
                "message": "An internal error occurred while clearing locations"
            }), 500

    @app.route('/api/weather/<city_name>', methods=['DELETE'])
    @login_required
    def delete_weather_location(city_name):
        """Delete a specific weather location for the current user"""
        try:
            user_id = Users.get_id_by_username(current_user.username)
            favorite = FavoriteLocation.query.filter_by(
                user_id=user_id,
                city=city_name
            ).first()

            if not favorite:
                return jsonify({
                    "status": "error",
                    "message": f"Favorite location '{city_name}' not found"
                }), 404

            db.session.delete(favorite)
            db.session.commit()
            return jsonify({
                "status": "success",
                "message": f"Location '{city_name}' deleted successfully"
            }), 200
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Failed to delete location {city_name}: {e}")
            return jsonify({
                "status": "error",
                "message": f"An error occurred while deleting location {city_name}"
            }), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.logger.info("Starting Weather Flask app...")
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        app.logger.error(f"Flask app encountered an error: {e}")
    finally:
        app.logger.info("Flask app has stopped.")
