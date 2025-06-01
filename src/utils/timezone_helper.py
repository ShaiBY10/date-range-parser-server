from datetime import datetime, timedelta
import pytz

def get_timezone_offset(timezone):
    tz = pytz.timezone(timezone)
    return tz.utcoffset(datetime.now()).total_seconds() / 3600

def convert_to_timezone(dt, timezone):
    tz = pytz.timezone(timezone)
    return dt.astimezone(tz)