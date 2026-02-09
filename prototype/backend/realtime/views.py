from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ActiveTrip, TripDelayHistory
from .serializers import ActiveTripSerializer
from gtfs.models import Route, StopTime, Trip
from django.db.models import Avg, Count, Q
from django.utils import timezone
import datetime


class ActiveTripViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActiveTrip.objects.all()
    serializer_class = ActiveTripSerializer
    
    @action(detail=False, methods=['get'])
    def patterns(self, request):
        """
        Detect patterns in delay data:
        - Routes with >50% of trips delayed >5 min
        - Stops that are skipped >30% of the time
        """
        # Look at last 7 days of data
        cutoff_date = timezone.now().date() - datetime.timedelta(days=7)
        
        # 1. Delayed Routes Analysis
        delayed_routes = self._analyze_delayed_routes(cutoff_date)
        
        # 2. Skipped Stops Analysis  
        skipped_stops = self._analyze_skipped_stops(cutoff_date)
        
        return Response({
            'delayed_routes': delayed_routes,
            'skipped_stops': skipped_stops,
            'analysis_period': {
                'start_date': cutoff_date.isoformat(),
                'end_date': timezone.now().date().isoformat(),
                'days': 7
            }
        })
    
    def _analyze_delayed_routes(self, cutoff_date):
        """
        Find routes where >50% of trips have avg delay >300s (5 min).
        """
        delayed_routes = []
        
        # Get all delay history from last 7 days
        history = TripDelayHistory.objects.filter(
            date__gte=cutoff_date
        ).select_related('trip__route')
        
        # Group by route
        route_data = {}
        for record in history:
            route_id = record.trip.route.route_id
            if route_id not in route_data:
                route_data[route_id] = {
                    'route_id': route_id,
                    'route_name': record.trip.route.short_name,
                    'total_trips': 0,
                    'delayed_trips': 0,
                    'total_delay': 0,
                }
            
            route_data[route_id]['total_trips'] += 1
            route_data[route_id]['total_delay'] += record.avg_delay_seconds
            
            # Count as delayed if avg delay > 300 seconds (5 min)
            if record.avg_delay_seconds > 300:
                route_data[route_id]['delayed_trips'] += 1
        
        # Filter routes with >50% trips delayed
        for route_id, data in route_data.items():
            pct_delayed = data['delayed_trips'] / data['total_trips'] if data['total_trips'] > 0 else 0
            
            if pct_delayed > 0.5:
                avg_delay = data['total_delay'] // data['total_trips']
                delayed_routes.append({
                    'route_id': route_id,
                    'route_name': data['route_name'],
                    'pct_trips_delayed': round(pct_delayed, 2),
                    'avg_delay_seconds': avg_delay,
                    'total_trips_analyzed': data['total_trips']
                })
        
        # Sort by percentage delayed (worst first)
        delayed_routes.sort(key=lambda x: x['pct_trips_delayed'], reverse=True)
        
        return delayed_routes
    
    def _analyze_skipped_stops(self, cutoff_date):
        """
        Find stops that are frequently skipped based on observation data.
        
        Logic: Compare scheduled stop_times vs actual observations.
        If a stop has significantly fewer observations than expected, it may be skipped.
        """
        # This is complex - for MVP, return placeholder
        # Full implementation would:
        # 1. Get all trips that should have stopped at each stop
        # 2. Count observations at each stop
        # 3. Calculate observation rate (actual / expected)
        # 4. Flag stops with <70% observation rate
        
        # For now, return empty array with note
        return []
