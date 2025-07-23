import os
import sys
from flask import Flask
from models import db

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/pms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def migrate_tnd_target():
    with app.app_context():
        print("Adding TND total target column to User table...")
        
        # Check if the database exists
        if not os.path.exists('instance/pms.db'):
            print("Database not found. Creating new database...")
            db.create_all()
            print("Database created successfully.")
            return
        
        # Add new column to User table
        try:
            # Check if column already exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_columns = [column['name'] for column in inspector.get_columns('user')]
            
            # Add TND total target column
            if 'tnd_total_target' not in existing_columns:
                db.engine.execute('ALTER TABLE user ADD COLUMN tnd_total_target INTEGER DEFAULT 10')
                print("Added tnd_total_target column with default value 10")
            
            print("Migration completed successfully.")
        except Exception as e:
            print(f"Error during migration: {str(e)}")
            print("You may need to recreate the database if this is a critical error.")

if __name__ == '__main__':
    migrate_tnd_target()