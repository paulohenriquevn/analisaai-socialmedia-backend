"""
Script to list users from the database.
"""
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app import create_app
from app.models import User

def main():
    """List all users in the database."""
    app = create_app('development')
    
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("No users found in the database.")
            # Create a test user
            from app.models import Role
            from app.extensions import db
            
            print("Creating a test user...")
            test_user = User(
                username="testuser",
                email="test@example.com"
            )
            test_user.set_password("password123")
            
            # Assign default role
            default_role = Role.query.filter_by(name='user').first()
            if default_role:
                test_user.roles.append(default_role)
            else:
                # Create the role if it doesn't exist
                default_role = Role(name='user', description='Regular user')
                db.session.add(default_role)
                db.session.commit()
                test_user.roles.append(default_role)
            
            db.session.add(test_user)
            db.session.commit()
            print(f"Created user: {test_user.username} (password: password123)")
            users = [test_user]
        
        print("\nUsers in the database:")
        print("-" * 80)
        print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Roles':<20}")
        print("-" * 80)
        
        for user in users:
            roles = ", ".join([role.name for role in user.roles]) if hasattr(user, 'roles') else ""
            print(f"{user.id:<5} {user.username:<20} {user.email:<30} {roles:<20}")

if __name__ == "__main__":
    main()