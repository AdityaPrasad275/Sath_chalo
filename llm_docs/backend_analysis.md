# Backend State Report & Architecture Review

**Date**: Feb 09, 2026
**Status**: Core Logic Complete (Phases 0-3 Done) ✅

## 1. Executive Summary: Then vs. Now

When you wrote `problems.md`, the backend was a simple **Static GTFS Viewer**. It could list stops and trips but had no concept of "active" buses, user feedback, or deviations.

**Today, it is a Real-Time Inference Engine.**

| Feature | State in `problems.md` | State NOW |
| :--- | :--- | :--- |
| **GTFS Data** | Basic ingestion. Timezone/Direction missing. | **Robust**. Timezone-aware (`Agency`), `headed_to` inferred from schedule. |
| **Shape Data** | "shape_id is empty" | **Implemented**. `Shape` model, `shapes.txt` generation, full geometry support. |
| **Realtime** | Non-existent. | **ActiveTrips**. Tracking delay, position, and confidence. |
| **Evidence** | "Waiting/On Bus" only. No processing. | **Smart**. 8+ types, explicit trip linking, automatic delay calculation. |
| **Deviation** | "Bus took different route?" (Unsolved) | **Solved**. `is_deviation` flag calculated via spatial queries. |
| **History** | None. | **Aggregation**. `TripDelayHistory` tracks persistent delays. |

---

## 2. Architecture & Data Flow

How data moves through the system today:

### A. The Signal Loop (Real-Time)
1.  **User Observation**: "I am on Trip T_123 at Lat/Lon X,Y"
    -   API: `POST /api/evidence/observations/`
2.  **Validation**:
    -   System checks: "Is X,Y close to the shape of Trip T_123?"
    -   If > 200m away: Marks `is_deviation=True` (Deviation Alert).
    -   If < 50m: Marks valid.
3.  **Inference (ActiveTrip Update)**:
    -   **Delay**: User time vs. Schedule time = `delay_seconds`.
    -   **Confidence**: Increases score (0.0 → 1.0) based on vote count.
    -   **Position**: Updates `last_stop_sequence` based on location.
4.  **Frontend**:
    -   Polls `GET /api/realtime/active-trips/`
    -   Sees: "Trip T_123 is Active, +5min late, High Confidence".

### B. The Learning Loop (Historic)
1.  **Daily Aggregation** (`scheduler.sh`):
    -   Runs `aggregate_delays` command at 4 AM.
2.  **Pattern Extraction**:
    -   Computes average delay for every trip-route combo.
    -   Stores in `TripDelayHistory`.
3.  **Prediction**:
    -   When no live users are active, system looks up history.
    -   "Usually +8 min late on Mondays" -> Shows predicted ETA.

---

## 3. Addressing Your `problems.md` Questions

You asked specific questions at the start. Here are the answers based on what we built:

### Q1: "How to handle new GTFS data (BMTC, etc) and Timezones?"
**Solved**.
-   We added an `Agency` model with a `timezone` field.
-   We rewrote the time logic to handle "25:30:00" timestamps (trips extending past midnight) by storing them as `seconds_since_midnight`.
-   The system is now compliant with standard GTFS feeds.

### Q2: "Stop Direction / Towards?"
**Solved**.
-   We don't store "direction" on the Stop (which is ambiguous).
-   Instead, `Trip` models have a `headed_to` field (calculated from the last stop).
-   Frontend displays: "Route 500D → **Heading to Whitefield**".

### Q3: "What is shape_id?"
**Solved**.
-   It links a Trip to a `Shape` (LineString geometry).
-   We updated the generator to create this data.
-   We updated ingestion to store it.
-   **Utility**: This is what powers the "Off Route" detection you wanted.

### Q4/Q5: "Realtime Chaos vs Systemic Errors?"
**We chose both.**
-   **Realtime**: `ActiveTrip` handles "Bus is late right now".
-   **Systemic**: `TripDelayHistory` handles "Bus is always late".
-   **Chaos (Deviations)**: The new `is_deviation` logic detects when a bus physically leaves its path (e.g., "Bus took a shortcut").

---

## 4. API Surface (The "Contract")

The backend now exposes a powerful set of APIs:

### GTFS (Static)
-   `GET /api/gtfs/stops/` (List stops, search by name/loc)
-   `GET /api/gtfs/stops/{id}/upcoming/` (The "Arrival Board" - mixes Schedule + Realtime + History)
-   `GET /api/gtfs/trips/{id}/` (Full route details, stops, shape)

### Realtime (Dynamic)
-   `GET /api/realtime/active-trips/` (Global view of all moving buses)
-   `GET /api/realtime/active-trips/patterns/` (Analytics: "Which routes are failing?")

### Evidence (Input)
-   `POST /api/evidence/observations/` (The User Vote)
    -   Accepts `trip_id`, `lat/lon`, `type`.
    -   Returns `is_deviation` flag instantly.

---

## 5. What's Next?

The Backend is effectively "MVP Complete". The logic exists.
**Your focus should now shift entirely to the Frontend to visualize this power:**
1.  **Map**: Draw the `Shape` geometry (colored lines).
2.  **Bus Markers**: Place them along the shape based on `TripPosition`.
3.  **Alerts**: Show "Deviation Detected" or "Delayed" badges.
