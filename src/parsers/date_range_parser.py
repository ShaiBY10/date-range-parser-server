import re
import pytz
from datetime import datetime, timedelta
from dateutil import parser as dateutil_parser
from dateutil.relativedelta import relativedelta

class DateRangeParser:
    def __init__(self):
        # Time unit mappings with various aliases
        self.time_units = {
            # Seconds
            'second': 'seconds', 'seconds': 'seconds', 'sec': 'seconds', 'secs': 'seconds', 's': 'seconds',
            # Minutes
            'minute': 'minutes', 'minutes': 'minutes', 'min': 'minutes', 'mins': 'minutes', 'm': 'minutes',
            # Hours
            'hour': 'hours', 'hours': 'hours', 'hr': 'hours', 'hrs': 'hours', 'h': 'hours',
            # Days
            'day': 'days', 'days': 'days', 'd': 'days',
            # Weeks
            'week': 'weeks', 'weeks': 'weeks', 'wk': 'weeks', 'wks': 'weeks', 'w': 'weeks',
            # Months
            'month': 'months', 'months': 'months', 'mon': 'months', 'mons': 'months', 'mo': 'months',
            # Years
            'year': 'years', 'years': 'years', 'yr': 'years', 'yrs': 'years', 'y': 'years',
        }
        
        # Number word mappings
        self.number_words = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
            'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20,
            'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
            'eighty': 80, 'ninety': 90, 'hundred': 100, 'thousand': 1000,
            'a': 1, 'an': 1, 'half': 0.5, 'quarter': 0.25, 'dozen': 12
        }
        
        # Relative time keywords
        self.relative_keywords = {
            'last': -1, 'past': -1, 'previous': -1, 'ago': -1, 'before': -1,
            'next': 1, 'upcoming': 1, 'following': 1, 'forward': 1, 'ahead': 1,
            'this': 0, 'current': 0, 'today': 0, 'now': 0
        }

    def parse_command(self, command: str, timezone: str = 'UTC'):
        """
        Parse various date range commands and return start and end datetime objects.
        
        Examples of supported commands:
        - "1 day", "2 days", "last 3 hours", "past 5 minutes"
        - "a week", "half an hour", "quarter day"
        - "yesterday", "tomorrow", "today"
        - "this week", "last month", "next year"
        - "3 days ago", "in 2 hours"
        - "from 2023-01-01 to 2023-01-31"
        - "between yesterday and today"
        - "since last week"
        """
        try:
            # Get the current time in the specified timezone
            local_tz = pytz.timezone(timezone)
            now = datetime.now(local_tz)
            
            # Clean and normalize the command
            command = self._normalize_command(command.lower().strip())
            
            # Try different parsing strategies
            result = self._try_parse_strategies(command, now, local_tz)
            
            if result:
                return result
            else:
                raise ValueError(f"Unable to parse command: {command}")
                
        except Exception as e:
            raise ValueError(f"Error parsing command '{command}': {str(e)}")

    def _normalize_command(self, command):
        """Normalize the command by removing unnecessary words and standardizing format."""
        # Remove common filler words
        filler_words = ['the', 'for', 'of', 'in', 'at', 'on', 'from', 'to', 'and', 'or']
        words = command.split()
        words = [word for word in words if word not in filler_words or len(words) <= 2]
        
        # Handle contractions and common abbreviations
        command = ' '.join(words)
        command = re.sub(r"n't", " not", command)
        command = re.sub(r"'s", "", command)
        command = re.sub(r"'re", " are", command)
        
        return command

    def _try_parse_strategies(self, command, now, local_tz):
        """Try different parsing strategies in order of specificity."""
        
        # Strategy 1: Specific date ranges (from X to Y)
        result = self._parse_specific_date_range(command, now, local_tz)
        if result: return result
        
        # Strategy 2: Relative time expressions (last X, next X, X ago)
        result = self._parse_relative_time(command, now, local_tz)
        if result: return result
        
        # Strategy 3: Simple time duration (X days, X hours)
        result = self._parse_simple_duration(command, now, local_tz)
        if result: return result
        
        # Strategy 4: Named periods (yesterday, today, tomorrow)
        result = self._parse_named_periods(command, now, local_tz)
        if result: return result
        
        # Strategy 5: Calendar periods (this week, last month)
        result = self._parse_calendar_periods(command, now, local_tz)
        if result: return result
        
        # Strategy 6: Since/until expressions
        result = self._parse_since_until(command, now, local_tz)
        if result: return result
        
        return None

    def _parse_specific_date_range(self, command, now, local_tz):
        """Parse specific date ranges like 'from 2023-01-01 to 2023-01-31' or 'between X and Y'."""
        
        # Pattern for "from X to Y" or "between X and Y"
        patterns = [
            r'(?:from|between)\s+(.+?)\s+(?:to|and)\s+(.+)',
            r'(.+?)\s+(?:to|until|through)\s+(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                start_str, end_str = match.groups()
                try:
                    start_date = self._parse_flexible_date(start_str, now, local_tz)
                    end_date = self._parse_flexible_date(end_str, now, local_tz)
                    return start_date, end_date
                except:
                    continue
        
        return None

    def _parse_relative_time(self, command, now, local_tz):
        """Parse relative time expressions like 'last 3 hours', 'next week', '2 days ago'."""
        
        # Pattern for "last/past/next X Y" or "X Y ago/ahead"
        patterns = [
            r'(last|past|previous)\s+(\d+|\w+)\s+(\w+)',
            r'(next|upcoming|following)\s+(\d+|\w+)\s+(\w+)',
            r'(\d+|\w+)\s+(\w+)\s+(ago|before)',
            r'in\s+(\d+|\w+)\s+(\w+)',
            r'(\d+|\w+)\s+(\w+)\s+(ahead|forward)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                if len(match.groups()) == 3:
                    if match.group(3) in ['ago', 'before']:
                        # "X Y ago"
                        number_str, unit_str = match.group(1), match.group(2)
                        direction = -1
                    elif match.group(3) in ['ahead', 'forward']:
                        # "X Y ahead"
                        number_str, unit_str = match.group(1), match.group(2)
                        direction = 1
                    else:
                        # "last/next X Y"
                        direction_str, number_str, unit_str = match.groups()
                        direction = self.relative_keywords.get(direction_str, -1)
                elif len(match.groups()) == 2:
                    # "in X Y"
                    number_str, unit_str = match.groups()
                    direction = 1
                else:
                    continue
                
                try:
                    number = self._parse_number(number_str)
                    unit = self._normalize_time_unit(unit_str)
                    
                    if unit and number is not None:
                        delta = self._create_timedelta(number * direction, unit)
                        if direction < 0:
                            start_date = now + delta
                            end_date = now
                        else:
                            start_date = now
                            end_date = now + delta
                        return start_date, end_date
                except:
                    continue
        
        return None

    def _parse_simple_duration(self, command, now, local_tz):
        """Parse simple duration expressions like '3 days', 'half hour', 'a week'."""
        
        # Pattern for "number unit" or "a/an unit"
        patterns = [
            r'^(\d+(?:\.\d+)?)\s+(\w+)$',
            r'^(a|an|one|half|quarter)\s+(\w+)$',
            r'^(\w+)\s+(\w+)$',  # For written numbers
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                number_str, unit_str = match.groups()
                try:
                    number = self._parse_number(number_str)
                    unit = self._normalize_time_unit(unit_str)
                    
                    if unit and number is not None:
                        delta = self._create_timedelta(-number, unit)  # Default to past
                        start_date = now + delta
                        end_date = now
                        return start_date, end_date
                except:
                    continue
        
        return None

    def _parse_named_periods(self, command, now, local_tz):
        """Parse named periods like 'yesterday', 'today', 'tomorrow'."""
        
        if 'yesterday' in command:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999) - timedelta(days=1)
            return start_date, end_date
        
        elif 'today' in command or 'now' in command:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
            return start_date, end_date
        
        elif 'tomorrow' in command:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999) + timedelta(days=1)
            return start_date, end_date
        
        return None

    def _parse_calendar_periods(self, command, now, local_tz):
        """Parse calendar periods like 'this week', 'last month', 'next year'."""
        
        patterns = [
            r'(this|last|next|current|past|previous)\s+(week|month|year|quarter)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                direction_str, period = match.groups()
                direction = self.relative_keywords.get(direction_str, 0)
                
                try:
                    return self._get_calendar_period(now, period, direction)
                except:
                    continue
        
        return None

    def _parse_since_until(self, command, now, local_tz):
        """Parse since/until expressions like 'since yesterday', 'until tomorrow'."""
        
        patterns = [
            r'since\s+(.+)',
            r'until\s+(.+)',
            r'up\s+to\s+(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                date_str = match.group(1)
                try:
                    parsed_date = self._parse_flexible_date(date_str, now, local_tz)
                    if 'since' in command:
                        return parsed_date, now
                    else:  # until
                        return now, parsed_date
                except:
                    continue
        
        return None

    def _parse_number(self, number_str):
        """Parse various number representations including words and fractions."""
        
        # Try direct number conversion
        try:
            return float(number_str)
        except ValueError:
            pass
        
        # Try number words
        if number_str in self.number_words:
            return self.number_words[number_str]
        
        # Try compound number words (like "twenty one")
        words = number_str.split()
        if len(words) == 2 and all(word in self.number_words for word in words):
            return sum(self.number_words[word] for word in words)
        
        return None

    def _normalize_time_unit(self, unit_str):
        """Normalize time unit to standard form."""
        unit_str = unit_str.lower().rstrip('s')  # Remove plural 's'
        return self.time_units.get(unit_str)

    def _create_timedelta(self, amount, unit):
        """Create timedelta object based on amount and unit."""
        
        if unit == 'seconds':
            return timedelta(seconds=amount)
        elif unit == 'minutes':
            return timedelta(minutes=amount)
        elif unit == 'hours':
            return timedelta(hours=amount)
        elif unit == 'days':
            return timedelta(days=amount)
        elif unit == 'weeks':
            return timedelta(weeks=amount)
        elif unit == 'months':
            return relativedelta(months=int(amount))
        elif unit == 'years':
            return relativedelta(years=int(amount))
        else:
            raise ValueError(f"Unknown time unit: {unit}")

    def _get_calendar_period(self, now, period, direction):
        """Get start and end dates for calendar periods."""
        
        if period == 'week':
            # Get start of week (Monday)
            days_since_monday = now.weekday()
            start_of_week = now - timedelta(days=days_since_monday)
            start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if direction == 0:  # this week
                start_date = start_of_week
                end_date = now
            elif direction < 0:  # last week
                start_date = start_of_week - timedelta(weeks=1)
                end_date = start_of_week - timedelta(microseconds=1)
            else:  # next week
                start_date = start_of_week + timedelta(weeks=1)
                end_date = start_of_week + timedelta(weeks=2) - timedelta(microseconds=1)
            
            return start_date, end_date
        
        elif period == 'month':
            if direction == 0:  # this month
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now
            elif direction < 0:  # last month
                start_date = (now.replace(day=1) - relativedelta(months=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(day=1) - timedelta(microseconds=1)
            else:  # next month
                start_date = (now.replace(day=1) + relativedelta(months=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = (now.replace(day=1) + relativedelta(months=2)) - timedelta(microseconds=1)
            
            return start_date, end_date
        
        elif period == 'year':
            if direction == 0:  # this year
                start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now
            elif direction < 0:  # last year
                start_date = now.replace(year=now.year-1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(month=1, day=1) - timedelta(microseconds=1)
            else:  # next year
                start_date = now.replace(year=now.year+1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(year=now.year+2, month=1, day=1) - timedelta(microseconds=1)
            
            return start_date, end_date
        
        return None

    def _parse_flexible_date(self, date_str, now, local_tz):
        """Parse flexible date strings using dateutil and custom logic."""
        
        # Try dateutil parser first
        try:
            parsed = dateutil_parser.parse(date_str, default=now)
            if parsed.tzinfo is None:
                parsed = local_tz.localize(parsed)
            return parsed
        except:
            pass
        
        # Try our custom named period parsing
        if date_str in ['yesterday']:
            return now - timedelta(days=1)
        elif date_str in ['today', 'now']:
            return now
        elif date_str in ['tomorrow']:
            return now + timedelta(days=1)
        
        # Try relative parsing
        temp_result = self._parse_relative_time(date_str, now, local_tz)
        if temp_result:
            return temp_result[0]  # Return start date
        
        raise ValueError(f"Cannot parse date: {date_str}")