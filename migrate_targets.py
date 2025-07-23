import os
import sys
from flask import Flask
from models import db

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/pms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def migrate_targets():
    with app.app_context():
        print("Adding new target columns to User table...")
        
        # Check if the database exists
        if not os.path.exists('instance/pms.db'):
            print("Database not found. Creating new database...")
            db.create_all()
            print("Database created successfully.")
            return
        
        # Add new columns to User table
        try:
            # Check if columns already exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_columns = [column['name'] for column in inspector.get_columns('user')]
            
            # Add TND target columns
            if 'ms_azure_900_target' not in existing_columns:
                db.engine.execute('ALTER TABLE user ADD COLUMN ms_azure_900_target INTEGER DEFAULT 0')
                print("Added ms_azure_900_target column")
            
            if 'seo_starter_target' not in existing_columns:
                db.engine.execute('ALTER TABLE user ADD COLUMN seo_starter_target INTEGER DEFAULT 0')
                print("Added seo_starter_target column")
            
            if 'seo_smm_target' not in existing_columns:
                db.engine.execute('ALTER TABLE user ADD COLUMN seo_smm_target INTEGER DEFAULT 0')
                print("Added seo_smm_target column")
            
            if 'dm_crash_target' not in existing_columns:
                db.engine.execute('ALTER TABLE user ADD COLUMN dm_crash_target INTEGER DEFAULT 0')
                print("Added dm_crash_target column")
            
            if 'job_ready_target' not in existing_columns:
                db.engine.execute('ALTER TABLE user ADD COLUMN job_ready_target INTEGER DEFAULT 0')
                print("Added job_ready_target column")
            
            if 'azure_combo_target' not in existing_columns:
                db.engine.execute('ALTER TABLE user ADD COLUMN azure_combo_target INTEGER DEFAULT 0')
                print("Added azure_combo_target column")
            
            # Add Category target columns
            if 'recruitment_target' not in existing_columns:
                db.engine.execute('ALTER TABLE user ADD COLUMN recruitment_target INTEGER DEFAULT 0')
                print("Added recruitment_target column")
            
            if 'college_db_target' not in existing_columns:
                db.engine.execute('ALTER TABLE user ADD COLUMN college_db_target INTEGER DEFAULT 0')
                print("Added college_db_target column")
            
            if 'client_db_target' not in existing_columns:
                db.engine.execute('ALTER TABLE user ADD COLUMN client_db_target INTEGER DEFAULT 0')
                print("Added client_db_target column")
            
            if 'school_lead_db_target' not in existing_columns:
                db.engine.execute('ALTER TABLE user ADD COLUMN school_lead_db_target INTEGER DEFAULT 0')
                print("Added school_lead_db_target column")
            
            print("Migration completed successfully.")
        except Exception as e:
            print(f"Error during migration: {str(e)}")
            print("You may need to recreate the database if this is a critical error.")

if __name__ == '__main__':
    migrate_targets()