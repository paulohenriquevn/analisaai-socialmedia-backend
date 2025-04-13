# Analisa.ai Social Media - Backend

Backend API for Analisa.ai Social Media, a platform for analyzing social media influencers using AI.

## Features

- User authentication with JWT
- Social media integration with Instagram, Facebook, and TikTok
- Influencer data collection and analysis
- Analytics and metrics calculation
- Search and discovery features
- API for frontend integration

## Tech Stack

- Python 3.8+
- Flask 3.1.0
- SQLAlchemy ORM
- PostgreSQL
- JWT Authentication
- OAuth 2.0 Integration
- NumPy and Pandas for analytics

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- Developer accounts for social media platforms (Instagram, Facebook, TikTok)

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/analisaai-socialmedia-backend.git
cd analisaai-socialmedia-backend
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env file with your configuration
```

5. Set up the database
```bash
# Create PostgreSQL database
python setup_db.py
# OR manually: createdb analisaai

# Initialize the database with tables and initial data
python init_db.py

# Alternative (if the above doesn't work due to circular imports):
export FLASK_APP=run.py
flask init-db
```

### Configuration

1. Set up OAuth credentials for social media platforms:
   - Instagram: Create an app in the Facebook Developer Portal
   - Facebook: Create an app in the Facebook Developer Portal
   - TikTok: Create an app in the TikTok Developer Portal

2. Add the OAuth credentials to your `.env` file

## Running the Application

Start the development server:
```bash
python run.py
```

The API will be available at http://localhost:5000

## API Documentation

### Authentication Endpoints

- POST `/api/auth/register` - Register a new user
- POST `/api/auth/login` - User login
- POST `/api/auth/refresh` - Refresh JWT token
- GET `/api/auth/profile` - Get user profile

### Social Media OAuth Endpoints

- GET `/api/auth/instagram` - Initiate Instagram OAuth flow
- GET `/api/auth/facebook` - Initiate Facebook OAuth flow
- GET `/api/auth/tiktok` - Initiate TikTok OAuth flow

### Influencer Endpoints

- GET `/api/influencers` - List influencers
- GET `/api/influencers/:id` - Get influencer details
- POST `/api/influencers/lookup` - Look up influencer by username

### Analytics Endpoints

- GET `/api/analytics/influencer/:id/growth` - Get influencer growth metrics
- GET `/api/analytics/benchmarks` - Get platform benchmarks
- GET `/api/analytics/recommendations` - Get influencer recommendations

### Search Endpoints

- GET `/api/search/influencers` - Search for influencers
- GET `/api/categories` - Get influencer categories

## Development

### Project Structure

```
analisaai-socialmedia-backend/
├── app/
│   ├── __init__.py         # App initialization
│   ├── models.py           # Database models
│   ├── views.py            # API routes and controllers
│   ├── services/           # Business logic services
│   │   ├── __init__.py
│   │   ├── oauth_service.py       # OAuth integrations
│   │   ├── security_service.py    # Authentication and security
│   │   ├── social_media_service.py # Social media API integrations
│   │   └── analytics_service.py   # Analytics and metrics calculation
│   └── tests/              # Unit tests
├── run.py                  # Application entry point
├── requirements.txt        # Dependencies
└── .env.example            # Environment variables example
```

## License

MIT