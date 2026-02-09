from rest_framework import serializers
from .models import ActiveTrip, TripPosition, TripDelayHistory
from gtfs.serializers import TripSerializer
from django.utils import timezone
import datetime


class TripPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripPosition
        fields = ['last_stop_sequence', 'progress_ratio', 'observed_at']


class ActiveTripSerializer(serializers.ModelSerializer):
    trip_details = TripSerializer(source='trip', read_only=True)
    position = TripPositionSerializer(read_only=True)
    
    # Predicted delay based on historic data
    predicted_delay_seconds = serializers.SerializerMethodField()
    prediction_confidence = serializers.SerializerMethodField()
    
    class Meta:
        model = ActiveTrip
        fields = ['id', 'trip', 'trip_details', 'started_at', 'last_observed_at', 
                  'delay_seconds', 'confidence_score', 'position',
                  'predicted_delay_seconds', 'prediction_confidence']
    
    def get_predicted_delay_seconds(self, obj):
        """
        Calculate predicted delay based on last 7 days of TripDelayHistory.
        Returns average delay or None if insufficient data.
        """
        cutoff_date = (timezone.now().date() - datetime.timedelta(days=7))
        
        history = TripDelayHistory.objects.filter(
            trip=obj.trip,
            date__gte=cutoff_date
        )
        
        if not history.exists():
            return None
        
        # Calculate weighted average (more recent = higher weight)
        total_delay = 0
        total_weight = 0
        
        for record in history:
            # Weight by number of observations
            weight = record.num_observations
            total_delay += record.avg_delay_seconds * weight
            total_weight += weight
        
        if total_weight == 0:
            return None
        
        return total_delay // total_weight  # Integer average
    
    def get_prediction_confidence(self, obj):
        """
        Return number of days of historic data available (0-7).
        Higher = more confident in prediction.
        """
        cutoff_date = (timezone.now().date() - datetime.timedelta(days=7))
        
        count = TripDelayHistory.objects.filter(
            trip=obj.trip,
            date__gte=cutoff_date
        ).count()
        
        return count
