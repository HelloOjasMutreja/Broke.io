# Django Backend Setup Guide

This document provides detailed instructions for setting up and using the Django backend for Broke.io.

## Overview

The Broke.io game now includes a Django backend with user authentication, enabling features like:
- User registration and login
- Profile management
- Future features: game state persistence, leaderboards, multiplayer, etc.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Django 5.2.7
- asgiref 3.10.0
- sqlparse 0.5.3

### 2. Initialize Database

Run Django migrations to create the database:

```bash
python manage.py migrate
```

This creates a `db.sqlite3` file with all necessary tables.

### 3. Create Admin User (Optional)

To access the Django admin interface:

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 4. Start Development Server

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

## Project Structure

```
Broke.io/
├── backend/              # Django project configuration
│   ├── settings.py      # Main settings (database, apps, static files)
│   ├── urls.py          # Root URL configuration
│   └── ...
├── users/               # User authentication app
│   ├── views.py         # Login, signup, profile views
│   ├── urls.py          # User-related URLs
│   └── ...
├── templates/           # HTML templates
│   ├── base.html        # Base template for auth pages
│   ├── index.html       # Main game page (Django version)
│   └── users/           # User authentication templates
│       ├── login.html
│       ├── signup.html
│       └── profile.html
├── css/                 # Game stylesheets (served as static)
├── js/                  # Game JavaScript (served as static)
└── manage.py            # Django management script
```

## Available URLs

- **`/`** - Main game page (works for both guests and logged-in users)
- **`/users/signup/`** - User registration
- **`/users/login/`** - User login
- **`/users/logout/`** - User logout
- **`/users/profile/`** - User profile (requires login)
- **`/admin/`** - Django admin interface (requires superuser)

## Features

### User Authentication

The authentication system uses Django's built-in `User` model with the following features:

- **Sign Up**: Users can create accounts with username and password
- **Login**: Secure authentication with password hashing
- **Logout**: Session-based logout
- **Profile**: View user information (username, join date, last login)

### Guest Play

Users can play the game without creating an account. The game header will show:
- Login and Sign Up links for guests
- Profile and Logout icons for authenticated users

### Static Files

The game's CSS and JavaScript files are served through Django's static files system:
- CSS files from `css/` directory
- JavaScript files from `js/` directory

## Development

### Running Tests

```bash
python manage.py test
```

### Creating New Apps

```bash
python manage.py startapp <app_name>
```

Don't forget to add the app to `INSTALLED_APPS` in `backend/settings.py`.

### Database Migrations

After changing models:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files (Production)

```bash
python manage.py collectstatic
```

## Security Notes

⚠️ **Important for Production:**

1. Change `SECRET_KEY` in `settings.py` to a secure, random value
2. Set `DEBUG = False` in production
3. Update `ALLOWED_HOSTS` with your domain names
4. Use a production database (PostgreSQL, MySQL) instead of SQLite
5. Use a proper web server (Gunicorn, uWSGI) behind a reverse proxy (Nginx, Apache)
6. Enable HTTPS/SSL
7. Configure proper static file serving

## Future Enhancements

With this backend foundation, you can add:

1. **Game State Persistence**
   - Save/load game progress
   - Store player properties and money

2. **Leaderboards**
   - Track player statistics
   - Display top players

3. **Multiplayer**
   - WebSocket integration for real-time gameplay
   - Match-making system

4. **Social Features**
   - Friend system
   - In-game messaging
   - Game invitations

5. **Achievements**
   - Track player accomplishments
   - Award badges and rewards

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, specify a different port:

```bash
python manage.py runserver 8080
```

### Static Files Not Loading

Make sure you've configured `STATICFILES_DIRS` in `settings.py`:

```python
STATICFILES_DIRS = [
    BASE_DIR / 'css',
    BASE_DIR / 'js',
]
```

### Database Locked Error

If you get a "database is locked" error with SQLite:
- Close any other processes accessing the database
- Consider using a client-server database for production

## Support

For issues or questions:
- Check Django documentation: https://docs.djangoproject.com/
- Open an issue on GitHub
- Review the code comments in the project files

## Standalone Game

The original `index.html` file still works as a standalone game:
- Can be opened directly in a browser without Django
- All CSS and JavaScript work with relative paths
- Perfect for offline play or simple deployment

To use standalone mode, simply open `index.html` in your browser.
