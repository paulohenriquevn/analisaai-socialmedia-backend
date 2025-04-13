# Facebook Authentication Integration Guide

This document provides detailed information on how to integrate and use Facebook OAuth authentication in the Analisa.ai Social Media platform.

## Overview

The Facebook integration in Analisa.ai allows users to:

- Authenticate with their Facebook account
- Connect their Facebook pages
- Access analytics for Facebook pages
- Import Facebook page insights

## Prerequisites

Before you can use Facebook integration, you need:

1. A valid Facebook Developer account
2. A registered Facebook App with the following permissions:
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_manage_insights`
3. Properly configured OAuth settings in your Facebook App

## Setting Up Facebook App

### 1. Create a Facebook App

1. Go to [Facebook for Developers](https://developers.facebook.com/)
2. Click "My Apps" → "Create App"
3. Choose "Business" as the app type
4. Complete the app creation form
5. In the app dashboard, add the "Facebook Login" product

### 2. Configure the Facebook Login Product

1. Go to your app dashboard → Products → Facebook Login → Settings
2. Add the following OAuth Redirect URIs:
   - `https://yourdomain.com/api/auth/facebook/callback` (Production)
   - `http://localhost:5000/api/auth/facebook/callback` (Development)
3. Save changes

### 3. Configure App Permissions

1. Go to App Review → Permissions and Features
2. Request the following permissions:
   - `pages_read_engagement` - To access page metrics
   - `instagram_basic` - To access basic Instagram account data
   - `instagram_manage_insights` - To access Instagram insights
3. Complete the review process with Facebook

### 4. Get App Credentials

From your app dashboard, note down:
- App ID (Client ID)
- App Secret (Client Secret)

## Configuration in Analisa.ai

Update your `.env` file with the Facebook credentials:

```
FACEBOOK_CLIENT_ID=your_app_id
FACEBOOK_CLIENT_SECRET=your_app_secret
FACEBOOK_REDIRECT_URI=http://localhost:5000/api/auth/facebook/callback
```

## Integration Flow

### Authentication Process

1. **Initiate Login**: Direct the user to the Facebook authentication endpoint:
   ```
   GET /api/auth/facebook
   ```
   
   This endpoint requires JWT authentication to link the Facebook account with the user's Analisa.ai account.

2. **User Consent**: User is redirected to Facebook, where they:
   - Log in (if not already logged in)
   - Grant permissions to your app
   - Select which Facebook Pages to grant access to

3. **Callback Processing**: After consent, Facebook redirects to:
   ```
   GET /api/auth/facebook/callback
   ```
   
   This endpoint:
   - Receives the Facebook authentication code
   - Exchanges it for access and refresh tokens
   - Securely stores the tokens for the user
   - Redirects the user back to the application's settings page

4. **Verify Connection**: The user can verify their connected accounts at:
   ```
   GET /api/users/me/connected-accounts
   ```

## Using the Facebook Integration

### Accessing Page Data

Once a user has connected their Facebook account, you can fetch data for their pages:

```javascript
// Frontend example (Angular)
this.http.get('/api/facebook/pages').subscribe(
  pages => {
    // Handle the list of connected pages
    console.log(pages);
  }
);
```

### Page Analytics

To get analytics for a specific Facebook page:

```javascript
// Frontend example (Angular)
this.http.get(`/api/facebook/pages/${pageId}/analytics`).subscribe(
  analytics => {
    // Handle the page analytics
    console.log(analytics);
  }
);
```

## Refresh Tokens & Long-lived Access

Facebook access tokens initially expire after a short period. The system automatically:

1. Exchanges the short-lived token for a long-lived token (60-day validity)
2. Stores the expiration date
3. Automatically refreshes tokens before they expire

## Troubleshooting

### Common Issues

1. **"App Not Setup"**: Your app is still in development mode. Either switch to live mode or add test users.

2. **Permission Denied**: Ensure your app has been approved for the requested permissions.

3. **Invalid Redirect URI**: Check that the redirect URI in your app settings exactly matches the one in your app configuration.

4. **Token Expired**: If you encounter token expiration issues, the user may need to reconnect their account.

### Debug Tools

- Use the [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/) to test API calls
- Check token validity with the [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)

## Security Considerations

- Facebook access tokens are stored encrypted in the database
- The system uses HTTPS for all communication with Facebook APIs
- Tokens are never exposed to frontend clients
- User permission can be revoked any time through Facebook or by disconnecting the account in Analisa.ai

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/facebook` | GET | Initiates Facebook OAuth flow |
| `/api/auth/facebook/callback` | GET | Handles OAuth callback |
| `/api/users/me/connected-accounts` | GET | Lists connected accounts |
| `/api/facebook/pages` | GET | Lists user's Facebook pages |
| `/api/facebook/pages/:id/analytics` | GET | Gets analytics for specific page |