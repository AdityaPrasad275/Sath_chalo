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
        stop = self.get_object()
        now = timezone.now().time()
        
        # User can provide a time like HH:MM:SS
        user_time = request.query_params.get('time')
        if user_time:
            try:
                now = datetime.datetime.strptime(user_time, '%H:%M:%S').time()
            except ValueError:
                pass # Fallback to current time

        # Filter stop times for this stop, arriving after 'now'
        # We assume services running today for MVP (ignoring service_id for a moment)
        queryset = StopTime.objects.filter(
            stop=stop,
            arrival_time__gte=now
        ).select_related('trip', 'trip__route').order_by('arrival_time')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UpcomingTripSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UpcomingTripSerializer(queryset, many=True)
        return Response(serializer.data)

class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

class TripViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    filterset_fields = ['route__route_id', 'direction_id']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TripDetailSerializer
        return TripSerializer
