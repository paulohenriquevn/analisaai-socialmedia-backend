#!/usr/bin/env python3
"""
Simple script to create the database for Analisa.ai Social Media.
This script doesn't rely on Flask app or ORM, just uses direct SQL commands.
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create the PostgreSQL database."""
    # Get database connection details from environment
    db_name = os.getenv('DB_NAME', 'socialmedia')
    db_user = os.getenv('DB_USER', 'genbi')
    db_password = os.getenv('DB_PASSWORD', 'genbipassword')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    
    # Connect to PostgreSQL server
    print(f"Connecting to PostgreSQL server at {db_host}:{db_port}...")
    try:
        conn = psycopg2.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database already exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"Database '{db_name}' created successfully!")
        else:
            print(f"Database '{db_name}' already exists.")
        
        cursor.close()
        conn.close()
        
        # Generate DATABASE_URL for .env file
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        # Update .env file if DATABASE_URL doesn't match
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            # Check if DATABASE_URL is in .env
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('DATABASE_URL='):
                    if line.strip() != f'DATABASE_URL={database_url}':
                        lines[i] = f'DATABASE_URL={database_url}\n'
                        updated = True
                    break
            else:
                # DATABASE_URL not found, add it
                lines.append(f'\nDATABASE_URL={database_url}\n')
                updated = True
            
            if updated:
                print(f"Updating DATABASE_URL in .env file...")
                with open(env_path, 'w') as f:
                    f.writelines(lines)
        
        return True
    
    except Exception as e:
        print(f"Error creating database: {str(e)}")
        return False

if __name__ == '__main__':
    if create_database():
        print("Database setup complete. Now run 'python init_db.py' to initialize tables and data.")
    else:
        sys.exit(1)