import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from gtfs.models import Agency, Stop, Route, Trip, StopTime
from gtfs.utils.time_helpers import gtfs_time_to_seconds

class Command(BaseCommand):
    help = 'Ingest GTFS data from a directory'

    def add_arguments(self, parser):
        parser.add_argument('folder_path', type=str, help='Path to the GTFS folder')

    def handle(self, *args, **kwargs):
        folder_path = kwargs['folder_path']
        
        self.stdout.write("Clearing existing GTFS data...")
        # Delete in order of dependencies
        StopTime.objects.all().delete()
        Trip.objects.all().delete()
        Route.objects.all().delete()
        Stop.objects.all().delete()
        Agency.objects.all().delete()

        # Import in dependency order
        self.import_agencies(os.path.join(folder_path, 'agency.txt'))
        self.import_stops(os.path.join(folder_path, 'stops.txt'))
        self.import_routes(os.path.join(folder_path, 'routes.txt'))
        self.import_trips(os.path.join(folder_path, 'trips.txt'), os.path.join(folder_path, 'stop_times.txt'))
        self.import_stop_times(os.path.join(folder_path, 'stop_times.txt'))
        
        self.stdout.write(self.style.SUCCESS('Successfully ingested GTFS data'))

    def import_agencies(self, path):
        self.stdout.write(f"Importing agencies from {path}...")
        agencies = []
        with open(path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                agencies.append(Agency(
                    agency_id=row['agency_id'],
                    name=row['agency_name'],
                    url=row.get('agency_url', ''),
                    timezone=row['agency_timezone']
                ))
        Agency.objects.bulk_create(agencies)
        self.stdout.write(f"Created {len(agencies)} agencies.")

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
        
        # Load agencies for FK lookup
        agencies = {a.agency_id: a for a in Agency.objects.all()}
        
        routes = []
        with open(path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                agency_id = row.get('agency_id')
                agency = agencies.get(agency_id) if agency_id else list(agencies.values())[0]
                
                routes.append(Route(
                    route_id=row['route_id'],
                    short_name=row['route_short_name'],
                    long_name=row['route_long_name'],
                    agency=agency
                ))
        Route.objects.bulk_create(routes)
        self.stdout.write(f"Created {len(routes)} routes.")


    def import_trips(self, path, stop_times_path):
        self.stdout.write(f"Calculating trip destinations from {stop_times_path}...")
        trip_destinations = {} # trip_id -> last_stop_id
        trip_max_sequence = {} # trip_id -> max_sequence

        # First pass: find last stop ID for each trip
        with open(stop_times_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                uid = row['trip_id']
                seq = int(row['stop_sequence'])
                sid = row['stop_id']
                
                if uid not in trip_max_sequence or seq > trip_max_sequence[uid]:
                    trip_max_sequence[uid] = seq
                    trip_destinations[uid] = sid

        # Load all stop names to memory for fast lookup
        stop_names = dict(Stop.objects.values_list('stop_id', 'name'))

        self.stdout.write(f"Importing trips from {path}...")
        trips = []
        
        with open(path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tid = row['trip_id']
                last_stop_id = trip_destinations.get(tid)
                headed_to = stop_names.get(last_stop_id, "Unknown")

                trips.append(Trip(
                    trip_id=tid,
                    route_id=row['route_id'], # Referencing the PK directly
                    service_id=row['service_id'],
                    shape_id=row.get('shape_id'),
                    headed_to=headed_to
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
                    arrival_seconds=gtfs_time_to_seconds(row['arrival_time']),
                    departure_seconds=gtfs_time_to_seconds(row['departure_time'])
                ))
        # Large file, chunk it
        batch_size = 5000
        for i in range(0, len(stop_times), batch_size):
            StopTime.objects.bulk_create(stop_times[i:i+batch_size])
        self.stdout.write(f"Created {len(stop_times)} stop times.")
