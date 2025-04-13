# Facebook Login Integration Guide for Analisa.ai

This guide provides step-by-step instructions for integrating and using Facebook Login in the Analisa.ai Social Media platform, both for developers implementing the feature and for end-users connecting their accounts.

## For Developers

### Setting Up Facebook Authentication

#### 1. Register a Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "My Apps" → "Create App"
3. Select "Business" as the app type
4. Complete the app creation form with your details
5. Navigate to the app dashboard

#### 2. Configure Facebook Login Product

1. In the app dashboard, click "Add Product"
2. Select "Facebook Login" 
3. In the settings page for Facebook Login:
   - Set the Valid OAuth Redirect URIs to:
     ```
     https://yourdomain.com/api/auth/facebook/callback
     http://localhost:5000/api/auth/facebook/callback
     ```
   - Under "Login with the JavaScript SDK", set "Allow Login from Webview" to Yes
   - Under "Enforce HTTPS" select Yes
   - Save changes

#### 3. Configure App Permissions

1. Navigate to "App Review" → "Permissions and Features"
2. Request the following permissions:
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_manage_insights`
3. Provide appropriate use cases and testing instructions

#### 4. Update Environment Variables

Add these variables to your `.env` file:

```
FACEBOOK_CLIENT_ID=your_app_id
FACEBOOK_CLIENT_SECRET=your_app_secret
FACEBOOK_REDIRECT_URI=http://localhost:5000/api/auth/facebook/callback
```

#### 5. Configure OAuth Client

The OAuth client is already configured in the backend:

```python
# From app/services/oauth_service.py
oauth.register(
    name='facebook',
    client_id=app.config['FACEBOOK_CLIENT_ID'],
    client_secret=app.config['FACEBOOK_CLIENT_SECRET'],
    authorize_url='https://www.facebook.com/v16.0/dialog/oauth',
    access_token_url='https://graph.facebook.com/v16.0/oauth/access_token',
    redirect_uri=app.config['FACEBOOK_REDIRECT_URI'],
    client_kwargs={'scope': 'pages_read_engagement,instagram_basic,instagram_manage_insights'},
)
```

### Implementing Frontend Components

Create a Facebook Login button component:

```typescript
// Angular component example
@Component({
  selector: 'app-facebook-login',
  template: `
    <button 
      class="facebook-btn" 
      (click)="connectFacebook()">
      <i class="fab fa-facebook-f"></i>
      Connect Facebook Account
    </button>
  `,
  styles: [`
    .facebook-btn {
      background-color: #4267B2;
      color: white;
      padding: 10px 15px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
  `]
})
export class FacebookLoginComponent {
  constructor(private authService: AuthService) {}
  
  connectFacebook() {
    // Check if user is logged in
    if (!this.authService.isAuthenticated()) {
      return this.authService.redirectToLogin();
    }
    
    // Redirect to backend endpoint
    window.location.href = '/api/auth/facebook';
  }
}
```

## For End Users

### Connecting a Facebook Account to Analisa.ai

#### Step 1: Log in to Analisa.ai

Ensure you're logged in to your Analisa.ai account before attempting to connect Facebook.

#### Step 2: Navigate to Account Settings

1. Click on your profile picture in the top-right corner
2. Select "Settings" from the dropdown menu
3. Go to the "Connected Accounts" section

#### Step 3: Connect Facebook Account

1. Click the "Connect Facebook" button
2. A new window/tab will open with Facebook's authentication page
3. Log in to your Facebook account if not already logged in
4. Review the permissions requested by Analisa.ai
5. Click "Continue" to grant access

![Facebook Permission Dialog](https://example.com/images/facebook-permissions.png)

#### Step 4: Select Facebook Pages (Optional)

If you manage Facebook Pages:

1. Select which Pages you want to connect to Analisa.ai
2. You can select all or individual Pages
3. Click "Next" to continue

#### Step 5: Verify Connection

After successful connection:

1. You'll be redirected back to Analisa.ai
2. The Connected Accounts section will show Facebook as connected
3. You can now access Facebook analytics in your Analisa.ai dashboard

### Managing Facebook Connection

#### Viewing Connected Pages

1. Go to the "Facebook Insights" section in your dashboard
2. You'll see all connected Facebook Pages
3. Select a Page to view detailed analytics

#### Disconnecting Facebook

To disconnect your Facebook account:

1. Go to Settings → Connected Accounts
2. Find Facebook in the list of connected platforms
3. Click "Disconnect"
4. Confirm your choice

Alternatively, you can revoke access from Facebook:

1. Go to Facebook → Settings → Apps and Websites
2. Find Analisa.ai in the list
3. Click "Remove" and confirm

## Troubleshooting

### Common Issues

1. **Login fails with "Invalid redirect_uri"**:
   - Ensure the redirect URI in your Facebook app matches exactly with the one in your application

2. **"The app is still in development mode"**:
   - Either add yourself as a test user or switch the app to live mode

3. **Limited data access**:
   - Check if all required permissions have been approved
   - Ensure you've selected Pages to manage during the connection process

4. **"This app does not have access to your pages"**:
   - Reconnect your Facebook account and explicitly select Pages to grant access

### Support Resources

If you encounter any issues:

- Visit the [Facebook Developer Documentation](https://developers.facebook.com/docs/)
- Contact support at support@analisaai.com
- Check [Facebook Login Error Reference](https://developers.facebook.com/docs/facebook-login/web/troubleshooting)

## Privacy Information

When connecting Facebook to Analisa.ai:

- We only access the data you explicitly grant permission for
- Your Facebook credentials are never stored by Analisa.ai
- You can disconnect your account at any time
- Disconnecting will stop all data collection from Facebook

## Best Practices

- Connect Facebook from a desktop browser for the best experience
- Use the same email address for Facebook and Analisa.ai if possible
- Regularly review connected applications in your Facebook settings
- Keep your Facebook app updated with the latest security settings