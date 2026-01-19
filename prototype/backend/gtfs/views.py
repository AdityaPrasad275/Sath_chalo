from rest_framework import viewsets
from rest_framework_gis.filters import DistanceToPointFilter
from .models import Stop, Route, Trip
from .serializers import StopSerializer, RouteSerializer, TripSerializer

class StopViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer
    filter_backends = [DistanceToPointFilter]
    distance_filter_field = 'geom'
    distance_filter_convert_meters = True

class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

class TripViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    filterset_fields = ['route__route_id', 'direction_id']
