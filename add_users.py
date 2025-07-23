from app import app, db
from models import User

# List of intern names to add
interns = [
    "Smriti Panigrahi",
    "Kanak Bansal",
    "Alishala Sai Suhitha",
    "Mubashshira Qureshi",
    "Priya Gava",
    "Shivani Mewada",
    "Shruti Malviya",
    "Taniya Soni",
    "Ishvpreet Kaur",
    "Riya Kapoor",
    "Bavleen Kaur Bhandari",
    "Gourav",
    "Yatharth Sharma",
    "Ipshita Guha",
    "Namrata Kumari",
    "Harman Choudhary",
    "Nidhi Singh",
    "Anshika Srivastava",
    "Sagar Suman",
    "Maninder Singh",
    "Patel Sweta Vijaybhai",
    "Kajal Kumari",
    "Amrita Kumari",
    "Charu Pant",
    "Anjali Kumari Thakur",
    "Shreyansh Pandey",
    "Mohit Pathania",
    "Kishan Singh",
    "Ayush Chauhan",
    "Gaurav Kumar",
    "Rahul Singh",
    "Asad Zafar",
    "Damini Kumari",
    "Mayank Pratap Singh",
    "Sania Parween",
    "Shivam",
    "Harshita Singh",
    "Suhani Sahu",
    "Paridhi Chouhan",
    "Anshika Pandey"
]

def add_interns():
    with app.app_context():
        # Add each intern to the database
        for name in interns:
            # Use full name as username
            username = name
            
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                print(f"User {username} already exists, skipping...")
                continue
            
            # Create new user
            user = User(
                username=username,
                name=name,
                role='intern'
            )
            
            # Set default password (first name lowercase)
            first_name = name.split()[0].lower()
            user.set_password(first_name)
            
            # Add to database
            db.session.add(user)
            print(f"Added user: {name} (username: {username}, password: {first_name})")
        
        # Commit changes
        db.session.commit()
        print(f"Added {len(interns)} interns to the database")

if __name__ == "__main__":
    add_interns()