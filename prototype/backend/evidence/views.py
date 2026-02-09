from rest_framework import viewsets, mixins
from .models import Observation
from .serializers import ObservationSerializer
from realtime.models import ActiveTrip, TripPosition
from gtfs.models import Agency
from gtfs.utils.time_helpers import get_current_service_time, datetime_to_service_seconds
from django.utils import timezone as django_timezone
from datetime import timedelta


class ObservationViewSet(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer

    def perform_create(self, serializer):
        """
        Save observation and trigger evidence processing.
        
        Core logic:
        1. Save the observation
        2. If observation has trip_id, try to update corresponding ActiveTrip:
           - Update last_observed_at timestamp
           - Calculate delay_seconds (actual vs scheduled time)
           - Update confidence_score based on recent observation count
           - Update TripPosition if stop information available
        """
        observation = serializer.save()
        
        # Only process if observation is linked to a trip
        if not observation.trip:
            return
        
        try:
            # Get or create ActiveTrip for this trip
            active_trip, created = ActiveTrip.objects.get_or_create(
                trip=observation.trip,
                defaults={
                    'delay_seconds': 0,
                    'confidence_score': 0.0
                }
            )
            
            # Update timestamp
            active_trip.last_observed_at = django_timezone.now()
            
            # Calculate delay if we have stop information
            if observation.stop:
                delay = self._calculate_delay(observation)
                if delay is not None:
                    active_trip.delay_seconds = delay
            
            # Update confidence score based on recent observation count
            confidence = self._calculate_confidence(observation.trip)
            active_trip.confidence_score = confidence
            
            active_trip.save()
            
            # Update position if we have stop information
            if observation.stop:
                self._update_position(active_trip, observation)
                
        except Exception as e:
            # Log error but don't fail the observation save
            print(f"Error processing observation {observation.id}: {e}")
    
    def _calculate_delay(self, observation):
        """
        Calculate delay in seconds: actual_time - scheduled_time.
        
        Args:
            observation: Observation with trip and stop
            
        Returns:
            Delay in seconds (positive = late, negative = early), or None if can't calculate
        """
        try:
            # Find the scheduled time for this trip at this stop
            stop_time = observation.trip.stop_times.filter(stop=observation.stop).first()
            
            if not stop_time:
                return None  # Stop not in this trip's schedule
            
            # Get agency timezone
            agency = observation.trip.route.agency
            
            # Convert observation timestamp to service seconds
            service_date, actual_seconds = datetime_to_service_seconds(
                observation.timestamp,
                agency.timezone
            )
            
            # Calculate delay: actual - scheduled
            # Use arrival_seconds as the reference point
            delay = actual_seconds - stop_time.arrival_seconds
            
            return delay
            
        except Exception as e:
            print(f"Error calculating delay: {e}")
            return None
    
    def _calculate_confidence(self, trip):
        """
        Calculate confidence score based on recent observation count.
        
        Formula: min(1.0, num_recent_observations / 5.0)
        - 0 observations = 0.0
        - 5+ observations = 1.0
        
        Args:
            trip: Trip object
            
        Returns:
            Float between 0.0 and 1.0
        """
        # Count observations from the last 15 minutes
        cutoff_time = django_timezone.now() - timedelta(minutes=15)
        
        recent_count = Observation.objects.filter(
            trip=trip,
            timestamp__gte=cutoff_time
        ).count()
        
        # Score: 0.2 per observation, max 1.0
        confidence = min(1.0, recent_count / 5.0)
        
        return confidence
    
    def _update_position(self, active_trip, observation):
        """
        Update TripPosition based on observation location.
        
        Args:
            active_trip: ActiveTrip instance
            observation: Observation with stop information
        """
        try:
            # Get stop sequence for this stop
            stop_time = observation.trip.stop_times.filter(stop=observation.stop).first()
            
            if not stop_time:
                return
            
            # Get or create position record
            position, created = TripPosition.objects.get_or_create(
                trip=active_trip,
                defaults={
                    'last_stop_sequence': stop_time.stop_sequence,
                    'progress_ratio': 0.0
                }
            )
            
            # Update position
            position.last_stop_sequence = stop_time.stop_sequence
            # For MVP, set progress_ratio to 0.0 when at stop
            # Future: could interpolate based on time between stops
            position.progress_ratio = 0.0
            position.save()
            
        except Exception as e:
            print(f"Error updating position: {e}")

