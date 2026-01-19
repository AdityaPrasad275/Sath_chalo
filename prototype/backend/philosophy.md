# Vision

Build a transit backend that treats **GTFS as a prior, not truth**, and gradually improves accuracy by aggregating weak, noisy user evidence over time. The system does **not** aim for perfect real-time tracking. It aims to detect **persistent, repeatable deviations** from GTFS schedules and routes, and to provide increasingly reliable ETAs and stop behavior.

Key principles:

* GTFS is a *baseline belief*
* Reality is noisy and uncertain
* Users provide *weak evidence*, not facts
* The system aggregates evidence statistically
* Outputs are derived, not stored

---

# Core Mental Model

* There is no mutable "bus" object
* A running bus is modeled as an **active trip instance**
* ETAs are **computed**, not stored
* Confidence comes from **mass of observations**, not individual reports

---

# High-Level Architecture

The backend is split conceptually into three layers:

1. **Static GTFS Layer** (mostly read-only)

   * Ingested from GTFS feeds
   * Updated only via batch processes

2. **Real-Time Inference Layer** (volatile)

   * Tracks which trips are active today
   * Maintains delay estimates and coarse position

3. **Evidence Layer** (append-only)

   * Stores user observations
   * Never directly mutates GTFS

---

# Core Data Model (Postgres + PostGIS)

## Stops

Represents physical boarding locations.

```
stops(
  stop_id PK,
  name,
  lat,
  lon,
  geom GEOGRAPHY(Point),
  active BOOLEAN
)
```

Notes:

* Opposite directions are **separate stops** (even if colocated)
* Spatial index used for nearest-stop queries

---

## Routes

Logical bus lines (e.g. 500D).

```
routes(
  route_id PK,
  short_name,
  long_name,
  agency_id
)
```

---

## Trips

A **trip** is one scheduled run of a route in a specific direction and time.

```
trips(
  trip_id PK,
  route_id FK,
  direction_id,
  shape_id,
  service_id
)
```

---

## Stop Times (GTFS prior)

Defines the scheduled relationship between trips and stops.

```
stop_times(
  trip_id FK,
  stop_id FK,
  stop_sequence,
  arrival_time,
  departure_time,
  PRIMARY KEY (trip_id, stop_sequence)
)
```

This is the **skeleton** for all ETAs.

---

# Real-Time Inference Layer

## Active Trips

Tracks which trips are currently running and how delayed they are.

```
active_trips(
  trip_id PK,
  started_at,
  last_observed_at,
  delay_seconds,
  confidence_score
)
```

* `delay_seconds` is a **global offset** applied to all downstream stops
* No per-stop ETAs are stored

---

## Trip Position (1D motion)

Tracks coarse progress along a trip.

```
trip_position(
  trip_id PK,
  last_stop_sequence,
  progress_ratio,
  observed_at
)
```

* Motion is modeled **1-dimensionally** between stops
* Lat/lon is derived from shapes if needed

---

# Evidence Layer (Forward-Compatible)

User input is modeled as **observations**, not updates.

```
observations(
  observation_id PK,
  user_id,
  timestamp,
  type,
  stop_id NULL,
  lat NULL,
  lon NULL
)
```

Each observation is probabilistically associated with multiple trips:

```
observation_trip_likelihoods(
  observation_id,
  trip_id,
  probability
)
```

This enables:

* Uncertainty
* Noise tolerance
* Aggregation across users

---

# Query Flows

## Nearest Stops (`/`)

* Spatial query on `stops.geom`
* Order by distance
* Limit to top N

## Stop Page (`/stop/:id`)

1. Find trips that include this stop (`stop_times`)
2. Filter to active trips today
3. Compute ETA:

```
ETA = scheduled_arrival + delay_seconds
```

4. Sort by ETA
5. Return top upcoming trips

No denormalized stop→bus lists are stored.

---

## Trip Timeline (`/trip/:id`)

1. Load ordered `stop_times` for the trip
2. Join with `active_trips` and `trip_position`
3. Backend computes ETAs on the fly
4. Frontend marks passed/current/future stops

---

# Why This Design Works

* Avoids duplicated state
* Avoids mass updates
* Scales to multiple users naturally
* Treats uncertainty explicitly
* Allows gradual improvement without breaking correctness

---

# Forward Compatibility: User Feedback & Learning

The system is intentionally designed to support future enhancements:

* Probabilistic matching of user observations to trips
* Aggregation of repeated deviations
* Detection of:

  * Chronic delays
  * Skipped stops
  * Route deviations
* Offline batch updates to GTFS-derived beliefs

Crucially:

* GTFS is never mutated in real time
* All learning is reversible and statistical

---

# Summary

This backend is not a tracker. It is a **belief system**.

* GTFS provides structure
* Users provide weak signals
* The backend aggregates patterns
* Accuracy improves quietly over time

The result is a system that is robust to noise, respectful of users, and realistic about the chaos of real-world transit.
