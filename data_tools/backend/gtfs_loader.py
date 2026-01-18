import pandas as pd
import os
from typing import List, Dict, Any

class GTFSLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.stops = pd.DataFrame()
        self.routes = pd.DataFrame()
        self.trips = pd.DataFrame()
        self.stop_times = pd.DataFrame()

    def load(self):
        try:
            self.stops = pd.read_csv(os.path.join(self.data_dir, "stops.txt"))
            self.routes = pd.read_csv(os.path.join(self.data_dir, "routes.txt"))
            self.trips = pd.read_csv(os.path.join(self.data_dir, "trips.txt"))
            # Make sure we read stop_times as well
            self.stop_times = pd.read_csv(os.path.join(self.data_dir, "stop_times.txt"))
            
            # Fill NaNs to avoid JSON serialization errors (e.g. empty shape_id)
            self.trips = self.trips.fillna("")
            self.stop_times = self.stop_times.fillna("")
            self.stops = self.stops.fillna("")
            self.routes = self.routes.fillna("")
            
            # Basic type conversion if needed
            self.routes['route_id'] = self.routes['route_id'].astype(str)
            self.trips['route_id'] = self.trips['route_id'].astype(str)
            self.trips['trip_id'] = self.trips['trip_id'].astype(str)
            self.stops['stop_id'] = self.stops['stop_id'].astype(str)
            self.stop_times['trip_id'] = self.stop_times['trip_id'].astype(str)
            self.stop_times['stop_id'] = self.stop_times['stop_id'].astype(str)
            
        except FileNotFoundError as e:
            print(f"Warning: Could not load some GTFS files: {e}")

    def get_stops(self) -> List[Dict[str, Any]]:
        if self.stops.empty:
            return []
        return self.stops.to_dict(orient="records")

    def get_routes(self) -> List[Dict[str, Any]]:
        if self.routes.empty:
            return []
        return self.routes.to_dict(orient="records")

    def get_trips(self, route_id: str) -> List[Dict[str, Any]]:
        if self.trips.empty:
            return []
        
        # Filter trips for the route
        route_trips = self.trips[self.trips['route_id'] == route_id]
        
        # For simplicity in this visualizer, let's just return the trip info
        # In a real app, we might join with shapes or stop_times to give a full path
        return route_trips.to_dict(orient="records")

    def get_stop_times_for_trip(self, trip_id: str) -> List[Dict[str, Any]]:
        if self.stop_times.empty:
            return []
        st = self.stop_times[self.stop_times['trip_id'] == trip_id].sort_values('stop_sequence')
        # Join with stop info to get lat/lon
        merged = st.merge(self.stops, on='stop_id', how='left')
        return merged.to_dict(orient="records")

    def get_timetable(self, route_id: str) -> Dict[str, Any]:
        """
        Returns a pivot-table style structure:
        - stops: ordered list of stops for this route (based on a representative trip)
        - trips: list of trips, each with 'trip_id' and a map of 'times': {stop_id: arrival_time}
        """
        if self.trips.empty or self.stop_times.empty:
            return {"stops": [], "trips": []}

        # Get all trips for this route
        route_trips = self.trips[self.trips['route_id'] == route_id]
        if route_trips.empty:
            return {"stops": [], "trips": []}
        
        trip_ids = route_trips['trip_id'].unique()
        
        # Get all stop times for these trips
        mask = self.stop_times['trip_id'].isin(trip_ids)
        route_st = self.stop_times[mask].copy()
        
        if route_st.empty:
            return {"stops": [], "trips": []}
            
        # Determine the order of stops. 
        # In a simple world, all trips on a route have the same stops in same order.
        # We'll take the trip with the most stops as the "canonical" sequence.
        # Group by trip_id, count stops
        counts = route_st.groupby('trip_id')['stop_sequence'].count()
        longest_trip_id = counts.idxmax()
        
        canonical_stops_df = route_st[route_st['trip_id'] == longest_trip_id].sort_values('stop_sequence')
        canonical_stops_ids = canonical_stops_df['stop_id'].tolist()
        
        # Get stop details/names
        canonical_stops_details = []
        for sid in canonical_stops_ids:
            stop_info = self.stops[self.stops['stop_id'] == sid]
            if not stop_info.empty:
                canonical_stops_details.append(stop_info.iloc[0].to_dict())
            else:
                canonical_stops_details.append({"stop_id": sid, "stop_name": "Unknown"})

        # Now build the pivoted trip data
        # We want a list of trips, sorted by departure time at the first stop
        
        # Pivot: index=trip_id, columns=stop_id, values=arrival_time
        pivot = route_st.pivot(index='trip_id', columns='stop_id', values='arrival_time')
        
        # We also want to sort the trips by time. 
        # Let's find the time at the first stop for each trip
        first_stop_id = canonical_stops_ids[0]
        
        result_trips = []
        
        # Iterate through trips in the order they appear in trips.txt (which our generator makes chronological)
        # OR sort by the time at the first stop
        
        for tid in trip_ids:
            # Check if this trip exists in pivot (it should)
            if tid not in pivot.index:
                continue
                
            times = pivot.loc[tid].to_dict()
            # Filter times to only include canonical stops (or keep all? keep all is safer but let's stick to canonical structure for table)
            
            # Simple sorting value: time at first stop. If nan, try second, etc.
            sort_val = "99:99:99"
            for sid in canonical_stops_ids:
                val = times.get(sid)
                if pd.notna(val) and val != "":
                    sort_val = val
                    break
            
            result_trips.append({
                "trip_id": tid,
                "times": times, # {stop_id: "HH:MM:SS"}
                "start_time": sort_val 
            })
            
        # Sort trips by start_time
        result_trips.sort(key=lambda x: x['start_time'])
        
        return {
            "stops": canonical_stops_details,
            "trips": result_trips
        }
