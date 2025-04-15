# Visualization API Guide

This document provides information about the Visualization API endpoints that format analytics data for dashboard visualization.

## Endpoints

The API provides the following endpoints for visualization data:

### 1. Engagement Visualization

```
GET /api/analytics/visualization/engagement/{social_page_id}
```

Returns time series data and insights about engagement metrics for the specified social_page.

**Query Parameters:**
- `time_range`: Number of days to include in the visualization (default: 30)

**Response Format:**
```json
{
  "status": "success",
  "visualization": {
    "meta": {
      "social_page_id": 123,
      "social_page_name": "Example User",
      "platform": "instagram",
      "time_range": 30,
      "start_date": "2023-01-01",
      "end_date": "2023-01-30"
    },
    "time_series": [
      {
        "metric_name": "engagement_rate",
        "data_points": [
          { "date": "2023-01-01", "value": 3.5 },
          { "date": "2023-01-02", "value": 3.7 }
        ],
        "color": "#FF5733",
        "unit": "%"
      }
    ],
    "summary": {
      "avg_engagement_rate": 3.6,
      "max_engagement_rate": 4.2,
      "min_engagement_rate": 2.9
    },
    "trend": {
      "trend_direction": "up",
      "trend_percentage": 5.2,
      "trend_description": "Engagement is increasing",
      "compared_to_previous": "last_period"
    },
    "insights": [
      {
        "title": "Engagement Peak",
        "description": "Highest engagement on Thursdays",
        "type": "positive"
      }
    ],
    "best_performing_day": "Thursday",
    "worst_performing_day": "Monday"
  }
}
```

### 2. Reach Visualization

```
GET /api/analytics/visualization/reach/{social_page_id}
```

Returns time series data and insights about reach metrics for the specified social_page.

**Query Parameters:**
- `time_range`: Number of days to include in the visualization (default: 30)

**Response Format:**
Similar to the engagement visualization but with reach-specific metrics like impressions and story views.

### 3. Growth Visualization

```
GET /api/analytics/visualization/growth/{social_page_id}
```

Returns time series data and insights about growth metrics for the specified social_page.

**Query Parameters:**
- `time_range`: Number of days to include in the visualization (default: 30)

**Response Format:**
Similar to other visualizations but with growth-specific metrics like new followers and retention rates.

### 4. Score Visualization

```
GET /api/analytics/visualization/score/{social_page_id}
```

Returns time series data and insights about relevance score metrics for the specified social_page.

**Query Parameters:**
- `time_range`: Number of days to include in the visualization (default: 30)

**Response Format:**
Similar to other visualizations but with score-specific metrics including component scores.

### 5. Dashboard Overview

```
GET /api/analytics/visualization/dashboard/{social_page_id}
```

Returns a comprehensive dashboard overview with all metrics for the specified social_page.

**Response Format:**
```json
{
  "status": "success",
  "dashboard": {
    "meta": {
      "social_page_id": 123,
      "social_page_name": "Example User",
      "platform": "instagram"
    },
    "engagement": { ... },
    "reach": { ... },
    "growth": { ... },
    "score": { ... },
    "overall_health": "good",
    "recommended_actions": [
      "Post more consistently on Thursdays",
      "Respond to more comments to increase engagement"
    ]
  }
}
```

### 6. Compare social_pages

```
GET /api/analytics/visualization/compare?social_page_ids=1,2,3
```

Returns comparative data for multiple social_pages.

**Query Parameters:**
- `social_page_ids`: Comma-separated list of social_page IDs to compare

**Response Format:**
```json
{
  "status": "success",
  "comparison": {
    "metrics_compared": [
      "engagement_rate", 
      "followers_growth", 
      "relevance_score"
    ],
    "social_pages": [
      {
        "social_page_id": 1,
        "social_page_name": "social_page A",
        "platform": "instagram",
        "metrics": {
          "engagement_rate": 3.5,
          "followers_growth": 2.1,
          "relevance_score": 72.5
        }
      },
      {
        "social_page_id": 2,
        "social_page_name": "social_page B",
        "platform": "tiktok",
        "metrics": {
          "engagement_rate": 4.2,
          "followers_growth": 5.3,
          "relevance_score": 81.2
        }
      }
    ],
    "recommendations": [
      "social_page B has higher engagement and growth rates"
    ]
  }
}
```

## Error Handling

All visualization endpoints follow a standard error response format:

```json
{
  "status": "error",
  "message": "Error message description",
  "errors": "Detailed error information (optional)"
}
```

Common error scenarios:
- 404: social_page not found or no data available
- 400: Invalid request parameters
- 401: Unauthorized access
- 500: Server error processing the request

## Authentication

All visualization endpoints require authentication using a valid JWT token in the Authorization header:

```
Authorization: Bearer {your_jwt_token}
```