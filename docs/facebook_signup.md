# Facebook Signup/Login Integration for Analisa.ai

This document explains how to implement and use the Facebook signup feature in Analisa.ai. This feature allows users to register and log in using their Facebook accounts, streamlining the onboarding process.

## Features

- **One-click signup**: Users can create an account with their Facebook profile
- **Social login**: Returning users can log in with Facebook
- **Account linking**: Existing users can link their Facebook account
- **Profile data import**: Basic profile information is imported from Facebook

## Implementation Overview

The Facebook signup integration supports three main flows:

1. **Registration**: New users can create an account using Facebook
2. **Login**: Existing users can log in using Facebook
3. **Connection**: Logged-in users can connect their Facebook account

## Setup Requirements

### Facebook App Configuration

Ensure your Facebook App has the necessary permissions:

- `email` - To access the user's email address
- `public_profile` - To access basic profile information

### Backend Configuration

The following environment variables must be set:

```
FACEBOOK_CLIENT_ID=your_app_id
FACEBOOK_CLIENT_SECRET=your_app_secret
FACEBOOK_REDIRECT_URI=http://localhost:5000/api/auth/facebook/callback
```

## Registration Flow

### 1. Frontend Implementation

Add a "Sign up with Facebook" button to your registration page:

```html
<button (click)="signupWithFacebook()">
  <i class="fab fa-facebook-f"></i> Sign up with Facebook
</button>
```

```typescript
// Angular component method
signupWithFacebook() {
  // Redirect to the Facebook auth endpoint with 'register' action
  window.location.href = '/api/auth/facebook?action=register';
}
```

### 2. Backend Processing

The backend handles the OAuth flow and creates a new user account:

1. User is redirected to Facebook for authentication
2. Facebook redirects back with authorization code
3. Backend exchanges code for access token
4. Backend retrieves user's profile information
5. Backend creates a new user account
6. JWT tokens are generated for the new user
7. User is redirected to the welcome page with tokens

### 3. User Experience

From the user's perspective:

1. Click "Sign up with Facebook" button
2. Authorize Analisa.ai on Facebook
3. Get redirected back to Analisa.ai, already logged in
4. Complete any additional onboarding steps

## Login Flow

### 1. Frontend Implementation

Add a "Log in with Facebook" button to your login page:

```html
<button (click)="loginWithFacebook()">
  <i class="fab fa-facebook-f"></i> Log in with Facebook
</button>
```

```typescript
// Angular component method
loginWithFacebook() {
  // Redirect to the Facebook auth endpoint with 'login' action
  window.location.href = '/api/auth/facebook?action=login';
}
```

### 2. Backend Processing

The backend handles the OAuth flow and authenticates the user:

1. User is redirected to Facebook for authentication
2. Facebook redirects back with authorization code
3. Backend exchanges code for access token
4. Backend retrieves user's email
5. Backend looks up user by email
6. JWT tokens are generated for the user
7. User is redirected to the dashboard with tokens

### 3. User Experience

From the user's perspective:

1. Click "Log in with Facebook" button
2. Authorize Analisa.ai on Facebook (if not already authorized)
3. Get redirected back to Analisa.ai, already logged in

## Connection Flow

### 1. Frontend Implementation

Add a "Connect Facebook" button in the user settings:

```html
<button (click)="connectFacebook()">
  <i class="fab fa-facebook-f"></i> Connect Facebook Account
</button>
```

```typescript
// Angular component method
connectFacebook() {
  // Redirect to the Facebook auth endpoint with 'connect' action
  // Include the current user's ID
  window.location.href = `/api/auth/facebook?action=connect&user_id=${this.currentUser.id}`;
}
```

### 2. Backend Processing

The backend handles the OAuth flow and links the account:

1. User is redirected to Facebook for authentication
2. Facebook redirects back with authorization code
3. Backend exchanges code for access token
4. Backend stores the token with the user's account
5. User is redirected back to the settings page

### 3. User Experience

From the user's perspective:

1. Click "Connect Facebook" button
2. Authorize Analisa.ai on Facebook
3. Get redirected back to the settings page with success message

## Implementation Details

### Handling Facebook Callbacks

The endpoint `/api/auth/facebook/callback` handles all three flows:

```python
@bp.route('/facebook/callback')
def facebook_callback():
    # Get token from Facebook
    token = oauth.facebook.authorize_access_token()
    
    # Get user info (email, name, profile picture)
    resp = oauth.facebook.get('https://graph.facebook.com/me?fields=id,name,email,picture')
    facebook_user_info = resp.json()
    
    # Check action: register, login, or connect
    action = session.get('oauth_action')
    
    # Process based on action
    if action == 'register':
        # Create new user
        # ...
    elif action == 'login':
        # Find existing user
        # ...
    elif action == 'connect':
        # Link Facebook to existing account
        # ...
    
    # Redirect to appropriate page
    # ...
```

### User Creation

When creating a new user from Facebook data:

1. Email is taken from Facebook profile
2. Username is derived from the user's name (with uniqueness checks)
3. A random password is generated (user can set it later)
4. Profile picture URL is stored if available
5. Facebook ID is stored for future authentication

### Security Considerations

- Tokens are stored encrypted in the database
- Authentication state is maintained securely
- CSRF protection is implemented for all requests
- Facebook IDs are stored with unique constraints

## Testing

### Test Scenarios

1. **New user signup**: Verify a new user can register with Facebook
2. **Existing user login**: Verify an existing user can log in with Facebook
3. **Account connection**: Verify a user can connect their Facebook account
4. **Duplicate prevention**: Verify proper handling if a Facebook account is already linked
5. **Error handling**: Verify proper handling of denied permissions or failed requests

### Testing Accounts

For development, use Facebook Test Users:

1. Go to your Facebook App's Roles > Test Users
2. Create test users for development and testing
3. Use these test accounts to avoid using real Facebook accounts

## Troubleshooting

### Common Issues

1. **"Facebook account already connected"**: A different user has already connected this Facebook account.
2. **"Email already associated with an account"**: A user with this email already exists but isn't connected to Facebook.
3. **"Missing email permission"**: The user didn't grant email permission during Facebook OAuth.

### Debugging

- Check session storage for proper state maintenance
- Verify tokens are being correctly exchanged and stored
- Confirm redirect URIs match exactly in all configurations

## API Reference

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/api/auth/facebook` | GET | Initiate Facebook OAuth | `action`: 'register', 'login', or 'connect'<br>`user_id`: (optional) Current user ID for 'connect' action |
| `/api/auth/facebook/callback` | GET | Handle OAuth callback | (Automatically handles based on session state) |