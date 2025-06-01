import pytest
from src.parsers.date_range_parser import DateRangeParser
from datetime import datetime, timedelta
import pytz

@pytest.fixture
def date_range_parser():
    return DateRangeParser()

class TestBasicDurations:
    def test_simple_numbers(self, date_range_parser):
        commands = ["1 day", "2 days", "3 hours", "30 minutes", "45 seconds"]
        for command in commands:
            start, end = date_range_parser.parse_command(command, "UTC")
            assert start < end
            assert isinstance(start, datetime)
            assert isinstance(end, datetime)

    def test_word_numbers(self, date_range_parser):
        commands = ["one day", "two hours", "three minutes", "five seconds"]
        for command in commands:
            start, end = date_range_parser.parse_command(command, "UTC")
            assert start < end

    def test_fractional_numbers(self, date_range_parser):
        commands = ["half hour", "quarter day", "a week", "an hour"]
        for command in commands:
            start, end = date_range_parser.parse_command(command, "UTC")
            assert start < end

class TestRelativeExpressions:
    def test_last_expressions(self, date_range_parser):
        commands = ["last 3 hours", "past 2 days", "previous week", "last month"]
        for command in commands:
            start, end = date_range_parser.parse_command(command, "UTC")
            assert start < end

    def test_next_expressions(self, date_range_parser):
        commands = ["next 2 hours", "upcoming week", "following month"]
        for command in commands:
            start, end = date_range_parser.parse_command(command, "UTC")
            assert start < end

    def test_ago_expressions(self, date_range_parser):
        commands = ["3 hours ago", "2 days ago", "1 week ago"]
        for command in commands:
            start, end = date_range_parser.parse_command(command, "UTC")
            assert start < end

class TestNamedPeriods:
    def test_named_days(self, date_range_parser):
        commands = ["yesterday", "today", "tomorrow"]
        for command in commands:
            start, end = date_range_parser.parse_command(command, "UTC")
            assert isinstance(start, datetime)
            assert isinstance(end, datetime)

class TestCalendarPeriods:
    def test_week_periods(self, date_range_parser):
        commands = ["this week", "last week", "next week"]
        for command in commands:
            start, end = date_range_parser.parse_command(command, "UTC")
            assert start < end

    def test_month_periods(self, date_range_parser):
        commands = ["this month", "last month", "next month"]
        for command in commands:
            start, end = date_range_parser.parse_command(command, "UTC")
            assert start < end

    def test_year_periods(self, date_range_parser):
        commands = ["this year", "last year", "next year"]
        for command in commands:
            start, end = date_range_parser.parse_command(command, "UTC")
            assert start < end

class TestComplexExpressions:
    def test_various_units(self, date_range_parser):
        commands = [
            "15 mins", "2 hrs", "3 wks", "6 mos", "1 yr",
            "twenty minutes", "thirty seconds", "dozen hours"
        ]
        for command in commands:
            start, end = date_range_parser.parse_command(command, "UTC")
            assert start < end

    def test_since_expressions(self, date_range_parser):
        commands = ["since yesterday", "since last week"]
        for command in commands:
            start, end = date_range_parser.parse_command(command, "UTC")
            assert start < end

class TestTimezones:
    def test_different_timezones(self, date_range_parser):
        timezones = ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"]
        command = "last 24 hours"
        
        for tz in timezones:
            start, end = date_range_parser.parse_command(command, tz)
            assert start < end
            assert start.tzinfo is not None
            assert end.tzinfo is not None

class TestErrorHandling:
    def test_invalid_commands(self, date_range_parser):
        invalid_commands = ["invalid command", "xyz abc", ""]
        for command in invalid_commands:
            with pytest.raises(ValueError):
                date_range_parser.parse_command(command, "UTC")

    def test_invalid_timezone(self, date_range_parser):
        with pytest.raises(ValueError):
            date_range_parser.parse_command("1 day", "Invalid/Timezone")

class TestEdgeCases:
    def test_case_insensitive(self, date_range_parser):
        commands = ["LAST 3 HOURS", "Next Week", "YeStErDaY"]
        for command in commands:
            start, end = date_range_parser.parse_command(command, "UTC")
            assert start < end

    def test_extra_whitespace(self, date_range_parser):
        commands = ["  last   3   hours  ", "\tlast week\n", "  yesterday  "]
        for command in commands:
            start, end = date_range_parser.parse_command(command, "UTC")
            assert start < end

    def test_various_aliases(self, date_range_parser):
        commands = [
            "1 sec", "2 mins", "3 hrs", "4 wks", "5 mos", "6 yrs",
            "past 2 h", "last 3 d", "previous 4 w"
        ]
        for command in commands:
            start, end = date_range_parser.parse_command(command, "UTC")
            assert start < end