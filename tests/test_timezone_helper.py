import pytest
from datetime import datetime, timedelta
from src.utils.timezone_helper import get_timezone_offset, convert_to_timezone

def test_get_timezone_offset():
    assert get_timezone_offset("UTC") == 0
    assert get_timezone_offset("America/New_York") == -5  # Adjust for daylight saving if necessary
    assert get_timezone_offset("Europe/London") == 0  # Adjust for daylight saving if necessary

def test_convert_to_timezone():
    dt_utc = datetime(2023, 10, 1, 12, 0, 0)  # UTC time
    dt_ny = convert_to_timezone(dt_utc, "America/New_York")
    assert dt_ny.hour == 8  # 12 PM UTC is 8 AM in New York (EST)

    dt_london = convert_to_timezone(dt_utc, "Europe/London")
    assert dt_london.hour == 12  # 12 PM UTC is 12 PM in London (BST)

    dt_ny_dst = datetime(2023, 6, 1, 12, 0, 0)  # UTC time during DST
    dt_ny_dst_converted = convert_to_timezone(dt_ny_dst, "America/New_York")
    assert dt_ny_dst_converted.hour == 8  # 12 PM UTC is 8 AM in New York (EDT) during DST

    dt_london_dst = datetime(2023, 6, 1, 12, 0, 0)  # UTC time during DST
    dt_london_dst_converted = convert_to_timezone(dt_london_dst, "Europe/London")
    assert dt_london_dst_converted.hour == 13  # 12 PM UTC is 1 PM in London (BST) during DST