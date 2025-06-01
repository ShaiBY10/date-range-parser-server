# Date Range Parser Server

This project is a Flask-based server that parses various date range commands and converts them into datetime ranges based on the specified timezone.

## Features

- Parses commands like "1 day" or "last 3 hours" to generate datetime ranges.
- Supports timezone conversion for accurate date range calculations.

## Project Structure

```
date-range-parser-server
├── src
│   ├── app.py                # Entry point of the application
│   ├── parsers               # Module for parsing date range commands
│   │   ├── __init__.py       # Empty initializer for parsers module
│   │   └── date_range_parser.py # Contains DateRangeParser class
│   ├── utils                 # Utility functions
│   │   ├── __init__.py       # Empty initializer for utils module
│   │   └── timezone_helper.py # Functions for timezone handling
│   └── models                # Data models
│       ├── __init__.py       # Empty initializer for models module
│       └── date_range.py      # DateRange class representing a date range
├── tests                     # Unit tests for the application
│   ├── __init__.py           # Empty initializer for tests module
│   ├── test_date_parser.py    # Tests for DateRangeParser
│   └── test_timezone_helper.py # Tests for timezone helper functions
├── requirements.txt          # Project dependencies
├── Dockerfile                # Docker image instructions
├── docker-compose.yml        # Docker Compose configuration
├── .env.example              # Example environment variables
└── README.md                 # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd date-range-parser-server
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/app.py
   ```

## Usage

Send a POST request to the server with a date range command in the body. For example:
```json
{
  "command": "last 3 hours"
}
```

The server will respond with the corresponding datetime range based on the specified timezone.

## License

This project is licensed under the MIT License.