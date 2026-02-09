import os
import django
from django.conf import settings

# Setup Django if run directly
# Assuming we run this via `python manage.py shell < script.py` or similar context
# But better to just run as standalone script configuring django settings if needed.
# Since we will run via `docker compose exec web python verify_shapes.py`, we need to set up django.

import sys
sys.path.append('/app')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from gtfs.models import Shape, Trip
from django.contrib.gis.geos import Point, LineString
from gtfs.utils.spatial import get_distance_on_shape, is_off_route

def run():
    print("Verifying Shape ingestion...")
    shape_count = Shape.objects.count()
    print(f"Total Shapes: {shape_count}")
    
    if shape_count == 0:
        print("FAIL: No shapes found!")
        return

    trip_count_with_shape = Trip.objects.filter(shape__isnull=False).count()
    print(f"Trips with Shape: {trip_count_with_shape}")
    
    if trip_count_with_shape == 0:
        print("FAIL: No trips linked to shapes!")
        return

    # Test deviation logic
    print("\nTesting Deviation Logic...")
    s = Shape.objects.first()
    print(f"Using Shape: {s.shape_id}")
    
    # Get a point on the line
    line = s.geometry
    # Take the first point
    p_on_line = Point(line[0], srid=4326)
    
    dist = get_distance_on_shape(p_on_line, line)
    print(f"Distance for point on line: {dist:.2f} meters")
    if dist > 1.0:
        print("FAIL: Point on line should have ~0 distance")
    
    is_off = is_off_route(p_on_line, line)
    print(f"Is off route? {is_off}")
    if is_off:
         print("FAIL: Should not be off route")
         
    # Create a point far away
    # Add 0.01 degrees to lat (~1.1km)
    p_off_line = Point(line[0][0], line[0][1] + 0.01, srid=4326)
    dist_off = get_distance_on_shape(p_off_line, line)
    print(f"Distance for point off line: {dist_off:.2f} meters")
    
    is_off = is_off_route(p_off_line, line)
    print(f"Is off route? {is_off}")
    if not is_off:
        print("FAIL: Should be off route")

    print("\nVerification Complete!")

if __name__ == "__main__":
    run()
