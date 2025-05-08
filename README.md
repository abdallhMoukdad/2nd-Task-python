# Flask Authentication System

A complete authentication system built with Flask, featuring user registration, login, profile management, and password reset functionality. This project includes both API endpoints and web interface.

## Features

- **User Authentication**

  - Registration with email verification
  - Login with JWT token generation
  - Password reset via email

- **API Endpoints**

  - `/api/register` - Create new user account
  - `/api/login` - Authenticate user and receive token
  - `/api/profile` - Access protected user profile information
  - `/api/forgot-password` - Request password reset

- **Web Interface**

  - User registration form
  - Login page
  - Dashboard (protected)
  - User profile page (protected)
  - Password reset request and confirmation

- **Security Features**
  - Password hashing using Werkzeug
  - JWT-based authentication
  - Protected routes using decorators

## Installation

### Prerequisites

- Python 3.6+
- pip

### Setup

1. Clone the repository:

   ```
   git clone https://github.com/abdallhMoukdad/2nd-Task-python
   cd 2nd-Task-python
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```


## Project Structure

```
2nd-Task-python/
├── 2nd-app.py                  # Main application file
├── extensions.py           # Database extension
├── models.py               # User model
├── requirements.txt        # Project dependencies
├── templates/              # HTML templates
│   ├── home.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── forgot_password.html
│   └── reset_password.html
```

## Configuration

The application uses SQLite for development but can be configured to use other databases by changing the `SQLALCHEMY_DATABASE_URI` in `2nd-app.py`.

Email settings are loaded from environment variables with sensible defaults for development.

## Usage

1. Run the application:

   ```
   python3 2nd-app.py
   ```

2. Access the web interface at `http://localhost:5000`

3. For API usage, here are some example requests:

   **Register a new user**

   ```bash
   curl -X POST http://localhost:5000/api/register \
     -H "Content-Type: application/json" \
     -d '{"name":"John Doe","email":"john@example.com","password":"securepassword"}'
   ```

   **Login**

   ```bash
   curl -X POST http://localhost:5000/api/login \
     -H "Content-Type: application/json" \
     -d '{"email":"john@example.com","password":"securepassword"}'
   ```

   **Access protected profile with JWT token**

   ```bash
   curl -X GET http://localhost:5000/api/profile \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

## Security Considerations

- Change the JWT secret key in production
- Use HTTPS in production
- Consider adding rate limiting for login attempts
- For production, use a more robust database system like PostgreSQL or MySQL

## Running in Production

For production deployment:

1. Use a production WSGI server like Gunicorn:

   ```
   pip install gunicorn
   gunicorn app:app
   ```

2. Set appropriate environment variables for production

3. Configure a reverse proxy like Nginx

