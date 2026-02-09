# Backend Analysis & Recommendations

## Executive Summary

Your backend is **solid but incomplete**. The GTFS foundation works well, but the **confidence layer** (the core innovation from your problem statement) is currently just a placeholder. The good news: your architecture is ready for it. The challenge: you need to decide what signals to capture and how to aggregate them.

---

## Current Architecture: What Actually Exists

### Three Django Apps

#### 1. **`gtfs` App** - Static Transit Graph ✅
**Purpose**: Ingest and serve GTFS data as a queryable baseline

**Models**:
- `Stop`: Physical bus stop with lat/lon (PostGIS Point geometry)
- `Route`: Logical bus line (e.g., "500D")
- `Trip`: One scheduled run of a route (has `headed_to` field for last stop)
- `StopTime`: Join table connecting trips to stops with scheduled times

**Key Implementation**:
- `ingest_gtfs` management command: Bulk loads GTFS CSVs into Postgres
- Calculates `headed_to` by finding the last stop in each trip's `stop_times`
- `shape_id` field exists but is **currently empty** (more on this later)

**API Endpoints**:
- `GET /api/gtfs/stops/` - List/search stops (supports spatial filtering via `DistanceToPointFilter`)
- `GET /api/gtfs/stops/{id}/upcoming/` - Returns trips arriving at this stop in the next ~2 hours
- `GET /api/gtfs/trips/{id}/` - Trip details with full stop timeline
- `GET /api/gtfs/routes/` - List routes

**✅ What Works**:
- GTFS ingestion is robust
- Spatial queries for "nearest stops" work
- Can compute "bus should be between stops X and Y at time T" from schedule

**⚠️ Gaps**:
- No "direction" or "towards" field on stops themselves (you identified this in `problems.md`)
- `shape_id` is ingested but not used (no shapes table, no route geometry)
- Timezone handling is broken (`TIME_ZONE = 'UTC'` in settings, but times are in Asia/Kolkata)

---

#### 2. **`realtime` App** - Inference Layer 🚧
**Purpose**: Track active trips and their positions

**Models**:
- `ActiveTrip`: Represents a trip currently running (links to `Trip`)
  - `delay_seconds`: Global offset to apply to all scheduled times
  - `confidence_score`: How certain we are (0.0 - not implemented)
- `TripPosition`: Coarse 1D position along trip route
  - `last_stop_sequence`: Which stop it passed most recently
  - `progress_ratio`: Float (0.0-1.0) representing progress to next stop

**API Endpoints**:
- `GET /api/realtime/active-trips/` - List active trips with positions

**✅ What Works**:
- Clean 1D motion model (no trying to track lat/lon directly)
- Delay modeled as a single offset (simple, reasonable)

**❌ What's Missing (Critical)**:
- **No logic to CREATE ActiveTrip records**
  - Who decides when a trip becomes "active"?
  - When does it expire?
- **No logic to UPDATE positions**
  - Nothing populates `last_stop_sequence` or `progress_ratio`
  - Nothing updates `delay_seconds`
- **Confidence score is always 0.0**
  - No scoring logic exists

**Current State**: Models exist, but they're **empty shells**. This is where your core problem lives.

---

#### 3. **`evidence` App** - User Feedback Layer 🪹
**Purpose**: Capture user observations to drive the inference layer

**Models**:
- `Observation`: Single user signal
  - `type`: `WAITING_AT_STOP`, `ON_BUS`, `BUS_PASSED`
  - `user_id`: Session/user identifier
  - `stop`: Optional FK to Stop
  - `lat`/`lon`: Optional location

**API Endpoints**:
- `POST /api/evidence/observations/` - Submit observation
- `GET /api/evidence/observations/` - List observations

**✅ What Works**:
- Simple, append-only design (good!)
- API accepts observations

**❌ What's Missing (Critical)**:
- **No processing logic**
  - The `perform_create` method has a TODO comment: `# Here we will trigger the "Evidence Layer" logic`
  - Observations are saved to DB but **nothing happens with them**
- **Observation types are too narrow** (you identified this in `problems.md`)
  - Missing: "bus didn't come", "bus took different route", "bus broke down", etc.
- **No link to trips**
  - An observation doesn't say WHICH bus it's about
  - No `trip_id` field, no way to match observations to `ActiveTrip`

---

## Data Flow Analysis: How Information Moves (Or Doesn't)

### Current Flow (What Actually Happens)
```
┌─────────────┐
│ GTFS Files  │
└──────┬──────┘
       │ ingest_gtfs command
       ▼
┌─────────────┐
│ gtfs/ tables│ ──────┐
│ (Postgres)  │       │ API reads
└─────────────┘       ▼
                 ┌──────────┐
                 │ Frontend │
                 └──────────┘
```

**That's it.** The `realtime` and `evidence` apps exist but aren't wired to anything.

### Intended Flow (From `philosophy.md`)
```
┌─────────────┐
│ GTFS Files  │ (Prior/Baseline)
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Static Layer: stops, routes, trips │
└────────────┬────────────────────────┘
             │
   ┌─────────┴─────────┐
   │                   │
   ▼                   ▼
┌──────────┐     ┌──────────────┐
│ Frontend │────▶│ Observations │ (User signals)
└──────────┘     └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ Inference    │ (Matches observations to trips)
                 │ Engine       │ (Updates confidence + delay)
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ ActiveTrips  │ (Derived state)
                 │ TripPosition │
                 └──────────────┘
```

**The missing piece**: The inference engine in the middle.

---

## Answering Your Questions from `problems.md`

### Q1: How do we make sure new GTFS data (BMTC, Mumbai) can be ingested?

**Current Contract**:
Your `ingest_gtfs.py` expects these files:
- `stops.txt` → needs `stop_id`, `stop_name`, `stop_lat`, `stop_lon`
- `routes.txt` → needs `route_id`, `route_short_name`, `route_long_name`, `agency_id` (optional)
- `trips.txt` → needs `trip_id`, `route_id`, `service_id`, `shape_id` (optional)
- `stop_times.txt` → needs `trip_id`, `stop_id`, `stop_sequence`, `arrival_time`, `departure_time`

**✅ This is standard GTFS**. Real feeds (BMTC, Mumbai) should work.

**⚠️ Potential Issues**:
1. **Timezones**: Your `arrival_time` is a `TimeField`, which stores time-of-day without timezone info. Real GTFS times are "local time since midnight" and can exceed 24:00:00 (e.g., `25:30:00` for 1:30 AM next day). Django's `TimeField` will **reject** these. You need to either:
   - Store as string and parse manually, or
   - Convert to actual datetime with date offset
2. **`service_id`**: You ingest it but don't use it. Real GTFS has complex service calendars (weekday/weekend/holiday patterns). You'll need `calendar.txt` and `calendar_dates.txt` to filter trips by date.
3. **Shape data**: You store `shape_id` but don't ingest `shapes.txt`. Without it, you can't draw route paths or compute distance-to-route for evidence matching.

**Recommendation**: Test with real GTFS from [transitfeeds.com](http://transitfeeds.com/) to find edge cases.

---

### Q2: How do we figure out stop "direction" / "towards"?

**Current Situation**: You correctly identified that stops don't have a "towards" field. A stop like "MG Road" might serve buses going to different destinations, and you want to show "MG Road (towards Kormangala)" vs "MG Road (towards Whitefield)".

**Your Idea**:
> Figure out all routes going from this stop, find the common denominator stop (most common destination across routes).

**Problem with This Approach**:
- It's a **route-level** property, not a **stop-level** property
- Same stop can serve multiple routes with different "towards" values
- You'd need to show "MG Road (towards X for Route 500D, towards Y for Route 356C)"

**Better Solution** (aligns with GTFS philosophy):
1. **Don't add "towards" to `Stop` model**. It's not a property of the stop.
2. **Use `Trip.headed_to`** (which you already have!)
3. When displaying "upcoming trips at a stop", show:
   ```
   Route 500D → Kormangala (in 5 min)
   Route 500D → Whitefield (in 12 min)
   ```
   The "towards" comes from each trip's `headed_to` field.

**For the "two sides of the road" problem**:
- In GTFS, these are **different stops** with different `stop_id` values
- You can detect "same name, different side" by clustering stops with:
  - Same name (fuzzy match)
  - Within 50m of each other
  - Opposite `headed_to` values (inferred from trips)
- Label them as "Stop A (Platform 1)" and "Stop A (Platform 2)" or use directional arrows in UI

---

### Q3: What is `shape_id` and how do we populate it?

**What it is**: A reference to route geometry (the actual path the bus follows, not just stop-to-stop straight lines).

**In GTFS**: `shapes.txt` file contains:
```
shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence
shape_001,12.9716,77.5946,1
shape_001,12.9720,77.5950,2
...
```

**Why you need it**:
- To draw route lines on a map
- To measure "distance from user's location to route" (for matching observations to trips)
- To compute "progress along route" more accurately than stop-sequence alone

**How to populate**:
1. Add a `Shape` model with PostGIS `LineString` geometry
2. Update `ingest_gtfs.py` to load `shapes.txt` and build LineString from points
3. Link `Trip.shape_id` to this model as a ForeignKey

**For now**: You can skip this for MVP if you only use stop-based positioning. But you'll need it for "the bus took a different route" detection.

---

### Q4: How do we build the confidence/user feedback layer?

This is **the core question**. Let me break it down.

#### Stage 1: Deciding What Signals to Capture

**Current `Observation` types are too limited**. You need to capture:

| Signal Type | What it Means | Data Needed |
|-------------|---------------|-------------|
| `WAITING_AT_STOP` | User is at a stop expecting a bus | `stop_id`, `expected_trip_id` (optional) |
| `ON_BUS` | User confirms they boarded a bus | `stop_id` (where they boarded), `trip_id` (which bus) |
| `BUS_ARRIVED` | User sees bus arrive at their stop | `stop_id`, `trip_id`, `actual_time` |
| `BUS_DIDNT_COME` | User waited but bus never showed | `stop_id`, `expected_trip_id`, `waited_until` |
| `BUS_PASSED` | User sees bus go past a stop without stopping | `stop_id`, `trip_id` |
| `BUS_REROUTED` | User on bus notices it deviated from route | `trip_id`, `lat`, `lon`, `expected_stop_id` |
| `BUS_BREAKDOWN` | Bus stuck/broken | `trip_id`, `lat`, `lon` |
| `STILL_ON_BUS` | Periodic heartbeat from user on bus | `trip_id`, `lat`, `lon` |

**Recommendation**: Expand `ObservationType` choices and add nullable `trip_id` FK to `Observation`.

#### Stage 2: Matching Observations to Trips (The Hard Part)

When a user says "I'm waiting at Stop S001", which trip are they waiting for?
When they say "I'm at lat/lon X,Y", which bus are they on?

**Two Approaches**:

**A. Explicit (Easier, Less Powerful)**:
- User explicitly selects a trip from the UI ("I'm waiting for the 8:30 AM 500D to Kormangala")
- Observation includes `trip_id`
- No inference needed, just validation

**B. Implicit (Harder, More Powerful)**:
- User just shares location
- Backend computes likelihood scores for all plausible trips
- Uses: time of day, proximity to stops/routes, recent trip activity
- Returns probability distribution (as described in `0_1_problem_statment`)

**For 0.1 MVP**: Start with **Approach A**. Users click "I'm on this bus" from the list shown in the Stop Detail page. Much simpler.

#### Stage 3: Creating and Updating `ActiveTrip` Records

You need a **trip activation service** that:

1. **At scheduled start time** (or 15 min before), create `ActiveTrip` for each trip in `service_id` calendar
2. **When observations arrive**, update:
   - `last_observed_at` = now
   - `TripPosition.last_stop_sequence` = inferred from observation location
   - `delay_seconds` = actual_time - scheduled_time
3. **When trip ends** (last stop + 15 min), delete or archive `ActiveTrip`

**Where to implement**:
- **Option 1**: Background worker (Celery task running every 1 min)
- **Option 2**: Handle in `evidence/views.py` `perform_create()` (simpler for MVP)

#### Stage 4: Computing Confidence Scores

From `0_1_problem_statment`: "One user is useless. Three users are interesting. Ten users are truth."

**Formula** (simple version):
```python
# For each ActiveTrip
num_recent_observations = Observation.objects.filter(
    trip_id=trip.trip_id,
    timestamp__gte=now - timedelta(minutes=15)
).count()

confidence_score = min(1.0, num_recent_observations / 5.0)
# 0 observations = 0.0
# 5+ observations = 1.0
```

**Confidence Levels**:
- `< 0.2`: Scheduled (no evidence, show scheduled time)
- `0.2-0.6`: Low Confidence (few users, show "~5 min" with warning)
- `0.6-0.9`: Medium (multiple users, show "5 min")
- `> 0.9`: High (many users, show "5 min ✓ Verified")

---

### Q5: Realtime events vs. systemic errors - which do we solve?

You asked:
> Do we handle "bus broke down right now" (realtime chaos) or "this bus is always +10 min late" (aggregate pattern)?

**From `0_1_problem_statment`**: **You want aggregate patterns, not realtime chaos**. Your problem statement explicitly says:
> "Not 'handle all edge cases'. Not 'perfectly identify every bus'."

**The MVP goal**:
> "Detect persistent, repeatable deviations from the schedule."

**Translation**:
- ✅ "Route 356C is consistently +6 to +9 min late between 8–10 AM" ← Solve this
- ✅ "Stop X is never actually used" ← Solve this
- ❌ "Bus broke down right now, all downstream users need live alert" ← Don't solve this (yet)

**Why?**
Because realtime event propagation requires:
- WebSockets or push notifications
- Very high confidence (false alarms are worse than no info)
- Complex reasoning ("if bus is stuck, when does 'late' become 'cancelled'?")

**Roadmap**:
1. **0.1**: Aggregate delay patterns only (show "usually +8 min")
2. **0.2**: Basic realtime (if 10+ users say "bus didn't come", mark trip as likely skipped)
3. **0.3**: Event propagation (alerts to downstream stops)

---

## Critical Gaps Summary

### Blocking Issues (Can't Work Without These)
1. **No ActiveTrip creation logic** - Trips are never "activated"
2. **No observation processing** - Evidence is saved but ignored
3. **Timezone bug** - Times are in wrong timezone (UTC vs Asia/Kolkata)

### Important Missing Features (Limits Usefulness)
4. **No `trip_id` in Observation model** - Can't link evidence to trips
5. **Observation types too limited** - Can't capture key signals
6. **No confidence scoring** - Field exists but always 0.0
7. **No shape geometry** - Can't draw routes or measure distance-to-route
8. **No service calendar** - All trips show all days (wrong)

### Design Decisions Needed
9. **When/how to create ActiveTrips** - Schedule-based? Evidence-based?
10. **Observation matching strategy** - Explicit user selection vs. inference?
11. **Data retention** - How long to keep observations? When to archive ActiveTrips?

---

## Recommendations: What to Build Next

### Phase 0: Fix Critical Bugs ⚠️
1. **Fix timezone**: Set `TIME_ZONE = 'Asia/Kolkata'` in `settings.py`
2. **Add `trip` FK to Observation**:
   ```python
   trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, null=True, blank=True)
   ```
3. **Expand ObservationType**:
   ```python
   BUS_ARRIVED = 'ARRIVED', 'Bus Arrived'
   BUS_DIDNT_COME = 'NO_SHOW', 'Bus Didn\'t Come'
   # etc.
   ```

### Phase 1: Minimal Confidence Layer (The "Does It Work?" Test) 🎯
**Goal**: Answer "can we detect delay from user observations?"

**Scope**:
1. **Trip Activation Service** (simple version)
   - Management command `python manage.py activate_trips`
   - Runs every 5 min (cron job)
   - Creates `ActiveTrip` for all trips starting in next 15 min
   - Deletes `ActiveTrip` for trips ended >30 min ago
2. **Evidence Processing** (explicit matching)
   - User selects trip from UI, submits "I'm on this bus" observation with `trip_id`
   - `evidence/views.py` `perform_create()`:
     - Saves observation
     - If observation has `trip_id`, update corresponding `ActiveTrip`:
       - `last_observed_at = now`
       - `delay_seconds = actual_time - scheduled_time` (calculate from stop_times)
       - `confidence_score = num_observations / 5.0`
3. **Frontend Integration**:
   - Stop page fetches both `/api/gtfs/stops/{id}/upcoming/` AND `/api/realtime/active-trips/`
   - If a trip appears in both:
     - Show ETA as `scheduled_time + delay_seconds`
     - Show confidence badge if `confidence_score > 0.2`

**Success Criteria**: Open 3 browser tabs, submit "I'm on trip X" from each, see confidence go from 0.0 → 0.6.

### Phase 2: Aggregate Patterns (The Real MVP) 📊
**Goal**: Detect systemic delays like "this route is always late during rush hour"

**Scope**:
1. **Historic Delay Tracking**:
   - New model `TripDelayHistory(trip, date, avg_delay_seconds, num_observations)`
   - Daily batch job: aggregate previous day's `Observations` → compute average delay per trip
2. **Predicted Delay**:
   - When showing upcoming trips, check `TripDelayHistory` for past 7 days
   - If this trip is consistently +X min late, show adjusted ETA
3. **Pattern Detection**:
   - Identify routes with >50% of trips delayed >5 min
   - Identify stops that are skipped >30% of the time
   - API endpoint to expose these insights

### Phase 3: Shape Data & Route Deviation Detection 🗺️
**Goal**: Handle "the bus took a different route" (your Velankani Drive example)

**Scope**:
1. Add `Shape` model, ingest `shapes.txt`
2. For observations with `lat/lon` but no `trip_id`:
   - Compute distance to all active trip shapes
   - If user is 500m from expected route, flag as potential deviation
3. Accumulate deviation observations → suggest new shape when confidence reaches threshold

---

## Does Your Idea Work? Final Answer

**Yes, but with caveats.**

**What Works Already**:
- ✅ GTFS as queryable baseline
- ✅ Spatial queries (nearest stops)
- ✅ Schedule-based "bus should be here" reasoning
- ✅ Clean separation of layers (gtfs / realtime / evidence)

**What Needs to Work (But Doesn't Yet)**:
- ❌ Evidence collection → inference → ActiveTrip updates (the core loop is broken)
- ❌ Confidence scoring (exists as concept, not as code)
- ❌ Aggregation over time (no historic pattern detection)

**Is the Architecture Sound?**
**Yes.** Your `philosophy.md` describes a beautiful, Bayesian, evidence-based system. You just haven't built the core inference engine yet. The bones are strong.

**Can You Build It?**
**Yes.** Start with Phase 1 above (simple, explicit matching). Get the feedback loop working. Then iterate.

**The Key Insight from `0_1_problem_statment`**:
> "Build a small, fake universe where buses misbehave in known ways, and see what signals survive."

You need:
1. **Simulation** (generate fake observations with controlled noise) ← You have this partially (from conversation history)
2. **Inference** (process observations → update beliefs) ← You need to build this
3. **Validation** (does the inferred state match ground truth?) ← You need to measure this

**Bottom Line**: Your backend is 40% done. The GTFS layer is solid. The confidence layer is architected but not implemented. The next step is **not** more planning—it's building the minimal evidence processing loop and seeing if it works.
