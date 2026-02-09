from django.db import models
from gtfs.models import Trip

class ActiveTrip(models.Model):
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, related_name='active_trip')
    started_at = models.DateTimeField(auto_now_add=True)
    last_observed_at = models.DateTimeField(auto_now=True)
    delay_seconds = models.IntegerField(default=0)
    confidence_score = models.FloatField(default=0.0)

    def __str__(self):
        return f"Active: {self.trip_id} (Delay: {self.delay_seconds}s)"

class TripPosition(models.Model):
    trip = models.OneToOneField(ActiveTrip, on_delete=models.CASCADE, related_name='position')
    last_stop_sequence = models.IntegerField()
    progress_ratio = models.FloatField(default=0.0) # 0.0 to 1.0 between stops
    observed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.trip.trip_id} at seq {self.last_stop_sequence} + {self.progress_ratio:.2f}"

class TripDelayHistory(models.Model):
    """
    Stores aggregated delay data for trips on specific dates.
    Used for detecting patterns like "Route 100 is always +8 min late during rush hour".
    """
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='delay_history')
    date = models.DateField(help_text="Service date for this delay record")
    avg_delay_seconds = models.IntegerField(help_text="Average delay across all observations")
    num_observations = models.IntegerField(help_text="Number of observations used in average")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['trip', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['trip', 'date']),
        ]
        verbose_name_plural = "Trip Delay Histories"
    
    def __str__(self):
        return f"{self.trip_id} on {self.date}: {self.avg_delay_seconds}s avg ({self.num_observations} obs)"
