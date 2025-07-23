from app import app, db
from models import User, PMSEntry
import os
from sqlalchemy import text

def migrate_db():
    with app.app_context():
        # Check if the database file exists
        if os.path.exists('instance/pms.db'):
            print("Database exists, adding new columns...")
            
            # Add new columns to PMSEntry table
            try:
                # Check if section column exists
                with db.engine.connect() as conn:
                    conn.execute(text("SELECT section FROM pms_entry LIMIT 1"))
                print("Section column already exists")
            except:
                print("Adding section column...")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE pms_entry ADD COLUMN section VARCHAR(50)"))
                    conn.commit()
            
            try:
                # Check if mtd_leads column exists
                with db.engine.connect() as conn:
                    conn.execute(text("SELECT mtd_leads FROM pms_entry LIMIT 1"))
                print("mtd_leads column already exists")
            except:
                print("Adding mtd_leads column...")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE pms_entry ADD COLUMN mtd_leads INTEGER DEFAULT 0"))
                    conn.commit()
            
            # Add other new columns
            new_columns = [
                "daily_leads_generated INTEGER DEFAULT 0",
                "daily_leads_contacted INTEGER DEFAULT 0",
                "daily_prospects INTEGER DEFAULT 0",
                "daily_suspects INTEGER DEFAULT 0",
                "applications_received INTEGER DEFAULT 0",
                "interviewed INTEGER DEFAULT 0",
                "on_hold INTEGER DEFAULT 0",
                "shortlisted INTEGER DEFAULT 0",
                "rejected INTEGER DEFAULT 0",
                "support_required TEXT"
            ]
            
            for column_def in new_columns:
                column_name = column_def.split()[0]
                try:
                    with db.engine.connect() as conn:
                        conn.execute(text(f"SELECT {column_name} FROM pms_entry LIMIT 1"))
                    print(f"{column_name} column already exists")
                except:
                    print(f"Adding {column_name} column...")
                    with db.engine.connect() as conn:
                        conn.execute(text(f"ALTER TABLE pms_entry ADD COLUMN {column_def}"))
                        conn.commit()
            
            print("Database migration completed successfully!")
        else:
            print("Database does not exist, creating tables...")
            db.create_all()
            print("Tables created successfully!")

if __name__ == "__main__":
    migrate_db()