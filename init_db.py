#!/usr/bin/env python3
"""
Database initialization script for Analisa.ai Social Media.
Creates tables and initializes basic data.

This script uses a direct approach to avoid circular imports.
"""
import os
import sys
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Load environment variables
load_dotenv()

def init_db():
    """Initialize the database with required tables and data."""
    # Create a minimal Flask app with just what we need
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://genbi:genbipassword@localhost:5432/socialmedia')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db = SQLAlchemy(app)
    
    # Define minimal models for initialization
    # Association table for User-Role relationship
    user_roles = db.Table('user_roles',
        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
        db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
    )
    
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(256), nullable=False)
        created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
        updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
        is_active = db.Column(db.Boolean, default=True)
        roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
        
        def set_password(self, password):
            from werkzeug.security import generate_password_hash
            self.password_hash = generate_password_hash(password)
    
    class Role(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(80), unique=True)
        description = db.Column(db.String(255))
    
    class Category(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50), nullable=False, unique=True)
        description = db.Column(db.String(255))
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Created database tables")
        
        # Initialize roles
        default_roles = ['admin', 'user', 'analyst']
        for role_name in default_roles:
            if not Role.query.filter_by(name=role_name).first():
                role = Role(name=role_name)
                db.session.add(role)
        db.session.commit()
        print("Initialized user roles")
        
        # Create categories if they don't exist
        categories = [
            {'name': 'Fashion', 'description': 'Fashion, clothing, and style'},
            {'name': 'Beauty', 'description': 'Beauty products and makeup'},
            {'name': 'Travel', 'description': 'Travel and tourism'},
            {'name': 'Fitness', 'description': 'Fitness and exercise'},
            {'name': 'Food', 'description': 'Food and cooking'},
            {'name': 'Technology', 'description': 'Technology and gadgets'},
            {'name': 'Gaming', 'description': 'Video games and gaming'},
            {'name': 'Entertainment', 'description': 'Entertainment and celebrity news'},
            {'name': 'Lifestyle', 'description': 'Lifestyle and daily life'},
            {'name': 'Business', 'description': 'Business and entrepreneurship'}
        ]
        
        for category_data in categories:
            if not Category.query.filter_by(name=category_data['name']).first():
                category = Category(**category_data)
                db.session.add(category)
        
        db.session.commit()
        print("Initialized categories")
        
        # Create an admin user if it doesn't exist and ADMIN_USERNAME is set
        admin_username = os.getenv('ADMIN_USERNAME')
        admin_password = os.getenv('ADMIN_PASSWORD')
        admin_email = os.getenv('ADMIN_EMAIL')
        
        if admin_username and admin_password and admin_email:
            if not User.query.filter_by(username=admin_username).first():
                admin_user = User(
                    username=admin_username,
                    email=admin_email
                )
                admin_user.set_password(admin_password)
                
                # Add admin role
                admin_role = Role.query.filter_by(name='admin').first()
                if admin_role:
                    admin_user.roles.append(admin_role)
                
                db.session.add(admin_user)
                db.session.commit()
                print(f"Created admin user: {admin_username}")
        
        print("Database initialization complete")

if __name__ == '__main__':
    try:
        init_db()
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        sys.exit(1)