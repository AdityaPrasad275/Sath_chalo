import os
import django
from django.utils import timezone
import datetime

import sys
sys.path.append('/app')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rest_framework.test import APIClient
from gtfs.models import Trip, Stop, StopTime
from realtime.models import ActiveTrip
from gtfs.utils.time_helpers import get_current_service_time

def run():
    print("Verifying API Integration...")
    
    # 1. Setup Data
    # Create Dummy Data for accurate testing window
    from gtfs.models import Route, Agency
    
    agency = Agency.objects.first()
    service_date, current_seconds = get_current_service_time(agency.timezone)
    print(f"Current Service Time: {current_seconds} ({service_date})")
    
    # Create Dummy Route/Trip/Stop
    from django.contrib.gis.geos import Point
    
    route, _ = Route.objects.get_or_create(
        route_id="TEST_ROUTE", 
        defaults={'short_name': 'TEST', 'long_name': 'Test Route', 'agency': agency}
    )
    trip, _ = Trip.objects.get_or_create(
        trip_id="TEST_TRIP",
        defaults={'route': route, 'service_id': 'UNKNOWN', 'headed_to': 'Test Dest'}
    )
    stop, _ = Stop.objects.get_or_create(
        stop_id="TEST_STOP",
        defaults={'name': 'Test Stop', 'geom': Point(77.0, 12.0, srid=4326)}
    )
    
    # Schedule it for NOW + 30 mins
    scheduled_arrival = current_seconds + 1800
    StopTime.objects.update_or_create(
        trip=trip, stop=stop,
        defaults={
            'stop_sequence': 1,
            'arrival_seconds': scheduled_arrival,
            'departure_seconds': scheduled_arrival + 60
        }
    )
    print(f"Created/Updated Test Trip {trip.trip_id} at {stop.stop_id} for {scheduled_arrival}s")

    # 2. Create ActiveTrip with DELAY
    delay = 300 # 5 minutes late
    confidence = 0.8
    
    ActiveTrip.objects.filter(trip=trip).delete() # Cleanup
    active_trip = ActiveTrip.objects.create(
        trip=trip,
        delay_seconds=delay,
        confidence_score=confidence,
        last_observed_at=timezone.now()
    )
    print(f"Created ActiveTrip with {delay}s delay and {confidence} confidence.")
    
    # 3. Call API
    client = APIClient()
    url = f'/api/gtfs/stops/{stop.stop_id}/upcoming/'
    print(f"Fetching {url}...")
    
    response = client.get(url)
    if response.status_code != 200:
        print(f"FAIL: API Error {response.status_code}: {response.data}")
        return
        
    results = response.data
    print(f"Response Data Type: {type(results)}")
    if isinstance(results, list) and len(results) > 0:
         print(f"First Item Type: {type(results[0])}")
         print(f"First Item: {results[0]}")
    else:
         print(f"Response Data: {results}")

    # 4. Verify Results
    results_list = results
    if isinstance(results, dict) and 'results' in results:
        results_list = results['results']
        
    found = False
    for item in results_list:
        if not isinstance(item, dict):
             continue
             
        if item['trip']['trip_id'] == trip.trip_id:
            found = True
            print(f"Found Trip in results!")
            print(f"  Delay: {item.get('delay_seconds')}")
            print(f"  Confidence: {item.get('confidence_score')}")
            print(f"  Is Realtime: {item.get('is_realtime')}")
            
            if item.get('delay_seconds') == delay and item.get('is_realtime') == True:
                print("PASS: Realtime data merged correctly.")
            else:
                print("FAIL: Data mismatch.")
            break
            
    if not found:
        # It might not be in the upcoming window?
        # Check window logic in view: -15m to +2h
        # If the trip is outside this window, it won't show.
        # Let's check the stop time arrival
        print("WARN: Trip not found in response. Checking time window...")
        agency = trip.route.agency
        service_date, current_seconds = get_current_service_time(agency.timezone)
        print(f"Current Service Time: {current_seconds}")
        print(f"Stop Arrival Time: {stop_time.arrival_seconds}")
        
        diff = stop_time.arrival_seconds + delay - current_seconds
        print(f"Seconds until arrival (adjusted): {diff}")
        
        if diff < -900 or diff > 7200:
            print("Trip is outside the -15m to +2h window. Cannot verify via API.")
        else:
            print("FAIL: Trip should be visible but is not.")

    # Cleanup
    active_trip.delete()

if __name__ == "__main__":
    run()
