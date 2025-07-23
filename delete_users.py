from app import app, db
from models import User

def delete_interns():
    with app.app_context():
        # Delete all intern users except admin
        interns = User.query.filter_by(role='intern').all()
        for intern in interns:
            db.session.delete(intern)
        
        db.session.commit()
        print(f"Deleted {len(interns)} intern users")

if __name__ == "__main__":
    delete_interns()