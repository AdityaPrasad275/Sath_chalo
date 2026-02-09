"""
GTFS Time Handling Utilities

GTFS times can exceed 24:00:00 (e.g., "25:30:00" for 1:30 AM next day).
This module handles conversion between GTFS time format and actual datetimes.

GTFS Service Day Convention:
- Service day typically runs from 3 AM to 3 AM next day (not midnight to midnight)
- Times like "25:30:00" mean "1:30 AM on the next calendar day"
"""

import datetime
import pytz
from django.utils import timezone as django_timezone


def gtfs_time_to_seconds(time_str: str) -> int:
    """
    Convert GTFS time string to seconds since service day start.
    
    GTFS allows times > 24:00:00 for trips that continue past midnight.
    
    Args:
        time_str: Time in HH:MM:SS format (e.g., "08:30:00" or "25:30:00")
    
    Returns:
        Integer seconds since 00:00:00 of service day
    
    Examples:
        >>> gtfs_time_to_seconds("08:30:00")
        30600
        >>> gtfs_time_to_seconds("25:30:00")
        91800
        >>> gtfs_time_to_seconds("00:00:00")
        0
    """
    parts = time_str.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = int(parts[2])
    return hours * 3600 + minutes * 60 + seconds


def seconds_to_gtfs_time(seconds: int) -> str:
    """
    Convert seconds since service day start to GTFS time string.
    
    Args:
        seconds: Seconds since 00:00:00 of service day
    
    Returns:
        Time string in HH:MM:SS format (may exceed 24:00:00)
    
    Examples:
        >>> seconds_to_gtfs_time(30600)
        "08:30:00"
        >>> seconds_to_gtfs_time(91800)
        "25:30:00"
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def get_current_service_time(agency_timezone_str: str) -> tuple:
    """
    Get current "service day" date and time in seconds.
    
    GTFS service day convention: Service day changes at 3 AM (not midnight).
    This means:
    - 2:59 AM on Feb 10 is still part of "Feb 9 service day" at second 97140
    - 3:00 AM on Feb 10 is start of "Feb 10 service day" at second 10800
    
    Args:
        agency_timezone_str: IANA timezone identifier (e.g., "Asia/Kolkata")
    
    Returns:
        Tuple of (service_date, seconds_since_service_start)
        - service_date: datetime.date of the service day
        - seconds_since_service_start: int seconds since 00:00:00 of service day
    
    Examples:
        At 2:30 AM on Feb 10, 2024 in Asia/Kolkata:
        >>> get_current_service_time("Asia/Kolkata")
        (datetime.date(2024, 2, 9), 95400)  # Still Feb 9 service day
        
        At 8:30 AM on Feb 10, 2024 in Asia/Kolkata:
        >>> get_current_service_time("Asia/Kolkata")
        (datetime.date(2024, 2, 10), 30600)  # Feb 10 service day
    """
    tz = pytz.timezone(agency_timezone_str)
    now = django_timezone.now().astimezone(tz)
    
    # If before 3 AM, we're still in yesterday's service day
    if now.hour < 3:
        service_date = (now - datetime.timedelta(days=1)).date()
        # Seconds = 24 hours (from yesterday) + current time
        seconds = 86400 + now.hour * 3600 + now.minute * 60 + now.second
    else:
        service_date = now.date()
        seconds = now.hour * 3600 + now.minute * 60 + now.second
    
    return service_date, seconds


def seconds_to_actual_datetime(
    service_date: datetime.date, 
    seconds: int, 
    agency_timezone_str: str
) -> datetime.datetime:
    """
    Convert GTFS service day + seconds to actual datetime with timezone.
    
    This handles the conversion from GTFS's abstract "service day time" 
    to a real-world timestamp.
    
    Args:
        service_date: The service day (e.g., 2024-01-15)
        seconds: Seconds since 00:00:00 of service day (can exceed 86400)
        agency_timezone_str: IANA timezone identifier
    
    Returns:
        Timezone-aware datetime object
    
    Examples:
        >>> seconds_to_actual_datetime(
        ...     datetime.date(2024, 1, 15), 
        ...     91800,  # 25:30:00
        ...     "Asia/Kolkata"
        ... )
        datetime.datetime(2024, 1, 16, 1, 30, 0, tzinfo=<DstTzInfo 'Asia/Kolkata' IST+5:30:00 STD>)
        
        >>> seconds_to_actual_datetime(
        ...     datetime.date(2024, 1, 15),
        ...     30600,  # 08:30:00
        ...     "Asia/Kolkata"
        ... )
        datetime.datetime(2024, 1, 15, 8, 30, 0, tzinfo=<DstTzInfo 'Asia/Kolkata' IST+5:30:00 STD>)
    """
    tz = pytz.timezone(agency_timezone_str)
    
    # Start with midnight of service date
    base_dt = datetime.datetime.combine(service_date, datetime.time(0, 0, 0))
    localized_dt = tz.localize(base_dt)
    
    # Add the seconds (this handles overflow to next day automatically)
    result_dt = localized_dt + datetime.timedelta(seconds=seconds)
    return result_dt


def datetime_to_service_seconds(
    dt: datetime.datetime,
    agency_timezone_str: str
) -> tuple:
    """
    Convert a datetime to service day + seconds format.
    
    Useful for converting observations or realtime data into GTFS-compatible format.
    
    Args:
        dt: Timezone-aware datetime
        agency_timezone_str: IANA timezone identifier
    
    Returns:
        Tuple of (service_date, seconds_since_service_start)
    """
    tz = pytz.timezone(agency_timezone_str)
    local_dt = dt.astimezone(tz)
    
    # Determine service day
    if local_dt.hour < 3:
        service_date = (local_dt - datetime.timedelta(days=1)).date()
        seconds = 86400 + local_dt.hour * 3600 + local_dt.minute * 60 + local_dt.second
    else:
        service_date = local_dt.date()
        seconds = local_dt.hour * 3600 + local_dt.minute * 60 + local_dt.second
    
    return service_date, seconds
