from django.contrib.gis.db import models
from gtfs.models import Stop, Trip

class Observation(models.Model):
    class ObservationType(models.TextChoices):
        # Existing types
        WAITING_AT_STOP = 'WAITING', 'Waiting at Stop'
        ON_BUS = 'ON_BUS', 'On Bus'
        BUS_PASSED = 'PASSED', 'Bus Passed'
        
        # New types for comprehensive feedback
        BUS_ARRIVED = 'ARRIVED', 'Bus Arrived'
        BUS_DIDNT_COME = 'NO_SHOW', "Bus Didn't Come"
        BUS_REROUTED = 'REROUTED', 'Bus Rerouted'
        BUS_BREAKDOWN = 'BREAKDOWN', 'Bus Breakdown'
        STILL_ON_BUS = 'HEARTBEAT', 'Still on Bus (Heartbeat)'

    user_id = models.CharField(max_length=255)  # Anonymous session ID or user ID
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20, choices=ObservationType.choices)
    
    # Links to GTFS entities
    stop = models.ForeignKey(Stop, on_delete=models.SET_NULL, null=True, blank=True, 
                            help_text="Stop where observation was made")
    trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, null=True, blank=True,
                            help_text="Trip this observation is about (if known)")
    
    # Geolocation (for implicit matching or route deviation detection)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    
    # Additional metadata
    notes = models.TextField(blank=True, help_text="Optional user notes or details")

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['trip', 'timestamp']),
            models.Index(fields=['stop', 'timestamp']),
            models.Index(fields=['user_id', 'timestamp']),
        ]

    def __str__(self):
        trip_info = f"trip {self.trip_id}" if self.trip_id else "no trip"
        return f"{self.type} by {self.user_id} at {self.timestamp} ({trip_info})"

