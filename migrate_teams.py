from app import app, db
from models import User, Team, PMSEntry
import sqlite3
import os

def migrate_teams():
    with app.app_context():
        # Create teams table if it doesn't exist
        db.create_all()
        
        # Create teams
        teams = [
            {"name": "TND", "poc_name": "Smriti Panigrahi", "members": ["Kanak Bansal", "Alishala Sai Suhitha", "Mubashshira Qureshi"]},
            {"name": "COLLEGE COLLAB", "poc_name": "Priya Gava", "members": ["Shivani Mewada", "Shruti Malviya", "Taniya Soni"]},
            {"name": "COMPANY COLLAB", "poc_name": "Ishvpreet Kaur", "members": ["Riya Kapoor", "Bavleen Kaur Bhandari", "Gourav"]},
            {"name": "SCHOOL COLLAB", "poc_name": "Yatharth Sharma", "members": ["Ipshita Guha", "Namrata Kumari", "Harman Choudhary"]},
            {"name": "RECRUITMENT", "poc_name": "Nidhi Singh", "members": ["Anshika Srivastava", "Sagar Suman", "Maninder Singh"]}
        ]
        
        # Create teams and assign PoCs and members
        for team_data in teams:
            # Check if team already exists
            team = Team.query.filter_by(name=team_data["name"]).first()
            if not team:
                team = Team(name=team_data["name"])
                db.session.add(team)
                db.session.commit()
            
            # Find PoC
            poc = User.query.filter_by(name=team_data["poc_name"]).first()
            if poc:
                poc.is_poc = True
                poc.team_id = team.id
                team.poc_id = poc.id
                
                # Set targets
                poc.target = 50
                team.target = 150
                
                db.session.commit()
                print(f"Set {poc.name} as PoC for {team.name}")
            
            # Assign members
            for member_name in team_data["members"]:
                member = User.query.filter_by(name=member_name).first()
                if member:
                    member.team_id = team.id
                    member.target = 30
                    db.session.commit()
                    print(f"Added {member.name} to {team.name}")
        
        print("Team migration completed successfully!")

if __name__ == "__main__":
    migrate_teams()