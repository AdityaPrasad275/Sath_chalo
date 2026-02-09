# Deviation Detection System Design ("The Scout")

## Goal
To detect when a bus is physically far from its scheduled path, implying a **detour**, **rerouting**, or **user error**.

## Core Philosophy
We treat every observation as a vote.
- On-route votes reinforce the "Scheduled Shape".
- Off-route votes, **if clustered**, suggest a "New Shape".
- Scattered off-route votes suggest "Noise".

## 1. Database Schema Changes

### `Observation` Model Enrichment
We need to store the result of our spatial checks on every observation.

```python
class Observation(models.Model):
    # ... existing fields ...
    
    # NEW FIELDS
    distance_from_trip = models.FloatField(null=True, help_text="Meters from the linked trip's shape")
    is_deviation = models.BooleanField(default=False, help_text="True if distance > threshold")
    
    # For "I don't know which bus I'm on" or "Wrong Bus" detection
    nearest_trip = models.ForeignKey(Trip, null=True, related_name='nearby_observations')
    nearest_trip_distance = models.FloatField(null=True)
```

## 2. The Logic Flow

### Scenario A: User specifies Trip ID (Explicit) - **MVP FOCUS**
*User says: "I am on Bus 500D (T_123)"*

1.  **Calculate Distance**: Compute `d = distance(user_point, trip.shape)`.
2.  **Classify**:
    -   `d < 50m`: **ON TRACK**. High confidence observation.
    -   `50m < d < 200m`: **GPS DRIFT / MINOR**. Flag as weak match.
    -   `d > 200m`: **DEVIATION**.
        -   Mark `is_deviation = True`.
        -   **Action**: Log it. (Optional: Warn user in UI).

### Scenario B: User provides NO Trip ID (Implicit/Search) - **DEFERRED TO V2**
*(Complexity Warning: Requires reliable session IDs and continuous background location, which is hard in PWA MVP)*

> **Decision**: We will NOT implement "guess the trip" logic in V1. If a user doesn't select a trip, we just store the observation as a "orphan" for later analysis, but we don't try to auto-assign it to a trip in real-time.

## 3. Accumulation & "Suggesting New Shape"

One user being 500m away might be sitting in a cafe while mistakenly clicking "On Bus".
**Three users** being 500m away along the *same vector* is a **Reroute**.

### Deviation Clustering Algorithm (Future V2)
1.  Fetch all `is_deviation=True` observations for Route R in last hour.
2.  Cluster them spatially (DBSCAN or simple grid).
3.  If Cluster Size > 3 and Linear (forms a line):
    -   **Promote to "Known Detour"**.
    -   create `TemporaryShape` geometry.

## 4. Implementation Plan (Revised for MVP)

### Step 1: Update Observation Model
- Add `distance_from_trip` and `is_deviation`.

### Step 2: Observation Processing Service
- In `evidence/views.py`:
    - On `perform_create`:
        - **Only if `trip` is provided**:
            - Run `get_distance_on_shape`.
            - Update fields.
            - If `distance > threshold`: Log warning / Flag observation.
        - If `trip` is missing: Do nothing (just save raw lat/lon).

## Use Cases Covered
1.  **The "Velankani Drive" Shortcut**: Bus takes a parallel road. Distance ~800m. System flags `is_deviation=True`.
2.  **The "Forgot to get off"**: User is still reporting "On Bus" but bus has reached terminal and user is walking home. Distance grows. System detects deviation.
3.  **The "Wrong Direction"**: User selects "Going North" but is moving "South". (Requires vector math, out of scope for V1 but Shape distance helps if routes are separated).

## Constraints
- **Performance**: PostGIS `ST_Distance` is fast but doing it for *all* active trips on *every* observation (Implicit Case) requires spatial indexing.
- **GPS Accuracy**: Phones are noisy. Thresholds must be generous (50m, not 5m).

