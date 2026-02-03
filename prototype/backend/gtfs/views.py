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
        from django.db.models import Q
        
        stop = self.get_object()
        now = timezone.localtime(timezone.now()).time()
        
        # Calculate window: 15 mins ago to 2 hours from now
        today = datetime.date.today()
        now_dt = datetime.datetime.combine(today, now)
        
        start_dt = now_dt - datetime.timedelta(minutes=15)
        end_dt = now_dt + datetime.timedelta(hours=1)
        
        start_time = start_dt.time()
        end_time = end_dt.time()

        # Filter stop times for this stop, arriving between start and end
        # We assume services running today for MVP (ignoring service_id for a moment)
        if start_time > end_time:
            # Crosses midnight: Get times >= start OR times <= end
            queryset = StopTime.objects.filter(
                stop=stop
            ).filter(
                Q(arrival_time__gte=start_time) | Q(arrival_time__lte=end_time)
            ).select_related('trip', 'trip__route').order_by('arrival_time')
        else:
            # Standard case
            queryset = StopTime.objects.filter(
                stop=stop,
                arrival_time__range=(start_time, end_time)
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
    filterset_fields = ['route__route_id', 'headed_to']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TripDetailSerializer
        return TripSerializer
