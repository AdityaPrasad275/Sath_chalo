"""
Management command to activate trips and manage ActiveTrip lifecycle.

This command:
1. Creates ActiveTrip records for trips starting in the next 15 minutes
2. Deletes ActiveTrip records for trips that ended more than 30 minutes ago

Designed to run as a cron job every 5 minutes.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone as django_timezone
from gtfs.models import Trip, StopTime, Agency
from gtfs.utils.time_helpers import get_current_service_time, seconds_to_actual_datetime
from realtime.models import ActiveTrip
import datetime


class Command(BaseCommand):
    help = 'Activate upcoming trips and clean up expired ActiveTrips'

    def add_arguments(self, parser):
        parser.add_argument(
            '--lookahead-minutes',
            type=int,
            default=15,
            help='Activate trips starting within this many minutes (default: 15)'
        )
        parser.add_argument(
            '--cleanup-minutes',
            type=int,
            default=30,
            help='Delete ActiveTrips for trips ended more than this many minutes ago (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        lookahead_minutes = options['lookahead_minutes']
        cleanup_minutes = options['cleanup_minutes']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        # Get agency (assuming single agency for MVP)
        try:
            agency = Agency.objects.first()
            if not agency:
                self.stdout.write(self.style.ERROR('No agency found. Run ingest_gtfs first.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fetching agency: {e}'))
            return

        # Get current service time
        service_date, current_seconds = get_current_service_time(agency.timezone)
        self.stdout.write(f'Current service day: {service_date}, time: {current_seconds // 3600:02d}:{(current_seconds % 3600) // 60:02d}:{current_seconds % 60:02d}')

        # 1. Activate upcoming trips
        activated_count = self._activate_upcoming_trips(
            agency, service_date, current_seconds, lookahead_minutes, dry_run
        )

        # 2. Clean up old trips
        cleaned_count = self._cleanup_old_trips(
            agency, service_date, current_seconds, cleanup_minutes, dry_run
        )

        # Summary
        self.stdout.write(self.style.SUCCESS(
            f'\nSummary: Activated {activated_count} trips, cleaned up {cleaned_count} trips'
        ))

    def _activate_upcoming_trips(self, agency, service_date, current_seconds, lookahead_minutes, dry_run):
        """Create ActiveTrip records for trips starting soon."""
        
        lookahead_seconds = lookahead_minutes * 60
        start_window = current_seconds
        end_window = current_seconds + lookahead_seconds

        self.stdout.write(f'\n--- Activating trips starting between {start_window}s and {end_window}s ---')

        # Find all trips with first stop in the activation window
        # We look at the first stop_time for each trip (stop_sequence=1 or min sequence)
        trips_to_activate = []
        
        for trip in Trip.objects.select_related('route').prefetch_related('stop_times'):
            # Get first stop time
            first_stop_time = trip.stop_times.order_by('stop_sequence').first()
            
            if not first_stop_time:
                continue  # No stops for this trip
            
            departure_seconds = first_stop_time.departure_seconds
            
            # Check if departure is within activation window
            if start_window <= departure_seconds <= end_window:
                # Check if already activated
                if not hasattr(trip, 'active_trip') or trip.active_trip is None:
                    trips_to_activate.append((trip, first_stop_time))

        self.stdout.write(f'Found {len(trips_to_activate)} trips to activate')

        activated_count = 0
        for trip, first_stop_time in trips_to_activate:
            if dry_run:
                self.stdout.write(f'  [DRY RUN] Would activate: {trip.trip_id} ({trip.route.short_name}) departing at {first_stop_time.departure_time_str}')
            else:
                try:
                    ActiveTrip.objects.create(
                        trip=trip,
                        delay_seconds=0,
                        confidence_score=0.0
                    )
                    activated_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ Activated: {trip.trip_id} ({trip.route.short_name}) departing at {first_stop_time.departure_time_str}'
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Failed to activate {trip.trip_id}: {e}'))

        return activated_count

    def _cleanup_old_trips(self, agency, service_date, current_seconds, cleanup_minutes, dry_run):
        """Delete ActiveTrip records for trips that have ended."""
        
        cleanup_threshold_seconds = current_seconds - (cleanup_minutes * 60)
        
        self.stdout.write(f'\n--- Cleaning up trips that ended before {cleanup_threshold_seconds}s ---')

        trips_to_cleanup = []
        
        for active_trip in ActiveTrip.objects.select_related('trip').prefetch_related('trip__stop_times'):
            # Get last stop time for this trip
            last_stop_time = active_trip.trip.stop_times.order_by('-stop_sequence').first()
            
            if not last_stop_time:
                continue
            
            arrival_seconds = last_stop_time.arrival_seconds
            
            # Check if trip has ended (including grace period)
            if arrival_seconds < cleanup_threshold_seconds:
                trips_to_cleanup.append((active_trip, last_stop_time))

        self.stdout.write(f'Found {len(trips_to_cleanup)} trips to clean up')

        cleaned_count = 0
        for active_trip, last_stop_time in trips_to_cleanup:
            if dry_run:
                self.stdout.write(f'  [DRY RUN] Would delete: {active_trip.trip.trip_id} (arrived at {last_stop_time.arrival_time_str})')
            else:
                try:
                    trip_id = active_trip.trip.trip_id
                    active_trip.delete()
                    cleaned_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ Cleaned up: {trip_id} (arrived at {last_stop_time.arrival_time_str})'
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Failed to delete {active_trip.trip.trip_id}: {e}'))

        return cleaned_count
