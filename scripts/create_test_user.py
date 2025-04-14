"""
Script to create a test user for API testing.
"""
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app import create_app
from app.models import User, Role
from app.extensions import db

def main():
    """Create a test user if it doesn't exist."""
    app = create_app('development')
    
    with app.app_context():
        # Check if test user already exists
        test_user = User.query.filter_by(username='testuser').first()
        
        if test_user:
            print(f"Test user already exists: {test_user.username} (ID: {test_user.id})")
            print("You can use this user for testing with password: password123")
        else:
            # Create a test user
            print("Creating test user...")
            
            # Check if we need to create the user role
            user_role = Role.query.filter_by(name='user').first()
            if not user_role:
                print("Creating 'user' role...")
                user_role = Role(name='user', description='Regular user')
                db.session.add(user_role)
                db.session.commit()
            
            # Create the test user
            test_user = User(
                username='testuser',
                email='test@example.com'
            )
            test_user.set_password('password123')
            
            # Assign user role
            test_user.roles.append(user_role)
            
            # Save to database
            db.session.add(test_user)
            db.session.commit()
            
            print(f"Created test user: {test_user.username} (ID: {test_user.id})")
            print("You can use this user for testing with password: password123")

if __name__ == "__main__":
    main()