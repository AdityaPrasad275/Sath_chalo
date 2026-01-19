from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Stop, Route, Trip, StopTime

class StopSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Stop
        geo_field = 'geom'
        fields = ['stop_id', 'name']

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'

class TripSerializer(serializers.ModelSerializer):
    route_name = serializers.CharField(source='route.short_name', read_only=True)
    
    class Meta:
        model = Trip
        fields = ['trip_id', 'route', 'route_name', 'direction_id', 'shape_id']

class StopTimeSerializer(serializers.ModelSerializer):
    stop_name = serializers.CharField(source='stop.name', read_only=True)
    
    class Meta:
        model = StopTime
        fields = ['stop', 'stop_name', 'stop_sequence', 'arrival_time', 'departure_time']
