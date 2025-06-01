from flask import Flask, request, jsonify
from parsers.date_range_parser import DateRangeParser
from utils.timezone_helper import get_timezone_offset, convert_to_timezone
import pytz
from datetime import datetime, timedelta
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
date_range_parser = DateRangeParser()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200

@app.route('/parse-date-range', methods=['POST'])
def parse_date_range():
    """
    Parse date range commands and return start/end datetimes.
    
    Expected JSON payload:
    {
        "command": "last 3 hours",
        "timezone": "UTC"  // optional, defaults to UTC
    }
    
    Returns:
    {
        "start": "2023-01-01T00:00:00+00:00",
        "end": "2023-01-01T03:00:00+00:00",
        "command": "last 3 hours",
        "timezone": "UTC"
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        command = data.get('command')
        if not command:
            return jsonify({'error': 'Missing required field: command'}), 400
        
        timezone = data.get('timezone', 'UTC')
        
        # Validate timezone
        try:
            pytz.timezone(timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            return jsonify({'error': f'Invalid timezone: {timezone}'}), 400
        
        logger.info(f"Parsing command: '{command}' with timezone: {timezone}")
        
        # Parse the command
        start, end = date_range_parser.parse_command(command, timezone)
        
        response = {
            'start': start.isoformat(),
            'end': end.isoformat(),
            'command': command,
            'timezone': timezone,
            'duration_seconds': (end - start).total_seconds()
        }
        
        logger.info(f"Successfully parsed command. Duration: {response['duration_seconds']} seconds")
        return jsonify(response), 200
        
    except ValueError as e:
        logger.warning(f"Parsing error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/supported-formats', methods=['GET'])
def supported_formats():
    """Return examples of supported date range formats."""
    examples = {
        "simple_durations": [
            "1 day", "2 days", "3 hours", "30 minutes", "45 seconds",
            "half hour", "quarter day", "a week", "an hour"
        ],
        "relative_expressions": [
            "last 3 hours", "past 2 days", "previous week", "last month",
            "next 2 hours", "upcoming week", "following month",
            "3 hours ago", "2 days ago", "in 1 week"
        ],
        "named_periods": [
            "yesterday", "today", "tomorrow"
        ],
        "calendar_periods": [
            "this week", "last week", "next week",
            "this month", "last month", "next month",
            "this year", "last year", "next year"
        ],
        "since_until": [
            "since yesterday", "since last week", "until tomorrow"
        ],
        "word_numbers": [
            "one day", "two hours", "three minutes", "dozen hours",
            "twenty minutes", "thirty seconds"
        ],
        "abbreviations": [
            "1 sec", "2 mins", "3 hrs", "4 wks", "5 mos", "6 yrs"
        ]
    }
    
    return jsonify({
        'supported_formats': examples,
        'supported_timezones': 'All pytz timezones (e.g., UTC, America/New_York, Europe/London)',
        'note': 'Commands are case-insensitive and support various aliases'
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Date Range Parser Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)