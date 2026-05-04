NDX DOCTOR DASHBOARD

A Django-based dashboard application for managing doctor and dental lab information.


OVERVIEW

The NDX Doctor Dashboard is a web application built with Django that provides a centralized interface for viewing and managing doctor information and related data. The application is designed with a clean, user-friendly interface and provides administrative capabilities for data management.


FEATURES

Doctor profile management
Dashboard interface for data visualization
Admin panel for database management
Responsive design with custom styling
RESTful URL routing structure


INSTALLATION

Prerequisites:
- Python 3.7 or higher
- pip (Python package manager)
- Virtual environment support

Setup Steps:

1. Clone or navigate to the project directory:
   cd "NDX Doctor Dashboard"

2. Create and activate a virtual environment:
   python -m venv venv
   source venv/Scripts/activate  (On Windows)
   or
   source venv/bin/activate      (On macOS/Linux)

3. Install dependencies:
   pip install -r requirements.txt

4. Set up the database:
   python manage.py migrate
   python seed_data.py  (Optional: populate with seed data)

5. For Excel data import (optional):
   - Place your Excel file "Remake Analysis - TTM.xlsx" on your desktop
   - The system automatically reads from the 'DATA' sheet
   - Run: python seed_data.py and choose option 1
   - For testing, you can limit rows in seed_data.py (max_rows_to_import variable)


CONFIGURATION

Key configuration files:

core/settings.py - Django project settings
core/urls.py - Main URL routing configuration
requirements.txt - Python package dependencies


RUNNING THE APPLICATION

Start the development server:

python manage.py runserver

The application will be available at http://127.0.0.1:8000/


PROJECT STRUCTURE

NDX Doctor Dashboard/
  core/                      Main Django project settings
    settings.py             Project configuration
    urls.py                 Main URL router
    wsgi.py                 WSGI configuration
    asgi.py                 ASGI configuration
  doctors/                   Doctor app
    models.py               Database models
    views.py                View logic
    urls.py                 App URL routing
    admin.py                Admin panel configuration
    migrations/             Database migrations
    templates/              HTML templates
    static/                 Static files (CSS, images)
  static/                    Project-wide static files
  db.sqlite3                SQLite database
  manage.py                 Django management script
  requirements.txt          Python dependencies
  seed_data.py              Script for populating test data
  inspect_excel.py          Utility to inspect Excel file columns


DATABASE

The application uses SQLite as the default database (db.sqlite3). The database schema is managed through Django migrations in the doctors/migrations/ directory.

Create a New Migration:

After modifying models:

python manage.py makemigrations
python manage.py migrate

Reset Database:

To reset and reseed the database:

Delete db.sqlite3 and migrations (except __init__.py)
python manage.py migrate
python seed_data.py


EXCEL DATA IMPORT

Your Excel import is now configured and working! The system automatically:

1. Reads from the 'DATA' sheet in "Remake Analysis - TTM.xlsx" on your desktop
2. Maps 29 columns including Month, CaseNumber, DoctorName, Department, etc.
3. Imports all 127,503 rows of production data

To import your Excel data:

1. Place "Remake Analysis - TTM.xlsx" on your desktop
2. Run: python seed_data.py
3. Choose option 1 for Excel import
4. The system will import all your production records

For testing with fewer records, edit seed_data.py and change:
max_rows_to_import = 1000  (or any number, or None for all rows)

The column mapping is already configured for your Excel file structure.


REQUIREMENTS

See requirements.txt for all project dependencies. Key packages include:

Django - Web framework
Python standard libraries - Core functionality

Install all requirements with:

pip install -r requirements.txt


ADMIN PANEL

Access the Django admin panel at http://127.0.0.1:8000/admin/ with appropriate credentials.


SUPPORT

For issues or questions about the project, please review the code comments or consult the Django documentation at https://docs.djangoproject.com/
