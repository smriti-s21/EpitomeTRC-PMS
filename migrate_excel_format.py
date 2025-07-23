import os
import sys
from datetime import datetime
from flask import Flask
from models import db, User, PMSEntry

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/pms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def migrate_database():
    with app.app_context():
        print("Starting database migration to Excel format...")
        
        # Check if the database exists
        if not os.path.exists('instance/pms.db'):
            print("Database file not found. Creating new database...")
            db.create_all()
            print("Database created successfully.")
            return
        
        try:
            # Backup existing data
            print("Backing up existing data...")
            users = User.query.all()
            user_data = []
            for user in users:
                user_dict = {
                    'id': user.id,
                    'username': user.username,
                    'password_hash': user.password_hash,
                    'role': user.role,
                    'name': user.name,
                    'email': user.email,
                    'is_poc': user.is_poc,
                    'target': user.target
                }
                user_data.append(user_dict)
            
            entries = PMSEntry.query.all()
            entry_data = []
            for entry in entries:
                entry_dict = {
                    'user_id': entry.user_id,
                    'date': entry.date,
                    'section': getattr(entry, 'section', None),
                    'mtd_leads': getattr(entry, 'mtd_leads', 0),
                    'daily_leads_generated': getattr(entry, 'daily_leads_generated', 0),
                    'daily_leads_contacted': getattr(entry, 'daily_leads_contacted', 0),
                    'daily_prospects': getattr(entry, 'daily_prospects', 0),
                    'daily_suspects': getattr(entry, 'daily_suspects', 0),
                    'applications_received': getattr(entry, 'applications_received', 0),
                    'interviewed': getattr(entry, 'interviewed', 0),
                    'on_hold': getattr(entry, 'on_hold', 0),
                    'shortlisted': getattr(entry, 'shortlisted', 0),
                    'rejected': getattr(entry, 'rejected', 0),
                    'support_required': getattr(entry, 'support_required', '')
                }
                entry_data.append(entry_dict)
            
            # Drop and recreate tables
            print("Dropping existing tables...")
            db.drop_all()
            print("Creating new tables with updated schema...")
            db.create_all()
            
            # Restore user data with new schema
            print("Restoring user data...")
            for user_dict in user_data:
                user = User(
                    id=user_dict['id'],
                    username=user_dict['username'],
                    password_hash=user_dict['password_hash'],
                    role=user_dict['role'],
                    name=user_dict['name'],
                    email=user_dict['email'],
                    is_poc=user_dict['is_poc'],
                    target=user_dict['target'],
                    post=user_dict.get('section', 'Unknown'),  # Map section to post
                    poc_name=None  # Will be updated later
                )
                db.session.add(user)
            
            db.session.commit()
            
            # Restore entry data with new schema
            print("Restoring entry data...")
            for entry_dict in entry_data:
                user = User.query.get(entry_dict['user_id'])
                if user:
                    entry = PMSEntry(
                        user_id=entry_dict['user_id'],
                        date=entry_dict['date'],
                        poc=None,  # Will be updated later
                        intern_name=user.name,
                        post=entry_dict.get('section', 'Unknown'),  # Map section to post
                        total_enrollments=entry_dict.get('mtd_leads', 0),
                        recruitment=entry_dict.get('applications_received', 0),
                        college_db=0,
                        client_db=0,
                        school_lead_db=0
                    )
                    db.session.add(entry)
            
            db.session.commit()
            print("Migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {str(e)}")
            db.session.rollback()
            print("Migration failed. Database rolled back.")

if __name__ == '__main__':
    migrate_database()