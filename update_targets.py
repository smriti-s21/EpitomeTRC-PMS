import os
import sys
from flask import Flask
from models import db, User

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/pms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def update_targets():
    with app.app_context():
        print("Updating targets for all interns...")
        
        # Get all interns
        interns = User.query.filter_by(role='intern').all()
        
        for intern in interns:
            # Set TND total target to 10 for all interns
            intern.tnd_total_target = 10
            
            # Set Category targets based on post
            if intern.post == 'Human Resources':
                # HR Interns: 10, 10, 5, 50
                intern.recruitment_target = 10
                intern.college_db_target = 10
                intern.client_db_target = 5
                intern.school_lead_db_target = 50
            else:
                # Other Interns: 0, 10, 5, 50
                intern.recruitment_target = 0
                intern.college_db_target = 10
                intern.client_db_target = 5
                intern.school_lead_db_target = 50
        
        # Commit changes
        db.session.commit()
        print(f"Updated targets for {len(interns)} interns.")

if __name__ == '__main__':
    update_targets()