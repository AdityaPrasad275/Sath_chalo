#!/bin/bash
# Simple scheduler for running aggregate_delays daily at 4 AM
#
# TODO: For production, replace with Celery Beat or django-cron for more robust scheduling
# This is a lightweight solution for development/prototyping

echo "Scheduler started. Will run aggregate_delays daily at 4:00 AM (service timezone)"

while true; do
    # Get current time
    current_hour=$(date +%H)
    current_minute=$(date +%M)
    
    # Check if it's 4:00 AM (within 1-minute window)
    if [ "$current_hour" = "04" ] && [ "$current_minute" = "00" ]; then
        echo "[$(date)] Running aggregate_delays..."
        python manage.py aggregate_delays
        
        # Sleep for 2 minutes to avoid running multiple times
        sleep 120
    fi
    
    # Check every 60 seconds
    sleep 60
done
