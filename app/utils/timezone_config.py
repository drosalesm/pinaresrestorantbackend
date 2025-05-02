import pytz
from datetime import datetime

# Set your local timezone here
LOCAL_TIMEZONE = pytz.timezone('America/Tegucigalpa')  # Adjust to your exact timezone

def get_current_local_time():
    """Return the current time in the local timezone"""
    return datetime.now(LOCAL_TIMEZONE)

# You can add these other useful timezone functions if needed
def utc_to_local(utc_dt):
    """Convert UTC datetime to local timezone"""
    return utc_dt.replace(tzinfo=pytz.UTC).astimezone(LOCAL_TIMEZONE)

def local_to_utc(local_dt):
    """Convert local datetime to UTC"""
    if local_dt.tzinfo is None:
        local_dt = LOCAL_TIMEZONE.localize(local_dt)
    return local_dt.astimezone(pytz.UTC)

def format_datetime(dt, format_str="%Y-%m-%d %H:%M:%S"):
    """Format a datetime object to string using the specified format"""
    return dt.strftime(format_str)