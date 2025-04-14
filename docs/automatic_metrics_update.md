# Automatic Metrics Update

This document explains how the automatic metrics update feature works in the AnalisaAI Social Media platform.

## Overview

The Automatic Metrics Update feature ensures that metrics and scores are recalculated whenever a user logs in or refreshes their authentication token, providing the most up-to-date analytics information without requiring manual updates.

## Functionality

### Login-Triggered Updates

When a user logs in:

1. The system fetches the most recently updated social media data for up to 5 influencers
2. For each influencer, the following metrics are calculated:
   - Engagement metrics (engagement rate, avg likes/comments, etc.)
   - Reach metrics (impressions, story views, etc.)
   - Growth metrics (new followers, retention rates, etc.)
   - Relevance scores (combined scoring from all metrics)
3. Updates are performed in the login flow but don't block the login response
4. If any part of the update fails, the login still succeeds, with errors logged for investigation

### Token Refresh Updates

When a user refreshes their authentication token:

1. The system identifies the oldest updated influencer
2. A background thread is spawned to calculate all metrics for this influencer
3. Token refresh is not blocked or delayed by the metrics calculation
4. Updates are performed asynchronously to ensure rapid token refresh response

## Implementation Details

### Login Flow

The login flow update is implemented in `/app/api/auth/routes/__init__.py` in the `/login` endpoint. It:

- Prioritizes older entries first (sorted by `updated_at`)
- Limits updates to 5 influencers per login to prevent long login times
- Handles errors for each influencer separately to ensure continued processing
- Updates profile data first, then calculates metrics based on the new data
- Follows a specific sequence for metric calculation:
  1. Engagement metrics (base metrics)
  2. Reach metrics
  3. Growth metrics
  4. Relevance score (depends on other metrics)

### Token Refresh Flow

The token refresh update is implemented in the `/refresh` endpoint and:

- Updates a single influencer to minimize server load
- Runs in a separate thread to avoid blocking the token refresh
- Ensures sequential calculation of metrics to maintain data consistency

## Error Handling

Both update processes include comprehensive error handling:

- Individual influencer failures don't stop the entire process
- Metrics calculation failures are logged but don't affect user experience
- Login and token refresh operations are never blocked by update failures

## Benefits

This automatic update approach provides several benefits:

1. **Fresh Data**: Users always see recent metrics without manual refreshes
2. **Efficient Updates**: Distributes the update load across user interactions
3. **Transparent Experience**: Updates happen in the background without user awareness
4. **Load Management**: Limits updates to maintain server performance
5. **Fault Tolerance**: Continues to function even when parts of the update fail

## Monitoring

To monitor the automatic updates:

- Check logs with the prefix "Starting automatic metrics update" or "Starting metrics update in background"
- Look for "Successfully calculated" log entries to confirm successful updates
- Review errors prefixed with "Error updating metrics" to troubleshoot issues