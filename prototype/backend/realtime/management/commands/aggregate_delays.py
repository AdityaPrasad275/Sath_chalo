"""
Management command to aggregate observations into daily delay history.

This command:
1. Processes observations from a specific date (default: yesterday)
2. Calculates average delay per trip
3. Stores results in TripDelayHistory for pattern analysis

Designed to run daily as a cron job.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone as django_timezone
from django.db.models import Avg, Count
from gtfs.models import Trip, Agency
from gtfs.utils.time_helpers import get_current_service_time, datetime_to_service_seconds
from evidence.models import Observation
from realtime.models import TripDelayHistory, ActiveTrip
import datetime


class Command(BaseCommand):
    help = 'Aggregate observations into daily delay history for pattern detection'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date to aggregate (YYYY-MM-DD format, default: yesterday)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be aggregated without saving'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Determine which date to aggregate
        if options['date']:
            target_date = datetime.datetime.strptime(options['date'], '%Y-%m-%d').date()
        else:
            target_date = (datetime.date.today() - datetime.timedelta(days=1))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        self.stdout.write(f'Aggregating observations for service date: {target_date}')
        
        # Get agency timezone
        try:
            agency = Agency.objects.first()
            if not agency:
                self.stdout.write(self.style.ERROR('No agency found. Run ingest_gtfs first.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fetching agency: {e}'))
            return
        
        # Find all observations from this date
        # Target date covers service day (3 AM to 3 AM next day)
        start_dt = datetime.datetime.combine(target_date, datetime.time(3, 0))
        end_dt = start_dt + datetime.timedelta(days=1)
        
        # Make timezone-aware
        import pytz
        tz = pytz.timezone(agency.timezone)
        start_dt = tz.localize(start_dt).astimezone(pytz.UTC)
        end_dt = tz.localize(end_dt).astimezone(pytz.UTC)
        
        observations = Observation.objects.filter(
            timestamp__gte=start_dt,
            timestamp__lt=end_dt,
            trip__isnull=False
        ).select_related('trip', 'stop')
        
        self.stdout.write(f'Found {observations.count()} observations between {start_dt} and {end_dt}')
        
        # Group observations by trip and calculate delays
        trip_delays = {}
        
        for obs in observations:
            # Calculate delay for this observation
            delay = self._calculate_delay(obs, agency)
            
            if delay is None:
                continue  # Skip if we can't calculate delay
            
            trip_id = obs.trip_id
            if trip_id not in trip_delays:
                trip_delays[trip_id] = []
            trip_delays[trip_id].append(delay)
        
        self.stdout.write(f'Calculated delays for {len(trip_delays)} trips\n')
        
        # Aggregate and save
        created_count = 0
        updated_count = 0
        
        for trip_id, delays in trip_delays.items():
            avg_delay = sum(delays) // len(delays)  # Integer average
            num_obs = len(delays)
            
            if dry_run:
                self.stdout.write(
                    f'  [DRY RUN] Trip {trip_id}: avg_delay={avg_delay}s ({num_obs} observations)'
                )
            else:
                trip = Trip.objects.get(trip_id=trip_id)
                tdh, created = TripDelayHistory.objects.update_or_create(
                    trip=trip,
                    date=target_date,
                    defaults={
                        'avg_delay_seconds': avg_delay,
                        'num_observations': num_obs
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ Created: {trip_id} - avg_delay={avg_delay}s ({num_obs} obs)'
                    ))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'  ↻ Updated: {trip_id} - avg_delay={avg_delay}s ({num_obs} obs)'
                    ))
        
        # Summary
        self.stdout.write(self.style.SUCCESS(
            f'\nSummary: Created {created_count}, Updated {updated_count} delay history records'
        ))
    
    def _calculate_delay(self, observation, agency):
        """
        Calculate delay for an observation.
        
        Returns delay in seconds, or None if can't calculate.
        """
        try:
            if not observation.stop:
                return None
            
            # Find scheduled time for this trip at this stop
            stop_time = observation.trip.stop_times.filter(stop=observation.stop).first()
            
            if not stop_time:
                return None
            
            # Convert observation timestamp to service seconds
            service_date, actual_seconds = datetime_to_service_seconds(
                observation.timestamp,
                agency.timezone
            )
            
            # Calculate delay
            delay = actual_seconds - stop_time.arrival_seconds
            
            return delay
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error calculating delay for observation {observation.id}: {e}'))
            return None
