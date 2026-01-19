# Backend API Documentation

## Overview
The backend provides a RESTful API to access static GTFS data (stops, routes, trips) and ingest user evidence for real-time inference.

**Base URL**: `http://localhost:8000/api`

---

## 1. Stops & Routes (GTFS)

### Get Nearby Stops
Returns stops sorted by distance to the user's location.
- **URL**: `/gtfs/stops/?dist=500&point=lon,lat`
- **Method**: `GET`
- **Params**:
    - `dist`: Search radius in meters (optional, default might depend on backend config but good to specify).
    - `point`: `longitude,latitude` (e.g., `72.8777,19.0760`)
- **Response**: List of stops with `stop_id`, `name`, and `geometry`.

### Search Stops
Search for a stop by name or ID.
- **URL**: `/gtfs/stops/?search=query`
- **Method**: `GET`
- **Params**:
    - `search`: Partial name or stop ID.
- **Response**: List of matching stops.

### Get Upcoming Trips at a Stop
Returns the schedule for a specific stop—trips arriving after the current time (or specified time).
- **URL**: `/gtfs/stops/{stop_id}/upcoming/`
- **Method**: `GET`
- **Params**:
    - `time`: `HH:MM:SS` (optional, defaults to server time `now`)
- **Response**:
    ```json
    [
      {
        "trip": { ...trip_metadata... },
        "arrival_time": "10:30:00",
        "departure_time": "10:30:30",
        "stop_sequence": 12
      },
      ...
    ]
    ```

### Get Trip Details
Returns detailed info about a single scheduled trip, including its full path of stops.
- **URL**: `/gtfs/trips/{trip_id}/`
- **Method**: `GET`
- **Response**:
    ```json
    {
      "trip_id": "...",
      "route": { ... },
      "stop_times": [
        { "stop_id": "...", "stop_name": "...", "arrival_time": "...", ... },
        ...
      ]
    }
    ```

---

## 2. Real-Time Data (Inference Layer) (Coming Soon)
*Using `realtime` app.*

### Get Active Trips
- **URL**: `/realtime/active-trips/`
- **Method**: `GET`
- **Response**: List of trips currently inferred to be active based on schedule + delays.

---

## 3. User Evidence (Input Layer)
*Using `evidence` app.*

### Submit Observation
Frontend submits user location/status to help backend infer bus positions.
- **URL**: `/evidence/observations/`
- **Method**: `POST`
- **Body**:
    ```json
    {
      "lat": 19.01,
      "lon": 72.85,
      "accuracy": 15.0,
      "trip_id": "optional_if_known"
    }
    ```

---

## Philosophy & Future Features
**We treat GTFS as a baseline.**
Real-world operations often deviate from the schedule. Our system is designed to layer **User Evidence** on top of the static schedule to correct it.

**Future Capabilities (Not yet implemented):**
- **User Location & Prompts**:
    - We plan to ask users for input (e.g., "Are you on the bus?" or "Is the bus here?").
    - The API will eventually support querying for "pending questions" for a user.
- **Confidence Scores**:
    - We will assign confidence levels to trip positions (e.g., "Verified by User" vs. "Scheduled").
- **Gamification**:
    - Potential for leaderboards or rewards for high-quality evidence.
