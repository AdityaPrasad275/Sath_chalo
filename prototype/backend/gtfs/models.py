from django.contrib.gis.db import models

class Agency(models.Model):
    agency_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    timezone = models.CharField(max_length=50, help_text="IANA timezone (e.g., 'Asia/Kolkata')")
    
    class Meta:
        verbose_name_plural = "Agencies"
    
    def __str__(self):
        return self.name

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
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='routes')

    def __str__(self):
        return f"{self.short_name} - {self.long_name}"

class Shape(models.Model):
    shape_id = models.CharField(max_length=255, primary_key=True)
    geometry = models.LineStringField(srid=4326)
    
    def __str__(self):
        return self.shape_id

class Trip(models.Model):
    trip_id = models.CharField(max_length=255, primary_key=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='trips')
    headed_to = models.CharField(max_length=255, null=True, blank=True)
    shape = models.ForeignKey(Shape, on_delete=models.SET_NULL, null=True, blank=True, related_name='trips')
    service_id = models.CharField(max_length=255)

    def __str__(self):
        return self.trip_id

class StopTime(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='stop_times')
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='stop_times')
    stop_sequence = models.IntegerField()
    
    # Seconds since service day start (supports times > 24:00:00)
    arrival_seconds = models.IntegerField(
        help_text="Seconds since 00:00:00 of service day (can exceed 86400 for late-night trips)"
    )
    departure_seconds = models.IntegerField(
        help_text="Seconds since 00:00:00 of service day"
    )

    class Meta:
        ordering = ['stop_sequence']
        constraints = [
            models.UniqueConstraint(fields=['trip', 'stop_sequence'], name='unique_trip_sequence')
        ]
    
    @property
    def arrival_time_str(self):
        """Convert arrival_seconds back to HH:MM:SS format (can be >24:00:00)"""
        if self.arrival_seconds is None:
            return None
        from gtfs.utils.time_helpers import seconds_to_gtfs_time
        return seconds_to_gtfs_time(self.arrival_seconds)
    
    @property
    def departure_time_str(self):
        """Convert departure_seconds back to HH:MM:SS format"""
        if self.departure_seconds is None:
            return None
        from gtfs.utils.time_helpers import seconds_to_gtfs_time
        return seconds_to_gtfs_time(self.departure_seconds)
    
    def __str__(self):
        return f"{self.trip_id} @ {self.stop_id} ({self.stop_sequence})"
