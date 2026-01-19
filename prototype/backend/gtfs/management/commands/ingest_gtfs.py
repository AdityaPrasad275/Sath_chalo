import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from gtfs.models import Stop, Route, Trip, StopTime

class Command(BaseCommand):
    help = 'Ingest GTFS data from a directory'

    def add_arguments(self, parser):
        parser.add_argument('folder_path', type=str, help='Path to the GTFS folder')

    def handle(self, *args, **kwargs):
        folder_path = kwargs['folder_path']
        
        self.stdout.write("Clearing existing GTFS data...")
        StopTime.objects.all().delete()
        Trip.objects.all().delete()
        Route.objects.all().delete()
        Stop.objects.all().delete()

        self.import_stops(os.path.join(folder_path, 'stops.txt'))
        self.import_routes(os.path.join(folder_path, 'routes.txt'))
        self.import_trips(os.path.join(folder_path, 'trips.txt'))
        self.import_stop_times(os.path.join(folder_path, 'stop_times.txt'))
        
        self.stdout.write(self.style.SUCCESS('Successfully ingested GTFS data'))

    def import_stops(self, path):
        self.stdout.write(f"Importing stops from {path}...")
        stops = []
        with open(path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                lat = float(row['stop_lat'])
                lon = float(row['stop_lon'])
                stops.append(Stop(
                    stop_id=row['stop_id'],
                    name=row['stop_name'],
                    geom=Point(lon, lat)
                ))
        Stop.objects.bulk_create(stops)
        self.stdout.write(f"Created {len(stops)} stops.")

    def import_routes(self, path):
        self.stdout.write(f"Importing routes from {path}...")
        routes = []
        with open(path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                routes.append(Route(
                    route_id=row['route_id'],
                    short_name=row['route_short_name'],
                    long_name=row['route_long_name'],
                    agency_id=row.get('agency_id')
                ))
        Route.objects.bulk_create(routes)
        self.stdout.write(f"Created {len(routes)} routes.")

    def import_trips(self, path):
        self.stdout.write(f"Importing trips from {path}...")
        trips = []
        # Cache routes to avoid DB hits if needed, but for bulk_create we just need ID if referencing directly? 
        # Django bulk_create with ForeignKeys needs the instance or the ID. 
        # Since we use simple string IDs for our models (primary_key=True), we can simple act as if they exist.
        
        with open(path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                trips.append(Trip(
                    trip_id=row['trip_id'],
                    route_id=row['route_id'], # Referencing the PK directly
                    service_id=row['service_id'],
                    shape_id=row.get('shape_id')
                ))
        Trip.objects.bulk_create(trips)
        self.stdout.write(f"Created {len(trips)} trips.")

    def import_stop_times(self, path):
        self.stdout.write(f"Importing stop_times from {path}...")
        stop_times = []
        with open(path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                stop_times.append(StopTime(
                    trip_id=row['trip_id'],
                    stop_id=row['stop_id'],
                    stop_sequence=int(row['stop_sequence']),
                    arrival_time=row['arrival_time'],
                    departure_time=row['departure_time']
                ))
        # Large file, chunk it
        batch_size = 5000
        for i in range(0, len(stop_times), batch_size):
            StopTime.objects.bulk_create(stop_times[i:i+batch_size])
        self.stdout.write(f"Created {len(stop_times)} stop times.")
