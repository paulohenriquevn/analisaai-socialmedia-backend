# Social Media Integration Guide for Analisa.ai

This document provides a comprehensive overview of social media integrations in the Analisa.ai platform, highlighting how to use Facebook authentication and other platform integrations.

## Supported Platforms

The Analisa.ai platform currently supports these social media platforms:

- Facebook
- Instagram (via Facebook Graph API)
- TikTok

Each platform has its own authentication flow, API limitations, and data capabilities.

## General Authentication Flow

All social media integrations follow a similar pattern:

1. **User Authentication**: The user must be logged into Analisa.ai
2. **Platform Connection**: The user initiates a connection to a social media platform
3. **Authorization**: The user grants permissions to Analisa.ai on the platform
4. **Token Storage**: Access tokens are securely stored for future API calls
5. **Data Access**: Analisa.ai can now access authorized data from the platform

## Facebook Integration

[Detailed Facebook integration guide](facebook_integration.md)

### Quick Start

To connect a Facebook account:

1. Ensure the user is logged in to Analisa.ai
2. Direct the user to `/api/auth/facebook`
3. After authorization, the user is redirected back to the application
4. Verify the connection at `/api/users/me/connected-accounts`

### Usage Example

```javascript
// Frontend authentication flow
function connectFacebook() {
  // Step 1: Check if user is authenticated in Analisa.ai
  if (!isAuthenticated()) {
    return redirectToLogin();
  }
  
  // Step 2: Redirect to Facebook OAuth endpoint
  window.location.href = '/api/auth/facebook';
}

// After redirect back to the application
function handleAuthCallback() {
  // Check connected accounts
  fetch('/api/users/me/connected-accounts', {
    headers: {
      'Authorization': `Bearer ${userToken}`
    }
  })
  .then(response => response.json())
  .then(data => {
    // Display connected accounts to user
    console.log('Connected accounts:', data.connected_accounts);
  });
}
```

### Code Implementation

```python
# Backend route handler (Flask)
@main.route('/api/auth/facebook')
@jwt_required()
def facebook_auth():
    """Initiate Facebook OAuth flow."""
    user_id = get_jwt_identity()
    session['user_id'] = user_id
    redirect_uri = url_for('main.facebook_callback', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)
```

## Security Considerations

### Token Storage

All social media access tokens are:

1. **Encrypted** before storage using Fernet symmetric encryption
2. **Stored** in the database with user association
3. **Never** exposed to frontend clients
4. **Automatically** refreshed when needed

### Code Example

```python
# Token encryption (from security_service.py)
def encrypt_token(token):
    """Encrypts a token for secure storage."""
    return cipher_suite.encrypt(token.encode()).decode()

# Saving tokens securely (from oauth_service.py)
def save_token(user_id, platform, token_data):
    # Encrypt sensitive token data
    encrypted_access_token = encrypt_token(token_data['access_token'])
    
    # Store in database
    # ...
```

## Best Practices

1. **Permission Scope**: Request only the minimum permissions needed
2. **Error Handling**: Implement robust error handling for API failures
3. **Rate Limiting**: Respect platform rate limits to avoid throttling
4. **Token Refresh**: Implement proper token refresh mechanisms
5. **User Feedback**: Provide clear feedback on connection status

## Troubleshooting

Common issues users may encounter:

1. **"Account not connected"**: User needs to reconnect their social media account
2. **"Insufficient permissions"**: The application needs additional permissions
3. **"Rate limit exceeded"**: Too many requests to the social platform API
4. **"Token expired"**: Access token has expired and couldn't be refreshed

## API References

| API Documentation | URL |
|-------------------|-----|
| Facebook Graph API | https://developers.facebook.com/docs/graph-api |
| Instagram Graph API | https://developers.facebook.com/docs/instagram-api |
| TikTok API | https://developers.tiktok.com/doc/login-kit-web |

## Additional Resources

- [Facebook Developer Portal](https://developers.facebook.com/)
- [TikTok for Developers](https://developers.tiktok.com/)
- [OAuth 2.0 Specification](https://oauth.net/2/)