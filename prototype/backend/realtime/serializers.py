from rest_framework import serializers
from .models import ActiveTrip, TripPosition
from gtfs.serializers import TripSerializer

class TripPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripPosition
        fields = ['last_stop_sequence', 'progress_ratio', 'observed_at']

class ActiveTripSerializer(serializers.ModelSerializer):
    trip_details = TripSerializer(source='trip', read_only=True)
    position = TripPositionSerializer(read_only=True)
    
    class Meta:
        model = ActiveTrip
        fields = ['id', 'trip', 'trip_details', 'started_at', 'last_observed_at', 'delay_seconds', 'confidence_score', 'position']
