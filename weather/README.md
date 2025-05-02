
# Weather Dashboard Application

## 1. Project Title  
**Weather Dashboard Application**

## 2. Project Description  
The Weather Management API is a Flask-based web application that enables users to manage personal accounts and track real-time weather information for favorite cities. Each user can register, log in, store preferred locations, and retrieve weather data such as temperature, humidity, and wind speed.

### Core Features  
- **User Account Management**  
  - Create and delete users.  
  - Password hashing with salt and secure storage.  
  - Validate and update passwords.

- **Weather Location Management**  
  - Add favorite cities and retrieve their current weather.  
  - Store data such as temperature, humidity, cloud cover, and wind speed.  
  - Update and delete saved weather locations.  
  - Store multiple cities per user with uniqueness constraint.

- **Data Persistence**  
  - Weather data is stored in an SQLAlchemy-based SQLite database.

- **Error Handling & Logging**  
  - Comprehensive error logging for troubleshooting.

## 3. Technologies Used  
- **Flask** – Backend web framework  
- **SQLAlchemy** – ORM and database schema  
- **Flask-Login** – User session and authentication  
- **SQLite** – Lightweight database  
- **Python 3.13.3**

## 4. Installation Instructions  

### Clone the Repository  
```bash
git clone https://github.com/AdiSingh998/411-Project.git
cd weather
```

### Set up the Virtual Environment  
#### For Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### Install Dependencies  
```bash
pip install -r requirements.txt
```

## 5. Set up Environment Variables  
Create a `.env` file in the project root with the following content:
```ini
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///weather.db
```

## 6. Initialize the Database  
Run the following in a Python shell:
```python
from weather import db
from weather.app import app
app.app_context().push()
db.create_all()
```

## 7. Usage  

### Run the Flask App  
Activate your virtual environment and run:
```bash
flask run
```
Access the server at: `http://127.0.0.1:5000`

---

## Example API Functionality

### User Management
- **Create User**
- **Check Password**
- **Update Password**
- **Delete User**

### Weather Location Features
- **Add Location (City)**
- **List All Favorites**
- **Delete Specific Favorite**
- **Clear All Locations**
- **Update Existing Location Weather Data**

### Example Request: Add Location
```json
POST /api/add-location
{
  "username": "user1",
  "city_name": "London"
}
```

### Response:
```json
{
  "status": "success",
  "message": "Weather data for London added successfully"
}
```

---

## 8. Testing

This project uses `pytest` for testing.

### Run All Tests:
```bash
pytest --maxfail=1 --disable-warnings -q
```

### Tested Features:
- User creation, authentication, and deletion
- Password hashing and validation
- Weather data addition, update, retrieval, and deletion
- Database operations and integrity constraints

---

## 9. Summary  
This Weather Management API enables secure user handling and persistent storage of weather data per user. With real-time weather retrieval and custom city management, it provides a functional backend for personalized weather tracking. 

The application employs Flask for the web layer, SQLAlchemy for data persistence, and rigorous error handling and logging for maintainability.

---

## 10. Conclusion  
The Weather Management API offers a modular and secure way to handle user data and weather information. It is easily extensible and can integrate more advanced features such as forecast predictions, alerts, or graphical dashboards. With its clean architecture and maintainable codebase, it's a strong foundation for any weather-related application.
