"""
Test fixtures for pytest.
"""
import os
import pytest
import tempfile
from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models.user import User, Role
from app.services.security_service import init_roles


@pytest.fixture
def app():
    """Create application for testing."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
        JWT_SECRET_KEY='test-jwt-secret-key',
        SECRET_KEY='test-secret-key'
    )
    
    # Create the database and load test data
    with app.app_context():
        db.create_all()
        init_roles(db)
        yield app
        
        # Clean up
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def test_client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def test_db(app):
    """Create a test database."""
    with app.app_context():
        yield db


@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    user_role = Role.query.filter_by(name='user').first()
    user = User(
        username='testuser',
        email='test@example.com'
    )
    user.set_password('password123')
    user.roles.append(user_role)
    
    test_db.session.add(user)
    test_db.session.commit()
    
    return user


@pytest.fixture
def test_access_token(app, test_user):
    """Create an access token for the test user."""
    with app.app_context():
        access_token = create_access_token(identity=test_user.id)
        return access_token