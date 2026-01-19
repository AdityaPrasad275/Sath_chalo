from django.contrib.gis.db import models
from gtfs.models import Stop

class Observation(models.Model):
    class ObservationType(models.TextChoices):
        WAITING_AT_STOP = 'WAITING', 'Waiting at Stop'
        ON_BUS = 'ON_BUS', 'On Bus'
        BUS_PASSED = 'PASSED', 'Bus Passed'

    user_id = models.CharField(max_length=255) # Anonymous session ID or user ID
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20, choices=ObservationType.choices)
    stop = models.ForeignKey(Stop, on_delete=models.SET_NULL, null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.type} by {self.user_id} at {self.timestamp}"
