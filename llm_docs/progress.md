# Project Progress - Backend Timezone & Observation Enhancement

**Session Date**: Feb 9, 2026  
**Branch**: `main` (merged `feature/observation-trip-linking`)  
**Status**: Phase 0 Complete ✅, Ready for Phase 1

---

## 🎯 What We Accomplished

### 1. Timezone-Aware GTFS Time System ✅

**Problem**: Backend couldn't handle:
- GTFS times exceeding 24:00:00 (e.g., "25:30:00" for late-night trips)
- Timezone-aware time calculations
- Proper service day logic (3 AM rollover)

**Solution Implemented**:
- ✅ Created `Agency` model with timezone field (IANA format)
- ✅ Replaced `TimeField` with integer seconds storage in `StopTime`
- ✅ Built comprehensive time utility module ([`gtfs/utils/time_helpers.py`](file:///home/ap/Personal_Files/coding/gt/prototype/backend/gtfs/utils/time_helpers.py))
- ✅ Updated `upcoming()` API view to return ISO8601 timestamps
- ✅ Removed deprecated fields (`arrival_time`, `departure_time`, `agency_id_legacy`)
- ✅ Extended GTFS generator to create late-night test data

**Files Modified**:
- [`gtfs/models.py`](file:///home/ap/Personal_Files/coding/gt/prototype/backend/gtfs/models.py) - Agency, Route, StopTime
- [`gtfs/utils/time_helpers.py`](file:///home/ap/Personal_Files/coding/gt/prototype/backend/gtfs/utils/time_helpers.py) - Time conversion utilities
- [`gtfs/management/commands/ingest_gtfs.py`](file:///home/ap/Personal_Files/coding/gt/prototype/backend/gtfs/management/commands/ingest_gtfs.py) - Updated ingestion
- [`gtfs/views.py`](file:///home/ap/Personal_Files/coding/gt/prototype/backend/gtfs/views.py) - Timezone-aware views
- [`data_tools/gtfs_generator/gtfs_generator.py`](file:///home/ap/Personal_Files/coding/gt/data_tools/gtfs_generator/gtfs_generator.py) - Late-night trip generation

**API Response Now**:
```json
{
  "arrival_timestamp": "2026-02-09T14:57:58+05:30",
  "departure_timestamp": "2026-02-09T14:57:58+05:30",
  "seconds_until_arrival": -890
}
```

**Testing**:
- ✅ Ingested GTFS with "25:30:00" times - no errors
- ✅ Database stores 91800 seconds, displays as "25:30:00"
- ✅ API returns proper ISO8601 timestamps with timezone

**Details**: See [walkthrough.md](file:///home/ap/.gemini/antigravity/brain/c93756d8-f78b-4716-8cd7-cf79b48cca0e/walkthrough.md)

---

### 2. Observation Model Enhancement ✅

**Problem**: Observations couldn't link to specific trips, limiting confidence layer implementation.

**Solution Implemented**:
- ✅ Added `trip` FK to `Observation` model
- ✅ Expanded observation types (5 new types):
  - `BUS_ARRIVED`
  - `BUS_DIDNT_COME`
  - `BUS_REROUTED`
  - `BUS_BREAKDOWN`
  - `STILL_ON_BUS`
- ✅ Added `notes` field for user comments
- ✅ Created database indexes on `(trip, timestamp)`, `(stop, timestamp)`, `(user_id, timestamp)`

**Files Modified**:
- [`evidence/models.py`](file:///home/ap/Personal_Files/coding/gt/prototype/backend/evidence/models.py)

**Testing**:
```bash
curl -X POST .../observations/ -d '{
  "type": "ON_BUS",
  "trip": "T_R03_0098",
  "notes": "Testing trip FK"
}'
# ✅ Works: Trip linked, can query o.trip.route.short_name
```

**Details**: See [observation_enhancement.md](file:///home/ap/.gemini/antigravity/brain/c93756d8-f78b-4716-8cd7-cf79b48cca0e/observation_enhancement.md)

---

## 📋 Current Status

### Phase 0: Fix Critical Bugs ✅ COMPLETE

From [backend_analysis.md](file:///home/ap/.gemini/antigravity/brain/c93756d8-f78b-4716-8cd7-cf79b48cca0e/backend_analysis.md#L377-L388):

- [x] Fix timezone handling (was UTC, now timezone-aware)
- [x] Add `trip` FK to Observation
- [x] Expand ObservationType choices

### Phase 1: Minimal Confidence Layer 🎯 NEXT

**Goal**: Answer "can we detect delay from user observations?"

**What to Build** (from [backend_analysis.md](file:///home/ap/.gemini/antigravity/brain/c93756d8-f78b-4716-8cd7-cf79b48cca0e/backend_analysis.md#L390-L414)):

#### 1.1 Trip Activation Service
- **Task**: Create management command `python manage.py activate_trips`
- **Logic**:
  - Runs every 5 min (cron job)
  - Creates `ActiveTrip` for trips starting in next 15 min
  - Deletes `ActiveTrip` for trips ended >30 min ago
- **File**: New `gtfs/management/commands/activate_trips.py`

#### 1.2 Evidence Processing
- **Task**: Process observations → update ActiveTrip
- **Logic**:
  - When observation with `trip_id` arrives
  - Update `ActiveTrip`:
    - `last_observed_at = now`
    - `delay_seconds = actual_time - scheduled_time`
    - `confidence_score = num_observations / 5.0`
- **File**: Update `evidence/views.py` `perform_create()`

#### 1.3 Frontend Integration
- **Task**: Show realtime ETA with confidence badges
- **Logic**:
  - Fetch both `/api/gtfs/stops/{id}/upcoming/` AND `/api/realtime/active-trips/`
  - If trip in both: show adjusted ETA (`scheduled + delay`)
  - Show confidence badge if `score > 0.2`

**Success Criteria**: Open 3 tabs, submit "I'm on trip X" from each, see confidence go from 0.0 → 0.6

---

## 🗂️ Key Artifacts Reference

| Document | Purpose |
|----------|---------|
| [backend_analysis.md](file:///home/ap/.gemini/antigravity/brain/c93756d8-f78b-4716-8cd7-cf79b48cca0e/backend_analysis.md) | Comprehensive analysis + roadmap (Phases 0-3) |
| [implementation_plan.md](file:///home/ap/.gemini/antigravity/brain/c93756d8-f78b-4716-8cd7-cf79b48cca0e/implementation_plan.md) | Detailed plan for timezone system |
| [walkthrough.md](file:///home/ap/.gemini/antigravity/brain/c93756d8-f78b-4716-8cd7-cf79b48cca0e/walkthrough.md) | Testing results for timezone work |
| [observation_enhancement.md](file:///home/ap/.gemini/antigravity/brain/c93756d8-f78b-4716-8cd7-cf79b48cca0e/observation_enhancement.md) | Observation model changes |

---

## 🔧 Database Migrations & Docker

### Current Migrations Applied
```
gtfs.0003_agency_timezone_changes
gtfs.0004_remove_deprecated_fields
evidence.0002_trip_fk_and_types
```

### Important: Migration & Branch Switching

**Q**: What happens if I checkout an old commit before these migrations?

**A**: Code and database can get out of sync. Here's how it works:

**Scenario**: You checkout to a commit before `BUS_ARRIVED` observation type existed

1. **Code**: Old - doesn't know about `BUS_ARRIVED`
2. **Database**: New - has the field

**What happens**:
- ✅ **Reading old data**: Works fine
- ⚠️ **Creating new observations**: Old code can't create `BUS_ARRIVED` type (it's not in choices)
- ❌ **If you run migrations backward**: Data loss risk!

**Best Practices**:

1. **For Development** (your case):
   ```bash
   # If switching to old branch, rollback migrations
   python manage.py migrate gtfs 0002  # Roll back to specific migration
   python manage.py migrate evidence 0001
   
   # When coming back to main
   python manage.py migrate  # Apply all migrations
   ```

2. **For Production**:
   - Never rollback migrations with data
   - Use **forward-only migrations**
   - Create new migration to undo changes if needed

3. **With Docker**:
   - Database is in Docker volume `pg_data`
   - Persists across container restarts
   - To reset completely: `docker compose down -v` (deletes volumes!)

**Workflow**:
```bash
# Safe way to test old code
git checkout <old-commit>
docker compose down -v  # Fresh database
docker compose up -d
# Re-ingest GTFS data
```

---

## 📊 Database Schema (Current State)

### GTFS App
- `Agency` - timezone, name, url
- `Stop` - lat/lon (PostGIS Point)
- `Route` - short_name, long_name, agency FK
- `Trip` - route FK, headed_to, service_id
- `StopTime` - trip FK, stop FK, arrival_seconds, departure_seconds

### Realtime App
- `ActiveTrip` - trip FK, delay_seconds, confidence_score
- `TripPosition` - active_trip FK, last_stop_sequence, progress_ratio

### Evidence App
- `Observation` - user_id, type, timestamp, stop FK, **trip FK**, lat/lon, notes

---

## 🚀 Next Session Action Plan

### Quick Start
1. Review [backend_analysis.md Phase 1](file:///home/ap/.gemini/antigravity/brain/c93756d8-f78b-4716-8cd7-cf79b48cca0e/backend_analysis.md#L390-L414)
2. Start with **Trip Activation Service** (simplest piece)
3. Then **Evidence Processing** (core logic)
4. Finally **Frontend Integration** (visual proof it works)

### Commands to Remember
```bash
# Start development
docker compose up -d

# Make migrations
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Ingest test data
docker compose exec web python manage.py ingest_gtfs /app/gtfs_data

# Test observation API
curl -X POST http://localhost:8000/api/evidence/observations/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "type": "ON_BUS", "trip": "T_R03_0098"}'
```

---

## 🎉 Key Wins

1. **Future-proof time system** - Works globally, handles all GTFS edge cases
2. **Clean API** - ISO8601 timestamps, no redundant fields
3. **Observation model ready** - Can link to trips, comprehensive signal types
4. **Solid foundation** - Phase 0 complete, ready for core confidence layer

**Bottom Line**: The plumbing is done. Now we build the intelligence layer! 🧠
