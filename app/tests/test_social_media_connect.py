"""
Tests for social media connection endpoints.
"""
import pytest
import json
from unittest.mock import patch

from app.models.user import User


class TestSocialMediaConnect:
    """Test cases for social media connection endpoints."""
    
    @pytest.fixture
    def auth_headers(self, test_client, test_user):
        """Get auth headers for test user."""
        response = test_client.post(
            '/api/auth/login',
            json={
                'username': test_user.username,
                'password': 'password123'
            }
        )
        tokens = json.loads(response.data)['tokens']
        return {'Authorization': f'Bearer {tokens["access_token"]}'}
    
    def test_connect_social_media_success(self, test_client, auth_headers, test_user, test_db):
        """Test successful connection of social media account."""
        # Prepare test data
        data = {
            'platform': 'instagram',
            'external_id': '12345678',
            'username': '@testinfluencer'
        }
        
        # Call endpoint
        response = test_client.post(
            '/api/social-media/connect',
            json=data,
            headers=auth_headers
        )
        
        # Check response
        assert response.status_code == 201
        resp_data = json.loads(response.data)
        assert resp_data['platform'] == 'instagram'
        assert resp_data['external_id'] == '12345678'
        
        # Verify database update
        user = User.query.get(test_user.id)
        assert user.instagram_id == '12345678'
    
    def test_connect_invalid_platform(self, test_client, auth_headers):
        """Test connection with invalid platform."""
        data = {
            'platform': 'invalid_platform',
            'external_id': '12345678',
            'username': '@testinfluencer'
        }
        
        response = test_client.post(
            '/api/social-media/connect',
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert json.loads(response.data)['error'] == 'Plataforma não suportada'
    
    def test_connect_already_connected(self, test_client, auth_headers, test_user, test_db):
        """Test connecting a platform that's already connected."""
        # First, connect a platform
        test_user.instagram_id = '12345678'
        test_db.session.commit()
        
        # Try to connect again
        data = {
            'platform': 'instagram',
            'external_id': '87654321',
            'username': '@newname'
        }
        
        response = test_client.post(
            '/api/social-media/connect',
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 409
        assert json.loads(response.data)['error'] == 'Rede social já vinculada'
    
    def test_connect_unauthorized(self, test_client):
        """Test connection without authentication."""
        data = {
            'platform': 'instagram',
            'external_id': '12345678',
            'username': '@testinfluencer'
        }
        
        response = test_client.post(
            '/api/social-media/connect',
            json=data
        )
        
        assert response.status_code == 401