import csv
import os
import math
import random
import datetime
import shutil

# --- Configuration ---
OUTPUT_DIR = "gtfs_data"
CENTER_LAT = 12.9716
CENTER_LON = 77.5946
LAT_SPREAD = 0.03  # Approx 3km spread
LON_SPREAD = 0.03

NUM_STOPS = 30
NUM_ROUTES = 5
TRIPS_PER_ROUTE = 10

START_HOUR = 6
END_HOUR = 22
FREQUENCY_MINUTES = 30

AGENCY_NAME = "Small World Transit"
AGENCY_TIMEZONE = "Asia/Kolkata"

# Simply Euclidean distance for "small world" (valid enough for small areas)
def get_distance(lat1, lon1, lat2, lon2):
    # Approx conversion for Bangalore latitude
    lat_km = (lat1 - lat2) * 110.574
    lon_km = (lon1 - lon2) * 111.320 * math.cos(math.radians(lat1)) 
    return math.sqrt(lat_km**2 + lon_km**2)

class GTFSGenerator:
    def __init__(self):
        self.stops = []
        self.routes = []
        self.trips = []
        self.stop_times = []
        self.shapes = [] # Not strictly needed for minimal valid GTFS but good for debugging if we add it
        self.calendar = []
        
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        else:
            # Clear existing data without removing the directory itself (which might be a mount point)
            for filename in os.listdir(OUTPUT_DIR):
                file_path = os.path.join(OUTPUT_DIR, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")

    def generate_agency(self):
        with open(f"{OUTPUT_DIR}/agency.txt", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["agency_id", "agency_name", "agency_url", "agency_timezone"])
            writer.writerow(["1", AGENCY_NAME, "http://example.com", AGENCY_TIMEZONE])
        print("Generated agency.txt")

    def generate_stops(self):
        print(f"Generating {NUM_STOPS} stops...")
        with open(f"{OUTPUT_DIR}/stops.txt", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["stop_id", "stop_name", "stop_lat", "stop_lon"])
            
            for i in range(1, NUM_STOPS + 1):
                # Random spread around center
                lat = CENTER_LAT + random.uniform(-LAT_SPREAD, LAT_SPREAD)
                lon = CENTER_LON + random.uniform(-LON_SPREAD, LON_SPREAD)
                stop_id = f"S{i:03d}"
                name = f"Stop {chr(65 + (i%26))} {i}"
                
                self.stops.append({"id": stop_id, "lat": lat, "lon": lon})
                writer.writerow([stop_id, name, lat, lon])
        print("Generated stops.txt")

    def generate_calendar(self):
        # Service runs every day
        with open(f"{OUTPUT_DIR}/calendar.txt", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["service_id", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "start_date", "end_date"])
            writer.writerow(["WEEKDAY", "1", "1", "1", "1", "1", "1", "1", "20240101", "20251231"])
        print("Generated calendar.txt")

    def generate_routes(self):
        print(f"Generating {NUM_ROUTES} routes...")
        with open(f"{OUTPUT_DIR}/routes.txt", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["route_id", "agency_id", "route_short_name", "route_long_name", "route_type"])
            
            for i in range(1, NUM_ROUTES + 1):
                route_id = f"R{i:02d}"
                short_name = f"{i*100}"
                long_name = f"Route {short_name}"
                route_type = 3 # Bus
                
                # Pick random stops for this route to serve
                # Each route gets a random subset of stops, ordered
                num_route_stops = random.randint(5, 12)
                route_stops = random.sample(self.stops, min(num_route_stops, len(self.stops)))
                # Sort by longitude to make somewhat straight-ish lines (simple heuristic)
                route_stops.sort(key=lambda s: s["lon"])
                
                self.routes.append({
                    "id": route_id,
                    "stops": route_stops
                })
                
                writer.writerow([route_id, "1", short_name, long_name, route_type])
        print("Generated routes.txt")

    def generate_trips_and_stop_times(self):
        print("Generating trips and stop times...")
        
        trips_file = open(f"{OUTPUT_DIR}/trips.txt", "w", newline="")
        trips_writer = csv.writer(trips_file)
        trips_writer.writerow(["route_id", "service_id", "trip_id", "shape_id"])
        
        st_file = open(f"{OUTPUT_DIR}/stop_times.txt", "w", newline="")
        st_writer = csv.writer(st_file)
        st_writer.writerow(["trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence"])
        
        trip_counter = 1
        
        for route in self.routes:
            # Generate trips throughout the day
            current_time = datetime.datetime(2024, 1, 1, START_HOUR, 0, 0)
            end_time = datetime.datetime(2024, 1, 1, END_HOUR, 0, 0)
            
            while current_time < end_time:
                trip_id = f"T_{route['id']}_{trip_counter:04d}"
                service_id = "WEEKDAY"
                shape_id = "" # Shapes not implemented in v0.1
                
                trips_writer.writerow([route['id'], service_id, trip_id, shape_id])
                
                # Generate stop times
                trip_cursor_time = current_time
                sequence = 1
                
                for i, stop in enumerate(route['stops']):
                    # Calculate travel time to next stop
                    if i > 0:
                        prev_stop = route['stops'][i-1]
                        dist_km = get_distance(prev_stop['lat'], prev_stop['lon'], stop['lat'], stop['lon'])
                        # Assume 20km/h average speed in city
                        minutes_travel = (dist_km / 20.0) * 60
                        # Add some dwell time (0.5 to 1.5 min)
                        dwell = 0.5
                        trip_cursor_time += datetime.timedelta(minutes=minutes_travel + dwell)
                    
                    time_str = trip_cursor_time.strftime("%H:%M:%S")
                    st_writer.writerow([trip_id, time_str, time_str, stop['id'], sequence])
                    sequence += 1
                
                # Next trip
                current_time += datetime.timedelta(minutes=FREQUENCY_MINUTES)
                trip_counter += 1
                
        trips_file.close()
        st_file.close()
        print("Generated trips.txt and stop_times.txt")

    def run(self):
        self.generate_agency()
        self.generate_stops()
        self.generate_calendar()
        self.generate_routes()
        self.generate_trips_and_stop_times()
        print(f"Done! GTFS data generated in ./{OUTPUT_DIR}")

if __name__ == "__main__":
    generator = GTFSGenerator()
    generator.run()
