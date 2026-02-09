from rest_framework import viewsets, filters
from rest_framework_gis.filters import DistanceToPointFilter
from .serializers import StopSerializer, RouteSerializer, TripSerializer, TripDetailSerializer, UpcomingTripSerializer
from .models import Stop, Route, Trip, StopTime
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import datetime

class StopViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer
    filter_backends = [DistanceToPointFilter, filters.SearchFilter]
    distance_filter_field = 'geom'
    distance_filter_convert_meters = True
    search_fields = ['name', 'stop_id']

    @action(detail=True, methods=['get'])
    def upcoming(self, request, pk=None):
        from gtfs.utils.time_helpers import get_current_service_time, seconds_to_actual_datetime
        from gtfs.models import Agency
        
        stop = self.get_object()
        
        # Get agency timezone (for MVP, use first agency)
        # In multi-agency system, would need to filter by route's agency
        agency = Agency.objects.first()
        if not agency:
            return Response({"error": "No agency configured. Run GTFS ingestion first."}, status=500)
        
        # Get current time in the transit system's timezone
        service_date, current_seconds = get_current_service_time(agency.timezone)
        
        # Query window: -15 min to +2 hours
        window_start = current_seconds - 900
        window_end = current_seconds + 7200
        
        # Find upcoming trips at this stop
        queryset = StopTime.objects.filter(
            stop=stop,
            arrival_seconds__isnull=False,  # Ensure new field is populated
            arrival_seconds__gte=window_start,
            arrival_seconds__lte=window_end
        ).select_related('trip', 'trip__route', 'trip__route__agency').order_by('arrival_seconds')
        
        # Serialize with actual timestamps
        results = []
        for st in queryset:
            arrival_dt = seconds_to_actual_datetime(service_date, st.arrival_seconds, agency.timezone)
            departure_dt = seconds_to_actual_datetime(service_date, st.departure_seconds, agency.timezone)
            
            results.append({
                'trip': {
                    'trip_id': st.trip.trip_id,
                    'route_id': st.trip.route.route_id,
                    'route_name': st.trip.route.short_name,
                    'headed_to': st.trip.headed_to,
                },
                'arrival_timestamp': arrival_dt.isoformat(),  # ISO8601 with timezone
                'departure_timestamp': departure_dt.isoformat(),  # ISO8601 with timezone
                'stop_sequence': st.stop_sequence,
                'seconds_until_arrival': st.arrival_seconds - current_seconds
            })
        
        # Apply pagination if needed
        page = self.paginate_queryset(results)
        if page is not None:
            return self.get_paginated_response(page)
        
        return Response(results)
    
class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

class TripViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    filterset_fields = ['route__route_id', 'headed_to']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TripDetailSerializer
        return TripSerializer
