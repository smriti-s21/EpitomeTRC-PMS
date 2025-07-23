from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
from models import db, User
import os

app = Flask(__name__)

# Secret key for session and CSRF protection
app.secret_key = os.environ.get("SECRET_KEY", "your_default_secret_key")

# PostgreSQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://pms_rovz_user:qFT3jUceAkt39Qx8xXtUqiaAIuuL8dGy@dpg-d20euq7fte5s738r5r4g-a:5432/pms_rovz'  # fallback for local testing
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Load user for login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Context processor to inject current time
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Import routes (ensure routes.py uses @app.route decorators)
from routes import *

# Optional package check (you can remove in production)
def check_required_packages():
    try:
        import pandas
        import openpyxl
        print("Required packages are installed.")
        return True
    except ImportError as e:
        print(f"Missing required package: {str(e)}")
        print("Please run 'pip install -r requirements.txt' to install required packages.")
        return False

# Only run if testing locally (this block is ignored by gunicorn)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Run only once or replace with Alembic migrations in production
    check_required_packages()
    app.run(debug=True)
