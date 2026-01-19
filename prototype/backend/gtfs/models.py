from django.contrib.gis.db import models

class Stop(models.Model):
    stop_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    geom = models.PointField(srid=4326)
    
    def __str__(self):
        return f"{self.name} ({self.stop_id})"

class Route(models.Model):
    route_id = models.CharField(max_length=255, primary_key=True)
    short_name = models.CharField(max_length=50)
    long_name = models.CharField(max_length=255)
    agency_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.short_name} - {self.long_name}"

class Trip(models.Model):
    trip_id = models.CharField(max_length=255, primary_key=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='trips')
    direction_id = models.IntegerField(null=True, blank=True)
    shape_id = models.CharField(max_length=255, null=True, blank=True)
    service_id = models.CharField(max_length=255)

    def __str__(self):
        return self.trip_id

class StopTime(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='stop_times')
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='stop_times')
    stop_sequence = models.IntegerField()
    arrival_time = models.TimeField()
    departure_time = models.TimeField()

    class Meta:
        ordering = ['stop_sequence']
        constraints = [
            models.UniqueConstraint(fields=['trip', 'stop_sequence'], name='unique_trip_sequence')
        ]
    
    def __str__(self):
        return f"{self.trip_id} @ {self.stop_id} ({self.stop_sequence})"
