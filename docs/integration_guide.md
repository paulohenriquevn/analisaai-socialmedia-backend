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

## Connection Methods

### Method 1: OAuth Flow (Recommended)

The most secure and user-friendly approach is to use the built-in OAuth flow:

1. Ensure the user is logged in to Analisa.ai
2. Direct the user to the appropriate endpoint:
   - Facebook: `/api/auth/facebook`
   - Instagram: `/api/auth/instagram`
   - TikTok: `/api/auth/tiktok`
3. After authorization, the user is redirected back to the application
4. Verify the connection at `/api/users/me/connected-accounts`

### Method 2: Manual Connection

For testing or when OAuth is not possible, you can connect accounts manually:

```
POST /api/social-media/connect
```

**Autenticação**: Bearer Token (JWT)

**Request Body**:
```json
{
  "platform": "instagram",
  "username": "@username"
}
```

Parameters:
- `platform`: Social media platform (instagram, facebook, tiktok)
- `username`: Username on the platform (can include @ or not)
- `external_id`: (Optional) External ID of the account. If not provided, the system will try to find it automatically.

**Response Example (201 Created)**:
```json
{
  "id": 123,
  "user_id": 456,
  "platform": "instagram",
  "external_id": "ig_1234567890abcdef",
  "username": "@username",
  "created_at": "2025-04-13T15:30:45Z"
}
```

**Possible Errors**:
- 400: Invalid data or unsupported platform
- 401: Not authenticated
- 404: User not found
- 409: Account already linked

## Automatic External ID Detection

When providing only the username, the system will:

1. Look for the account in the Analisa.ai database
2. If not found, try to fetch via the platform's API (when possible)
3. If unsuccessful, generate a consistent ID based on the username

This functionality simplifies integration, as the end user doesn't need to know the technical ID of their account.

## Usage Examples

### Connect Instagram

```bash
curl -X POST https://api.analisaai.com/api/social-media/connect \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "instagram",
    "username": "@my_instagram"
  }'
```

### Connect Facebook

```bash
curl -X POST https://api.analisaai.com/api/social-media/connect \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "facebook",
    "username": "my.facebook.page"
  }'
```

### Connect TikTok

```bash
curl -X POST https://api.analisaai.com/api/social-media/connect \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "tiktok",
    "username": "@my_tiktok"
  }'
```

## Security Considerations

### Token Storage

All social media access tokens are:

1. **Encrypted** before storage using Fernet symmetric encryption
2. **Stored** in the database with user association
3. **Never** exposed to frontend clients
4. **Automatically** refreshed when needed

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

## Social Media Post Management

The AnalisaAI platform now supports fetching and storing social media posts for influencers, which enables more accurate metrics calculation and historical data analysis.

### Automatic Post Collection

When an influencer profile is fetched via the API or manually updated, the system will:

1. Fetch the most recent posts (typically the last 5-25 posts, depending on the platform)
2. Store these posts in the database with engagement metrics
3. Use this data to calculate more accurate analytics metrics

### Post Fetching API Endpoints

#### Refresh Influencer Data (including posts)

Fetch fresh data for an influencer, including their recent posts:

```
POST /api/social-media/influencer/<influencer_id>/refresh
```

**Authentication**: Bearer Token (JWT)

**Request Body (optional)**:
```json
{
  "fetch_posts": true,
  "force_fetch_posts": false
}
```

Parameters:
- `fetch_posts`: Whether to fetch posts (default: true)
- `force_fetch_posts`: Force fetch posts even if we already have recent ones (default: false)

**Response Example (200 OK)**:
```json
{
  "status": "success",
  "message": "Successfully refreshed data for username",
  "influencer": {
    "id": 123,
    "username": "username",
    "platform": "instagram",
    "followers_count": 10000,
    "engagement_rate": 3.5,
    "posts_count": 547,
    "updated_at": "2025-04-14T12:30:45Z"
  },
  "posts": {
    "fetched": 5,
    "total_recent": 12
  }
}
```

#### Dedicated Post Fetching Endpoint

To explicitly fetch posts without updating the influencer profile:

```
POST /api/social-media/influencer/<influencer_id>/fetch-posts
```

**Authentication**: Bearer Token (JWT)

**Response Example (200 OK)**:
```json
{
  "status": "success",
  "message": "Successfully fetched posts for username",
  "posts_fetched": 5
}
```

### Batch Post Fetching Script

For bulk operations or scheduled post fetching, use the included script:

```bash
python scripts/fetch_influencer_posts.py [--platform instagram|tiktok|facebook] [--limit 10]
```

This script can be configured to run as a scheduled task (cron job) to keep the post data up-to-date.

### Benefits of Post Data Collection

Storing post data provides several advantages:

1. **More Accurate Metrics**: Engagement rates and other metrics are calculated from actual post data
2. **Historical Trends**: Track performance over time with consistent historical data
3. **Posting Time Analysis**: Determine optimal posting times based on engagement patterns
4. **Content Type Analysis**: Compare performance of different content types (image, video, etc.)
5. **Topic Analysis**: Identify topics and themes that resonate with the audience