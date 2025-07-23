import os
import sys
from flask import Flask
from models import db

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/pms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def fix_database():
    with app.app_context():
        print("Fixing database...")
        
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()
        
        print("Database schema has been reset.")
        print("Please run the application and upload your data again.")

if __name__ == '__main__':
    fix_database()