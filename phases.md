Recommendations: What to Build Next
Phase 0: Fix Critical Bugs ⚠️
Fix timezone: Set TIME_ZONE = 'Asia/Kolkata' in 

settings.py
Add 

trip
 FK to Observation:
python
trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, null=True, blank=True)
Expand ObservationType:
python
BUS_ARRIVED = 'ARRIVED', 'Bus Arrived'
BUS_DIDNT_COME = 'NO_SHOW', 'Bus Didn\'t Come'
# etc.
Phase 1: Minimal Confidence Layer (The "Does It Work?" Test) 🎯
Goal: Answer "can we detect delay from user observations?"

Scope:

Trip Activation Service (simple version)
Management command python manage.py activate_trips
Runs every 5 min (cron job)
Creates 

ActiveTrip
 for all trips starting in next 15 min
Deletes 

ActiveTrip
 for trips ended >30 min ago
Evidence Processing (explicit matching)
User selects trip from UI, submits "I'm on this bus" observation with trip_id

evidence/views.py
 

perform_create()
:
Saves observation
If observation has trip_id, update corresponding 

ActiveTrip
:
last_observed_at = now
delay_seconds = actual_time - scheduled_time (calculate from stop_times)
confidence_score = num_observations / 5.0
Frontend Integration:
Stop page fetches both /api/gtfs/stops/{id}/upcoming/ AND /api/realtime/active-trips/
If a trip appears in both:
Show ETA as scheduled_time + delay_seconds
Show confidence badge if confidence_score > 0.2
Success Criteria: Open 3 browser tabs, submit "I'm on trip X" from each, see confidence go from 0.0 → 0.6.

Phase 2: Aggregate Patterns (The Real MVP) 📊
Goal: Detect systemic delays like "this route is always late during rush hour"

Scope:

Historic Delay Tracking:
New model TripDelayHistory(trip, date, avg_delay_seconds, num_observations)
Daily batch job: aggregate previous day's Observations → compute average delay per trip
Predicted Delay:
When showing upcoming trips, check TripDelayHistory for past 7 days
If this trip is consistently +X min late, show adjusted ETA
Pattern Detection:
Identify routes with >50% of trips delayed >5 min
Identify stops that are skipped >30% of the time
API endpoint to expose these insights
Phase 3: Shape Data & Route Deviation Detection 🗺️
Goal: Handle "the bus took a different route" (your Velankani Drive example)

Scope:

Add Shape model, ingest shapes.txt
For observations with lat/lon but no trip_id:
Compute distance to all active trip shapes
If user is 500m from expected route, flag as potential deviation
Accumulate deviation observations → suggest new shape when confidence reaches threshold