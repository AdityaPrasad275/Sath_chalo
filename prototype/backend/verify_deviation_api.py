import os
import django
from django.utils import timezone

import sys
sys.path.append('/app')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rest_framework.test import APIClient
from gtfs.models import Trip
from evidence.models import Observation
from django.contrib.gis.geos import Point

def run():
    print("Testing Deviation API Logic via APIClient...")
    
    # Get a trip that has a shape
    trip = Trip.objects.filter(shape__isnull=False).first()
    if not trip:
        print("FAIL: No trips with shapes found.")
        return
        
    print(f"Using Trip: {trip.trip_id} (Shape: {trip.shape.shape_id})")
    
    client = APIClient()
    
    # Get a point ON the shape
    line = trip.shape.geometry
    p_on = Point(line[0], srid=4326)
    
    # Test 1: On-route observation
    print("\nTest 1: On-route observation")
    obs_data = {
        "user_id": "tester",
        "type": "ON_BUS",
        "trip": trip.trip_id,
        "lat": p_on.y,
        "lon": p_on.x,
        "notes": "Test on-route"
    }
    
    response = client.post('/api/evidence/observations/', obs_data, format='json')
    if response.status_code == 201:
        obs_id = response.data['id']
        obs = Observation.objects.get(id=obs_id)
        print(f"Observation {obs.id} created.")
        print(f"Distance: {obs.distance_from_trip}")
        print(f"Is Deviation: {obs.is_deviation}")
        
        if obs.is_deviation:
            print("FAIL: Should NOT be a deviation.")
        else:
            print("PASS: Correctly identified as on-route.")
    else:
        print(f"FAIL: API Error: {response.data}")

    # Test 2: Off-route observation (1km away)
    print("\nTest 2: Off-route observation")
    p_off = Point(line[0][0], line[0][1] + 0.01, srid=4326) # +0.01 lat ~ 1.1km
    
    obs_data_off = {
        "user_id": "tester",
        "type": "ON_BUS",
        "trip": trip.trip_id,
        "lat": p_off.y,
        "lon": p_off.x,
        "notes": "Test off-route"
    }
    
    response = client.post('/api/evidence/observations/', obs_data_off, format='json')
    if response.status_code == 201:
        obs_id = response.data['id']
        obs = Observation.objects.get(id=obs_id)
        print(f"Observation {obs.id} created.")
        print(f"Distance: {obs.distance_from_trip}")
        print(f"Is Deviation: {obs.is_deviation}")
        
        if not obs.is_deviation:
            print("FAIL: Should be a deviation.")
        else:
            print("PASS: Correctly identified as deviation.")
    else:
        print(f"FAIL: API Error: {response.data}")

if __name__ == "__main__":
    run()
